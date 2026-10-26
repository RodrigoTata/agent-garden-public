#!/usr/bin/env python3
"""
turn-into-rag: stage.py
Convert one source (file or URL) into raw, locator-marked Markdown, split into
ledger rows small enough to distill one at a time.

Usage:
  python stage.py <path-or-url> [--kb knowledge] [--slug SLUG] [--title TITLE] [--as auto|web|media]
                  [--lang CODE] [--whisper-model small] [--frames SECONDS]
                  [--max-words 9000] [--force]
  python stage.py --check

Writes <kb>/<slug>/ledger.md and <kb>/<slug>/_raw/{source.md, meta.json, sections/, frames/}.
Supported: PDF, DOCX, PPTX, XLSX, EPUB, HTML, MD/TXT, web pages, online video
(YouTube and other yt-dlp sites), local audio/video (mp3, wav, m4a, mp4, mkv...).
"""

import argparse
import hashlib
import html
import json
import math
import re
import shutil
import sys
import unicodedata
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() not in ("utf-8", "utf8"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
AUDIO_EXT = {".mp3", ".wav", ".m4a", ".aac", ".ogg", ".oga", ".opus", ".flac", ".wma"}
VIDEO_EXT = {".mp4", ".mkv", ".mov", ".webm", ".avi", ".m4v", ".wmv", ".mpeg", ".mpg"}
MARKITDOWN_EXT = {".docx", ".pptx", ".xlsx", ".xls", ".epub"}
HTML_EXT = {".html", ".htm", ".xhtml", ".mhtml"}
TEXT_EXT = {".md", ".markdown", ".txt", ".rst"}
MEDIA_HOSTS = ("youtube.com", "youtu.be", "vimeo.com", "dailymotion.com", "twitch.tv",
               "tiktok.com", "soundcloud.com", "rumble.com", "bilibili.com", "ted.com")
TRANSCRIPT_SPAN = 60  # seconds of speech per transcript paragraph


class StageError(Exception):
    pass


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Unit:
    """Smallest splittable piece of the source: a paragraph or a transcript minute."""
    loc: str   # page label ("12"), timestamp ("00:12:34") or "" for unpaginated text
    text: str


@dataclass
class Staged:
    kind: str
    title: str
    loc_style: str                                  # page | time | none
    units: list = field(default_factory=list)
    outline: list = field(default_factory=list)     # (level, title, unit_index)
    meta: dict = field(default_factory=dict)
    warnings: list = field(default_factory=list)
    frames: list = field(default_factory=list)      # (seconds, relative path)
    unlocated: set = field(default_factory=set)     # unit indexes where a TOC heading wasn't found


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def slugify(text: str, limit: int = 60) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode()
    text = re.sub(r"[^a-zA-Z0-9]+", "-", text).strip("-").lower()
    return text[:limit].rstrip("-") or "source"


def norm(text: str) -> str:
    text = unicodedata.normalize("NFKD", text).encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9]", "", text)


def hhmmss(seconds: float) -> str:
    s = int(seconds)
    return f"{s // 3600:02d}:{s % 3600 // 60:02d}:{s % 60:02d}"


def words(text: str) -> int:
    return len(text.split())


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(1 << 16), b""):
            h.update(block)
    return h.hexdigest()


def looks_generated(title: str) -> bool:
    t = title.strip().lower()
    return (not t or len(t) < 3 or t.startswith(("microsoft word", "untitled", "document"))
            or t.endswith((".doc", ".docx", ".pdf", ".indd", ".qxd")))


def markdown_units(md: str):
    """Split Markdown into paragraph units; ATX headings become outline entries."""
    units, outline, buf, in_fence = [], [], [], False

    def flush():
        if buf and "\n".join(buf).strip():
            units.append(Unit("", "\n".join(buf).strip()))
        buf.clear()

    for line in md.splitlines():
        if line.lstrip().startswith(("```", "~~~")):
            in_fence = not in_fence
            buf.append(line)
            continue
        m = None if in_fence else re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", line)
        if m:
            flush()
            title = re.sub(r"[*_`]", "", m.group(2)).strip()
            outline.append((len(m.group(1)), title, len(units)))
            units.append(Unit("", line.strip()))
        elif not line.strip() and not in_fence:
            flush()
        else:
            buf.append(line)
    flush()
    return units, outline


