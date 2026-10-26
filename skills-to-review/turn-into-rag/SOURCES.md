# Source handling

Find the warning or situation below and apply its fix. If the fix produces a new file, stage that file, adding `--force` if a ledger already exists.

## Scanned PDF

Warning: "N of M pages have no text layer". Those pages hold a placeholder instead of text.

- **OCR available** (`ocrmypdf --version` works; it needs Tesseract): run `ocrmypdf --skip-text -l eng+spa in.pdf out.pdf` with the source's languages, then stage `out.pdf`.
- **No OCR, few pages flagged**: run `python <skill-dir>/scripts/render_pages.py <pdf> <physical pages> --out knowledge/<slug>/_raw/pages`. Read each image and type its text into the raw section in place of the placeholder before distilling.
- **No OCR, most of the document scanned**: stop and tell the user. Reading hundreds of page images is slow and costly. Suggest installing Tesseract and ocrmypdf, or providing a PDF that has text.

## Figures, charts and image tables

Text extraction can't see them. When a raw section points to a figure or table that carries data ("see Table 4.2") and the data isn't in the extracted text, render that page and transcribe the data:
`python <skill-dir>/scripts/render_pages.py <pdf> 95 --labels --out knowledge/<slug>/_raw/pages` (`--labels` takes the printed page number the locator cites).

## Password-protected PDF

Ask the user for an unlocked copy.

## Thin web page

Warning: "Only N words extracted", or the fetch failed (403, timeout).

- **JS-rendered page, cookie wall or bot block**: ask the user to save the page (browser → Save as "Webpage, complete", or Print → PDF) and stage the file. If a browser-automation tool is available, it can save the rendered HTML instead.
- **Paywalled article or paper**: look for an open copy (arXiv, PubMed Central, the author's site) or ask the user for the file.
- Don't distill from a web-fetch tool that returns a model-written summary of the page. Distillation needs the full text.

## Video and audio

- **Video URL staged as a web page** (site not recognized as a video host): re-run with `--as media`.
- **No captions**: stage.py downloads the audio and transcribes it with Whisper (needs `requirements-media.txt`). Pass `--lang` when auto-detection picks the wrong language.
- **Transcript errors**: auto-captions and Whisper mishear names, numbers and jargon ("photopuria" for photoperiod). Correct them from context, the frames or the video description. When you can't be sure, keep the term and add `> Note: transcription uncertain`.
- **Accuracy vs speed**: `--whisper-model base` is faster; `medium` or `large-v3` are more accurate and practical on a GPU. If the machine has an NVIDIA GPU but no CUDA libraries, the script falls back to CPU by itself.
- **yt-dlp errors** (HTTP 403, "Sign in to confirm", format unavailable): sites change often, so run `pip install -U yt-dlp` and retry. If it still fails, ask the user for the downloaded file or a transcript.
- **Visual content in an online video**: download the video first with `yt-dlp -f "best[ext=mp4]" -o video.mp4 "<url>"`, then stage the file with `--frames 30`.
- **Playlists and courses**: stage each video as its own source. INDEX.md lists them all.

## Formats stage.py doesn't take

- **Legacy .doc, .ppt, .rtf, .odt, Pages, Keynote**: convert to .docx or .pdf (`soffice --headless --convert-to docx <file>` if LibreOffice is installed), or ask the user to re-save the file.
- **DRM ebooks** (Kindle .azw/.kfx, protected EPUB): don't try to remove the DRM. Ask the user for a DRM-free copy, such as the publisher's PDF or EPUB.
- **Images** (photographed pages, infographics, diagrams): skip staging. View them directly and write the single-file layout. For many photographed pages, merge them into one PDF and treat it as scanned.
- **Cloud links** (Google Drive, OneDrive, Dropbox, Notion): download or export the file through the available connector, or ask the user for it, then stage the local copy.
- **A book split across files** (one PDF per chapter): merge them first with `python -c "import pymupdf,sys; d=pymupdf.open(); [d.insert_pdf(pymupdf.open(f)) for f in sys.argv[2:]]; d.save(sys.argv[1])" book.pdf ch01.pdf ch02.pdf`, then stage `book.pdf`.