def fetch(url: str, timeout: int = 60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read(), resp.headers.get("Content-Type", "").lower(), resp.geturl()


def decode_html(data: bytes, ctype: str) -> str:
    m = re.search(r"charset=([\w-]+)", ctype) or re.search(rb'charset=["\']?([\w-]+)', data[:4000])
    enc = m.group(1) if m else "utf-8"
    enc = enc.decode() if isinstance(enc, bytes) else enc
    try:
        return data.decode(enc, errors="replace")
    except LookupError:
        return data.decode("utf-8", errors="replace")


# ---------------------------------------------------------------------------
# Extractors
# ---------------------------------------------------------------------------

def extract_pdf(path: Path) -> Staged:
    try:
        import pymupdf
    except ImportError:
        raise StageError("pymupdf missing - pip install -r requirements.txt")
    doc = pymupdf.open(path)
    if doc.needs_pass:
        raise StageError("PDF is password-protected. Ask the user for an unlocked copy.")

    texts = None
    try:
        import pymupdf4llm
        try:
            chunks = pymupdf4llm.to_markdown(doc, page_chunks=True, show_progress=False)
        except TypeError:
            chunks = pymupdf4llm.to_markdown(doc, page_chunks=True)
        if isinstance(chunks, list) and len(chunks) == doc.page_count:
            texts = [c.get("text", "") if isinstance(c, dict) else str(c) for c in chunks]
    except Exception as exc:  # layout engine failures must not block plain extraction
        log(f"pymupdf4llm failed ({exc.__class__.__name__}); falling back to plain text.")
    if texts is None:
        texts = [page.get_text() for page in doc]

    # Units are paragraphs tagged with their printed page label, so a section that
    # starts mid-page splits there instead of duplicating the shared page.
    st = Staged(kind="pdf", title="", loc_style="page")
    scanned, page_first = [], []
    for i, page in enumerate(doc):
        label = page.get_label() or str(i + 1)
        page_first.append(len(st.units))
        text = texts[i].strip()
        if len(text) < 25 and page.get_images():
            scanned.append(i + 1)
            text = (f"[scanned page - no text layer. Render physical page {i + 1} "
                    f"with render_pages.py and read the image]")
        st.units += [Unit(label, p.strip()) for p in re.split(r"\n\s*\n", text) if p.strip()]
    page_first.append(len(st.units))

    for level, title, page_no in doc.get_toc(simple=True):
        if not (st.units and 1 <= page_no <= doc.page_count and title.strip()):
            continue
        # look for the heading paragraph on its page or the next (TOCs are often off by one)
        lo, hi, key = page_first[page_no - 1], page_first[min(page_no + 1, doc.page_count)], norm(title)[:40]
        idx = next((j for j in range(lo, hi)
                    if key and words(st.units[j].text) <= 20 and key in norm(st.units[j].text)), None)
        if idx is None:
            idx = lo
            st.unlocated.add(min(lo, len(st.units) - 1))
        st.outline.append((level, title.strip(), min(idx, len(st.units) - 1)))
    if not st.outline:  # no bookmarks: fall back to the headings pymupdf4llm inferred from font sizes
        for j, u in enumerate(st.units):
            m = re.match(r"^(#{1,6})\s+(.+)", u.text)
            if m and words(u.text) <= 20:
                st.outline.append((len(m.group(1)), re.sub(r"[*_`]", "", m.group(2)).strip(), j))

    md = doc.metadata or {}
    st.title = md.get("title", "") if not looks_generated(md.get("title", "")) else ""
    if not st.title:  # first top-level heading on the first two pages, e.g. a paper's title
        st.title = next((re.sub(r"[*_`#]", "", u.text).strip() for u in st.units[:page_first[min(2, doc.page_count)]]
                         if re.match(r"^#\s", u.text)), "")
    st.meta = {"authors": md.get("author", ""), "date": md.get("creationDate", "")[2:10],
               "pages": doc.page_count, "has_toc": bool(st.outline)}
    if scanned:
        share = len(scanned) / doc.page_count
        st.warnings.append(f"{len(scanned)} of {doc.page_count} pages have no text layer "
                           f"(scanned){' - the whole document needs OCR' if share > 0.3 else ''}. "
                           f"See SOURCES.md > Scanned PDF.")
        st.meta["scanned_pages"] = scanned
    doc.close()  # Windows keeps the file locked while open
    return st


def extract_markitdown(path: Path) -> Staged:
    try:
        from markitdown import MarkItDown
    except ImportError:
        raise StageError("markitdown missing - pip install -r requirements.txt")
    result = MarkItDown(enable_plugins=False).convert(str(path))
    md = getattr(result, "markdown", None) or result.text_content or ""
    st = Staged(kind=path.suffix.lower().lstrip("."), title=(result.title or "").strip(), loc_style="none")
    st.units, st.outline = markdown_units(md)
    if path.suffix.lower() == ".pptx":
        st.meta["note"] = "slide numbers appear as <!-- Slide number: N --> comments; cite as (slide N)"
    return st


def keep_math(raw_html: str) -> str:
    """Replace MathML with its LaTeX alttext as visible text. Extractors otherwise drop
    equations silently, and sites like Wikipedia keep MathML inside display:none wrappers."""
    if "<math" not in raw_html:
        return raw_html
    try:
        import lxml.html
        tree = lxml.html.fromstring(raw_html)
    except Exception:
        return raw_html
    for m in tree.xpath("//*[local-name()='math'][@alttext]"):
        alt = re.sub(r"^\{\\displaystyle\s*(.*)\}$", r"\1", m.get("alttext").strip(), flags=re.S).strip()
        anchor = m
        for anc in m.iterancestors():
            style = (anc.get("style") or "").replace(" ", "").lower()
            if "display:none" in style or anc.get("hidden") is not None or anc.get("aria-hidden") == "true":
                anchor = anc
        span = lxml.html.Element("span")
        span.text = f" ${alt}$ "
        anchor.addprevious(span)
        if anchor is m:
            m.drop_tree()
    return lxml.html.tostring(tree, encoding="unicode")


def extract_html(raw_html: str, url: str = "") -> Staged:
    st = Staged(kind="web" if url else "html", title="", loc_style="none")
    raw_html = keep_math(raw_html)
    md = None
    try:
        import trafilatura
        md = trafilatura.extract(raw_html, url=url or None, output_format="markdown",
                                 include_tables=True, include_formatting=True,
                                 include_links=False, include_images=False,
                                 include_comments=False, favor_recall=True)
        meta = trafilatura.extract_metadata(raw_html, default_url=url or None)
        if meta:
            st.title = meta.title or ""
            st.meta = {"authors": meta.author or "", "date": meta.date or "",
                       "site": meta.sitename or ""}
    except ImportError:
        pass
    if not md:
        try:
            from markitdown import MarkItDown
            import io
            result = MarkItDown(enable_plugins=False).convert_stream(
                io.BytesIO(raw_html.encode("utf-8")), file_extension=".html")
            md = getattr(result, "markdown", None) or result.text_content or ""
            st.title = st.title or (result.title or "")
        except ImportError:
            raise StageError("trafilatura and markitdown both missing - pip install -r requirements.txt")
    st.units, st.outline = markdown_units(md or "")
    total = sum(words(u.text) for u in st.units)
    if total < 200:
        st.warnings.append(f"Only {total} words extracted - the page may be JS-rendered, paywalled "
                           f"or blocking bots. See SOURCES.md > Thin web page.")
    return st


def extract_text(path: Path) -> Staged:
    md = path.read_text(encoding="utf-8", errors="replace")
    st = Staged(kind="text", title="", loc_style="none")
    st.units, st.outline = markdown_units(md)
    return st


def transcript_units(segments):
    """Group (start_seconds, text) segments into ~1-minute paragraphs."""
    units, start, buf = [], None, []
    for t, text in segments:
        if start is None:
            start = t
        if t - start >= TRANSCRIPT_SPAN and buf:
            units.append(Unit(hhmmss(start), " ".join(buf)))
            start, buf = t, []
        buf.append(text)
    if buf:
        units.append(Unit(hhmmss(start), " ".join(buf)))
    return units


def parse_vtt(vtt: str):
    """WebVTT to (start_seconds, line) pairs, dropping the rolling repeats of auto-captions."""
    out, recent = [], []
    timing = re.compile(r"(?:(\d+):)?(\d{2}):(\d{2})[.,](\d{3})\s+-->")
    for block in re.split(r"\n\s*\n", vtt.replace("\r", "")):
        lines = block.strip().split("\n")
        idx = next((i for i, l in enumerate(lines) if timing.search(l)), None)
        if idx is None:
            continue
        h, m, s, ms = timing.search(lines[idx]).groups()
        start = int(h or 0) * 3600 + int(m) * 60 + int(s) + int(ms) / 1000
        for line in lines[idx + 1:]:
            line = html.unescape(re.sub(r"<[^>]+>", "", line)).strip()
            if not line or line in recent:
                continue
            out.append((start, line))
            recent = (recent + [line])[-4:]
    return out


def load_audio(path: Path, rate: int = 16000):
    """Decode any audio/video file to 16 kHz mono float32 (own decoder: faster-whisper's
    built-in one breaks on newer PyAV releases)."""
    import av
    import numpy as np
    chunks = []
    with av.open(str(path)) as container:
        if not container.streams.audio:
            raise StageError(f"{path.name} has no audio track.")
        resampler = av.AudioResampler(format="s16", layout="mono", rate=rate)
        for frame in container.decode(container.streams.audio[0]):
            chunks += [f.to_ndarray() for f in resampler.resample(frame)]
        chunks += [f.to_ndarray() for f in resampler.resample(None)]
    if not chunks:
        raise StageError(f"No audio could be decoded from {path.name}.")
    return np.concatenate(chunks, axis=1).flatten().astype(np.float32) / 32768.0


def transcribe(path: Path, lang, model_name: str):
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise StageError("faster-whisper missing - pip install -r requirements-media.txt")
    audio = load_audio(path)

    def run(device, compute_type):
        log(f"Loading Whisper model '{model_name}' on {device} (first run downloads it)...")
        model = WhisperModel(model_name, device=device, compute_type=compute_type)
        segments, info = model.transcribe(audio, language=lang, vad_filter=True)
        log(f"Transcribing {hhmmss(info.duration)} of audio, language '{info.language}'...")
        out, next_report = [], 300
        for seg in segments:
            out.append((seg.start, seg.text.strip()))
            if seg.start >= next_report:
                log(f"  {hhmmss(seg.start)} / {hhmmss(info.duration)}")
                next_report += 300
        return out, info.language, info.duration

    try:
        return run("auto", "auto")
    except RuntimeError as exc:  # GPU present but CUDA/cuDNN libraries missing
        if not re.search(r"cuda|cublas|cudnn", str(exc), re.I):
            raise
        log(f"GPU unusable ({exc}); falling back to CPU.")
        return run("cpu", "int8")


def extract_frames(path: Path, out_dir: Path, every: float, threshold: float = 5.0):
    """Sample one frame every `every` seconds, skipping near-duplicates of the last kept frame."""
    try:
        import av
        from PIL import ImageChops, ImageStat
    except ImportError:
        raise StageError("av/Pillow missing - pip install -r requirements-media.txt")
    out_dir.mkdir(parents=True, exist_ok=True)
    kept, prev = [], None
    with av.open(str(path)) as container:
        if not container.streams.video:
            return kept
        stream = container.streams.video[0]
        duration = float(container.duration / 1_000_000) if container.duration else 0.0
        t = 0.0
        while t <= duration:
            container.seek(int(t / stream.time_base), stream=stream, backward=True, any_frame=False)
            frame = next((f for f in container.decode(stream) if f.time is not None and f.time >= t - 0.05), None)
            if frame is None:
                break
            img = frame.to_image()
            thumb = img.convert("RGB").resize((96, 54))
            if prev is None or sum(ImageStat.Stat(ImageChops.difference(thumb, prev)).mean) / 3 >= threshold:
                img.thumbnail((1280, 1280))
                name = f"f-{hhmmss(frame.time).replace(':', '')}.jpg"
                img.save(out_dir / name, quality=80)
                kept.append((frame.time, f"_raw/frames/{name}"))
                prev = thumb
            t += every
    return kept


def pick_subtitle(info: dict, lang):
    for source, auto in ((info.get("subtitles") or {}, False), (info.get("automatic_captions") or {}, True)):
        keys = [k for k in source if k != "live_chat"]
        if not keys:
            continue
        # auto-captions list ~100 machine translations; the spoken language carries "-orig"
        orig = [k for k in keys if k.endswith("-orig")]
        prefs = [p for p in (lang, info.get("language")) if p] or ([] if orig else ["en", "es"])
        chosen = next((k for p in prefs for k in orig + keys if k == p or k.startswith(p + "-")), None)
        if chosen is None:
            chosen = orig[0] if orig else (None if auto else keys[0])
        if chosen:
            vtt = next((e for e in source[chosen] if e.get("ext") == "vtt"), None)
            if vtt:
                return chosen, vtt["url"], auto
    return None


def extract_media_url(url: str, raw_dir: Path, lang, model_name: str) -> Staged:
    try:
        import yt_dlp
    except ImportError:
        raise StageError("yt-dlp missing - pip install -r requirements-media.txt")
    opts = {"quiet": True, "no_warnings": True, "noplaylist": True, "skip_download": True}
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
    except Exception as exc:
        raise StageError(f"yt-dlp could not read the URL ({exc}). See SOURCES.md > yt-dlp errors.")

    st = Staged(kind="video" if info.get("vcodec") not in (None, "none") else "audio",
                title=info.get("title") or "", loc_style="time")
    st.meta = {"authors": info.get("uploader") or info.get("channel") or "",
               "date": info.get("upload_date") or "", "duration": hhmmss(info.get("duration") or 0),
               "url": info.get("webpage_url") or url}
    track = pick_subtitle(info, lang)
    if track:
        key, sub_url, auto = track
        data, ctype, _ = fetch(sub_url)
        segments = parse_vtt(decode_html(data, ctype))
        st.meta["transcript"] = f"{'auto' if auto else 'manual'} captions ({key})"
        if auto:
            st.warnings.append("Transcript comes from auto-captions: names, numbers and technical "
                               "terms may be misheard. See SOURCES.md > Transcript errors.")
    else:
        log("No captions found - downloading audio for transcription...")
        dl = {"quiet": True, "no_warnings": True, "noplaylist": True,
              "format": "bestaudio[ext=m4a]/bestaudio/best",
              "outtmpl": str(raw_dir / "audio.%(ext)s")}
        with yt_dlp.YoutubeDL(dl) as ydl:
            ydl.download([url])
        audio = next(raw_dir.glob("audio.*"), None)
        if audio is None:
            raise StageError("Audio download failed. See SOURCES.md > yt-dlp errors.")
        segments, detected, _ = transcribe(audio, lang, model_name)
        st.meta["transcript"] = f"whisper {model_name} ({detected})"
        audio.unlink()
    st.units = transcript_units(segments)
    starts = [hms_to_seconds(u.loc) for u in st.units]
    for ch in info.get("chapters") or []:
        idx = max([i for i, s in enumerate(starts) if s <= ch.get("start_time", 0) + 1] or [0])
        st.outline.append((1, ch.get("title") or "Chapter", idx))
    return st


def hms_to_seconds(loc: str) -> int:
    h, m, s = (int(x) for x in loc.split(":"))
    return h * 3600 + m * 60 + s


def extract_media_file(path: Path, raw_dir: Path, lang, model_name: str, frames_every) -> Staged:
    st = Staged(kind="video" if path.suffix.lower() in VIDEO_EXT else "audio",
                title="", loc_style="time")
    segments, detected, duration = transcribe(path, lang, model_name)
    st.units = transcript_units(segments)
    st.meta = {"duration": hhmmss(duration), "transcript": f"whisper {model_name} ({detected})"}
    if frames_every and st.kind == "video":
        log(f"Extracting frames every {frames_every}s...")
        st.frames = extract_frames(path, raw_dir / "frames", frames_every)
        st.meta["frames"] = len(st.frames)
    if not st.units:
        st.warnings.append("Transcription produced no speech. The file may be music-only or silent.")
    return st


# ---------------------------------------------------------------------------
# Dispatch
# ---------------------------------------------------------------------------

def stage_source(source: str, raw_dir: Path, args) -> Staged:
    is_url = re.match(r"^https?://", source, re.I) is not None
    if is_url:
        host = urllib.parse.urlparse(source).netloc.lower()
        as_media = args.as_ == "media" or (args.as_ == "auto" and any(host.endswith(h) for h in MEDIA_HOSTS))
        if as_media:
            st = extract_media_url(source, raw_dir, args.lang, args.whisper_model)
        else:
            try:
                data, ctype, final = fetch(source)
            except Exception as exc:
                raise StageError(f"Could not fetch {source} ({exc}). See SOURCES.md > Thin web page.")
            ext = Path(urllib.parse.urlparse(final).path).suffix.lower()
            if "pdf" in ctype or ext == ".pdf":
                ext = ".pdf"
            elif "audio/" in ctype or "video/" in ctype:
                ext = ext if ext in AUDIO_EXT | VIDEO_EXT else (".mp4" if "video/" in ctype else ".mp3")
            if ext in {".pdf"} | MARKITDOWN_EXT | AUDIO_EXT | VIDEO_EXT:
                local = raw_dir / f"download{ext}"
                local.write_bytes(data)
                st = stage_file(local, raw_dir, args)
                try:
                    local.unlink()
                except OSError:
                    pass  # stays in _raw/, which is deleted at the end anyway
            else:
                st = extract_html(decode_html(data, ctype), final)
        st.meta.setdefault("url", source)
        st.meta["origin"] = source
        st.title = st.title or Path(urllib.parse.urlparse(source).path).stem.replace("-", " ") or host
        return st

    path = Path(source).expanduser().resolve()
    if not path.is_file():
        raise StageError(f"File not found: {path}")
    st = stage_file(path, raw_dir, args)
    st.meta["origin"] = str(path)
    st.meta["sha256"] = sha256_file(path)
    st.title = st.title or path.stem.replace("_", " ").replace("-", " ").strip()
    return st


def stage_file(path: Path, raw_dir: Path, args) -> Staged:
    ext = path.suffix.lower()
    if ext == ".pdf":
        return extract_pdf(path)
    if ext in MARKITDOWN_EXT:
        return extract_markitdown(path)
    if ext in HTML_EXT:
        return extract_html(path.read_text(encoding="utf-8", errors="replace"))
    if ext in TEXT_EXT:
        return extract_text(path)
    if ext in AUDIO_EXT | VIDEO_EXT:
        return extract_media_file(path, raw_dir, args.lang, args.whisper_model, args.frames)
    if ext in {".doc", ".ppt", ".pages", ".key", ".odt", ".rtf"}:
        raise StageError(f"{ext} is not supported directly. See SOURCES.md > Legacy formats.")
    if ext in {".azw", ".azw3", ".mobi", ".kfx"}:
        raise StageError(f"{ext} ebooks are usually DRM-protected. See SOURCES.md > DRM ebooks.")
    raise StageError(f"Unsupported file type: {ext}")


# ---------------------------------------------------------------------------
# Sectioning
# ---------------------------------------------------------------------------

@dataclass
class Section:
    crumbs: list
    a: int          # first unit (inclusive)
    b: int          # last unit (exclusive)
    notes: list = field(default_factory=list)


def build_sections(st: Staged, max_words: int):
    units, outline = st.units, sorted(st.outline, key=lambda e: (e[2], e[0]))
    n = len(units)
    prefix = [0]
    for u in units:
        prefix.append(prefix[-1] + words(u.text))

    def wsum(a, b):
        return prefix[b] - prefix[a]

    out = []

    def size_split(a, b, crumbs):
        total = wsum(a, b)
        parts = max(1, math.ceil(total / max_words))
        target = total / parts
        start, acc, chunks = a, 0, []
        for i in range(a, b):
            acc += words(units[i].text)
            if acc >= target and len(chunks) < parts - 1 and i + 1 < b:
                chunks.append((start, i + 1))
                start, acc = i + 1, 0
        chunks.append((start, b))
        for k, (x, y) in enumerate(chunks, 1):
            suffix = [f"part {k}/{len(chunks)}"] if len(chunks) > 1 else []
            out.append(Section(crumbs + suffix, x, y))

    def split(a, b, parent_level, crumbs):
        inside = [e for e in outline if a <= e[2] < b and e[0] > parent_level]
        if wsum(a, b) <= max_words or not inside:
            if wsum(a, b) > max_words:
                size_split(a, b, crumbs)
            elif wsum(a, b) > 0:
                out.append(Section(crumbs, a, b))
            return
        level = min(e[0] for e in inside)
        children = [e for e in inside if e[0] == level]
        first = children[0][2]
        if first > a:
            if wsum(a, first) >= 80:
                label = crumbs + ["(intro)"] if crumbs else ["Front matter"]
                split(a, first, level, label)
            else:
                children[0] = (children[0][0], children[0][1], a)
        for i, (_, title, idx) in enumerate(children):
            end = children[i + 1][2] if i + 1 < len(children) else b
            if end > idx:
                split(idx, end, level, crumbs + [title])

    split(0, n, 0, [])

    for i, sec in enumerate(out):
        if i > 0 and sec.a in st.unlocated:
            sec.notes.append(f"Heading not found in the text, so this row starts at the top of p. "
                             f"{units[sec.a].loc}; the first paragraphs may belong to the previous row.")
    return out


def locator(st: Staged, sec: Section, duration: str = "") -> str:
    first, last = st.units[sec.a], st.units[sec.b - 1]
    if st.loc_style == "page":
        return f"p. {first.loc}" if first.loc == last.loc else f"pp. {first.loc}-{last.loc}"
    if st.loc_style == "time":
        end = st.units[sec.b].loc if sec.b < len(st.units) else (duration or last.loc)
        return f"[{first.loc}]-[{end}]"
    return "§ " + (" › ".join(sec.crumbs) if sec.crumbs else "whole document")


def render_units(st: Staged, units) -> str:
    """Join units, marking each page change as [[p. N]] and each transcript paragraph as [hh:mm:ss]."""
    out, page = [], None
    for u in units:
        if st.loc_style == "page" and u.loc != page:
            out.append(f"[[p. {u.loc}]]")
            page = u.loc
        out.append(f"[{u.loc}] {u.text}" if st.loc_style == "time" else u.text)
    return "\n\n".join(out)


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_outputs(st: Staged, sections, src_dir: Path, raw_dir: Path, kb: Path, slug: str, max_words: int):
    sec_dir = raw_dir / "sections"
    sec_dir.mkdir(parents=True, exist_ok=True)
    rows = []
    for i, sec in enumerate(sections, 1):
        title = " › ".join(sec.crumbs) or st.title
        loc = locator(st, sec, st.meta.get("duration", ""))
        body = render_units(st, st.units[sec.a:sec.b])
        wc = sum(words(u.text) for u in st.units[sec.a:sec.b])
        lo = hms_to_seconds(st.units[sec.a].loc) if st.loc_style == "time" else None
        hi = hms_to_seconds(st.units[sec.b].loc) if st.loc_style == "time" and sec.b < len(st.units) else math.inf
        frames = [(t, p) for t, p in st.frames if lo is not None and lo <= t < hi]
        name = f"{i:02d}-{slugify(sec.crumbs[-1] if sec.crumbs else st.title, 40)}.md"
        head = [f"# {i:02d} · {title}", "",
                f"Source: {st.title} · Locator: {loc} · Raw words: {wc}"]
        head += [f"NOTE: {n}" for n in sec.notes]
        if frames:
            head.append("Frames to view while distilling: " +
                        ", ".join(f"{p} [{hhmmss(t)}]" for t, p in frames))
        (sec_dir / name).write_text("\n".join(head) + "\n\n---\n\n" + body + "\n", encoding="utf-8")
        rows.append({"n": i, "file": f"_raw/sections/{name}", "title": title, "locator": loc,
                     "raw_words": wc, "frames": len(frames)})

    total = sum(r["raw_words"] for r in rows)
    layout = (f"single file -> {kb.as_posix()}/{slug}.md" if len(rows) == 1
              else f"folder -> {src_dir.as_posix()}/ ({len(rows)} rows)")
    lines = [f"# Ledger — {st.title}", "",
             f"Source: {st.meta.get('origin', '')}  ",
             f"Kind: {st.kind} · Layout: {layout} · Staged: {date.today().isoformat()}  ",
             f"Raw total: {total} words · Max words per row: {max_words}", "",
             "| # | Section | Locator | Raw words | Distilled words | Status |",
             "|---|---------|---------|-----------|-----------------|--------|"]
    for r in rows:
        cell = r["title"].replace("|", "\\|")
        lines.append(f"| {r['n']:02d} | {cell} | {r['locator']} | {r['raw_words']} |  | todo |")
    (src_dir / "ledger.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    full = f"# {st.title} (raw)\n\nOrigin: {st.meta.get('origin', '')}\n\n" + render_units(st, st.units)
    (raw_dir / "source.md").write_text(full + "\n", encoding="utf-8")

    meta = {"title": st.title, "slug": slug, "kind": st.kind, "loc_style": st.loc_style,
            "staged": date.today().isoformat(), **st.meta, "warnings": st.warnings,
            "outline": [{"level": l, "title": t, "unit": u} for l, t, u in st.outline],
            "rows": rows}
    (raw_dir / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
    return rows, total, layout


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def check() -> int:
    backends = [
        ("pymupdf", "PDF", "requirements.txt"),
        ("pymupdf4llm", "PDF tables/headings (optional)", "requirements.txt"),
        ("markitdown", "DOCX, PPTX, XLSX, EPUB", "requirements.txt"),
        ("trafilatura", "web pages, HTML", "requirements.txt"),
        ("yaml", "chunk export (optional)", "requirements.txt"),
        ("yt_dlp", "online video/audio URLs", "requirements-media.txt"),
        ("faster_whisper", "transcription of audio/video", "requirements-media.txt"),
        ("av", "audio decoding, video frames", "requirements-media.txt"),
        ("PIL", "video frames", "requirements-media.txt"),
    ]
    import importlib.util
    for mod, serves, req in backends:
        ok = importlib.util.find_spec(mod) is not None
        print(f"{'OK     ' if ok else 'MISSING'}  {mod:<15} {serves:<34} ({req})")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description="Stage a source for distillation into RAG knowledge files.")
    p.add_argument("source", nargs="?", help="file path or URL")
    p.add_argument("--kb", default="knowledge", help="knowledge base folder (default: knowledge)")
    p.add_argument("--title", help="override the title read from the source metadata")
    p.add_argument("--slug", help="folder name for this source (default: derived from the title)")
    p.add_argument("--as", dest="as_", choices=["auto", "web", "media"], default="auto",
                   help="treat a URL as a web page or as media (default: auto by host)")
    p.add_argument("--lang", help="language code for captions/transcription (e.g. en, es)")
    p.add_argument("--whisper-model", default="small", help="faster-whisper model (default: small)")
    p.add_argument("--frames", type=float, help="local video: keep a deduplicated frame every N seconds")
    p.add_argument("--max-words", type=int, default=9000, help="max raw words per ledger row")
    p.add_argument("--force", action="store_true", help="overwrite a ledger that already has progress")
    p.add_argument("--check", action="store_true", help="report which extraction backends are installed")
    args = p.parse_args()

    if args.check:
        return check()
    if not args.source:
        p.error("source is required (or use --check)")

    kb = Path(args.kb)
    tmp_raw = kb / ".staging-tmp"
    if tmp_raw.exists():
        shutil.rmtree(tmp_raw)
    tmp_raw.mkdir(parents=True)
    try:
        st = stage_source(args.source, tmp_raw, args)
        st.title = args.title or st.title
        if not st.units or not any(u.text.strip() for u in st.units):
            raise StageError("No text could be extracted from the source.")
        slug = args.slug or slugify(st.title)
        src_dir = kb / slug
        ledger = src_dir / "ledger.md"
        if ledger.exists() and not args.force and re.search(r"\|\s*(done|skipped)", ledger.read_text(encoding="utf-8")):
            raise StageError(f"{ledger} already has distilled rows. Resume from it, or pass --force to restart.")
        raw_dir = src_dir / "_raw"
        if raw_dir.exists():
            shutil.rmtree(raw_dir)
        src_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(tmp_raw), str(raw_dir))
        sections = build_sections(st, args.max_words)
        if len(sections) > 1 and not st.outline:
            st.warnings.append("Source has no TOC/headings - rows were split by size, not by chapter. "
                               "Name each distilled file after the topics it actually covers.")
        rows, total, layout = write_outputs(st, sections, src_dir, raw_dir, kb, slug, args.max_words)
    except StageError as exc:
        shutil.rmtree(tmp_raw, ignore_errors=True)
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False, indent=2))
        return 1

    print(json.dumps({"ok": True, "title": st.title, "kind": st.kind, "dir": src_dir.as_posix(),
                      "ledger": ledger.as_posix(), "rows": len(rows), "raw_words": total,
                      "layout": layout, "warnings": st.warnings}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
