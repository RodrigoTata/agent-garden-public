# Design System — generate-html-doc (Dual-Theme Engine)

This file contains the **complete CSS design system with Dual-Theme support (Dark Glassmorphic + Light Paper + Print Safe)** for the `generate-html-doc` skill.  
Copy the entire CSS block below into the `<style>` tag of the target HTML file.  
Replace `VAR_PRIMARY` and `VAR_PRIMARY_DARK` with the chosen colors before writing the file.

---

## CSS Block

```css
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;600;700&display=swap');

* { margin: 0; padding: 0; box-sizing: border-box; }

:root {
    --bg-page: #070b14;
    --bg-doc: rgba(13, 20, 36, 0.94);
    --border-doc: rgba(51, 65, 85, 0.65);
    --doc-shadow: 0 14px 45px rgba(0, 0, 0, 0.7);
    --text-title: #ffffff;
    --text-subtitle: #34d399;
    --text-body: #cbd5e1;
    --text-muted: #94a3b8;
    --card-bg: rgba(18, 28, 51, 0.75);
    --card-border: rgba(51, 65, 85, 0.6);
    --meta-bg: rgba(15, 23, 42, 0.85);
    --meta-border: rgba(51, 65, 85, 0.6);
    --table-th: VAR_PRIMARY_DARK;
    --table-border: rgba(51, 65, 85, 0.5);
    --table-row: rgba(15, 23, 42, 0.6);
    --table-row-alt: rgba(24, 34, 58, 0.5);
    --table-hover: rgba(51, 65, 85, 0.4);
    --step-bg: rgba(15, 23, 42, 0.75);
    --step-border: rgba(51, 65, 85, 0.6);
    --callout-bg: rgba(16, 185, 129, 0.1);
    --callout-border: VAR_PRIMARY;
    --callout-warn-bg: rgba(245, 158, 11, 0.1);
    --callout-warn-border: #f59e0b;
    --primary: VAR_PRIMARY;
    --primary-dark: VAR_PRIMARY_DARK;
    --divider: rgba(51, 65, 85, 0.6);
}

body.theme-light {
    --bg-page: #f1f5f9;
    --bg-doc: #ffffff;
    --border-doc: #e2e8f0;
    --doc-shadow: 0 4px 25px rgba(0, 0, 0, 0.08);
    --text-title: #0f172a;
    --text-subtitle: VAR_PRIMARY;
    --text-body: #334155;
    --text-muted: #64748b;
    --card-bg: #f8fafc;
    --card-border: #e2e8f0;
    --meta-bg: #f8fafc;
    --meta-border: #e2e8f0;
    --table-th: VAR_PRIMARY_DARK;
    --table-border: #e2e8f0;
    --table-row: #ffffff;
    --table-row-alt: #f8fafc;
    --table-hover: #f1f5f9;
    --step-bg: #f8fafc;
    --step-border: #e2e8f0;
    --callout-bg: #f0fdf4;
    --callout-border: VAR_PRIMARY;
    --callout-warn-bg: #fffbeb;
    --callout-warn-border: #f59e0b;
    --primary: VAR_PRIMARY;
    --primary-dark: VAR_PRIMARY_DARK;
    --divider: #e2e8f0;
}

@page {
    size: A4 portrait;
    margin: 1.2cm;
}

@media print {
    body, body.theme-light {
        background: white !important;
        color: #000000 !important;
        -webkit-print-color-adjust: exact;
        print-color-adjust: exact;
    }
    .page-break { page-break-before: always; }
    .no-print { display: none !important; }
    .document {
        background: white !important;
        border: none !important;
        box-shadow: none !important;
        padding: 0 !important;
        margin: 0 !important;
        max-width: 100% !important;
    }
    .card, .flow-step, .doc-meta {
        background: #fafafa !important;
        border: 1px solid #e0e0e0 !important;
        color: #111 !important;
    }
    p, li, td, .flow-step-desc { color: #222 !important; }
    h1, h2, h3, h4, strong, .flow-step-title { color: #000 !important; }
    th { background: VAR_PRIMARY_DARK !important; color: white !important; }
    .flow-step { break-inside: avoid; }
    .card { break-inside: avoid; }
    tr { break-inside: avoid; }
}

body {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    background: var(--bg-page);
    color: var(--text-body);
    line-height: 1.6;
    font-size: 13px;
    transition: background-color 0.25s ease, color 0.25s ease;
}

/* --- Top Navigation Bar (Consistent Interconnected Suite Header) --- */
.top-bar {
    background: var(--bg-doc);
    backdrop-filter: blur(14px);
    border-bottom: 1px solid var(--border-doc);
    padding: 14px 28px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    position: sticky;
    top: 0;
    z-index: 50;
    width: 100%;
    box-shadow: 0 4px 20px rgba(0,0,0,0.15);
}
.brand {
    display: flex;
    align-items: center;
    gap: 12px;
}
.brand-icon {
    width: 36px; height: 36px;
    border-radius: 10px;
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    display: flex; align-items: center; justify-content: center;
    font-size: 18px;
    box-shadow: 0 4px 14px rgba(16, 185, 129, 0.35);
}
.brand-title {
    font-size: 15px; font-weight: 800; color: var(--text-title); letter-spacing: -0.3px;
}
.brand-subtitle {
    font-size: 11.5px; color: var(--text-muted);
}

.top-actions {
    display: flex; align-items: center; gap: 10px;
}
.btn-action {
    background: var(--card-bg);
    border: 1px solid var(--card-border);
    color: var(--text-body);
    font-size: 12px; font-weight: 600;
    padding: 7px 14px;
    border-radius: 9px;
    text-decoration: none;
    display: inline-flex; align-items: center; gap: 6px;
    transition: all 0.2s ease;
    cursor: pointer;
}
.btn-action:hover {
    background: var(--table-hover);
    border-color: #64748b;
    transform: translateY(-1px);
    color: var(--text-title);
}
.btn-action.primary {
    background: var(--primary); color: #070b14;
    border-color: var(--primary); font-weight: 700;
    box-shadow: 0 0 14px rgba(16, 185, 129, 0.4);
}
.btn-action.theme-toggle {
    background: rgba(245, 158, 11, 0.15);
    color: #f59e0b;
    border-color: rgba(245, 158, 11, 0.4);
    font-weight: 700;
}
.btn-action.theme-toggle:hover {
    background: rgba(245, 158, 11, 0.3);
    color: #fff;
}

@media (max-width: 1024px) {
    .top-bar { padding: 12px 16px; flex-direction: column; gap: 10px; align-items: flex-start; }
    .top-actions { width: 100%; justify-content: flex-start; flex-wrap: wrap; }
}

/* --- Document Shell (A4 Layout) --- */
.document {
    max-width: 210mm;
    margin: 30px auto;
    background: var(--bg-doc);
    backdrop-filter: blur(14px);
    border: 1px solid var(--border-doc);
    padding: 44px 40px;
    box-shadow: var(--doc-shadow);
    border-radius: 12px;
    transition: all 0.25s ease;
}

/* --- Header --- */
.doc-header {
    border-bottom: 3px solid var(--primary);
    padding-bottom: 18px;
    margin-bottom: 22px;
}
.doc-header-top {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 8px;
}
.doc-code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    font-weight: 700;
    color: var(--primary);
    background: rgba(16, 185, 129, 0.15);
    padding: 3px 8px;
    border-radius: 4px;
    border: 1px solid rgba(16, 185, 129, 0.3);
}
.doc-header h1 {
    font-size: 22px;
    font-weight: 900;
    color: var(--text-title);
    line-height: 1.25;
    margin-bottom: 4px;
    letter-spacing: -0.4px;
}
.doc-header .subtitle {
    font-size: 13px;
    color: var(--text-subtitle);
    font-weight: 700;
    margin-bottom: 14px;
}
.doc-meta {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 6px;
    font-size: 11.5px;
    color: var(--text-muted);
    background: var(--meta-bg);
    padding: 10px 14px;
    border-radius: 6px;
    border: 1px solid var(--meta-border);
}
.doc-meta span { display: block; }
.doc-meta strong { color: var(--text-title); }

/* --- Headings --- */
h2 {
    font-size: 16px;
    font-weight: 800;
    color: var(--text-title);
    margin-top: 26px;
    margin-bottom: 12px;
    padding-bottom: 5px;
    border-bottom: 2px solid var(--divider);
    display: flex;
    align-items: center;
    gap: 8px;
    letter-spacing: -0.2px;
}
h3 {
    font-size: 14px;
    font-weight: 700;
    color: var(--primary);
    margin-top: 18px;
    margin-bottom: 8px;
}

p { margin-bottom: 8px; color: var(--text-body); }
ul, ol { padding-left: 18px; margin-bottom: 8px; color: var(--text-body); }
li { margin-bottom: 3px; }

/* --- Tables --- */
.table-container {
    overflow-x: auto;
    margin: 14px 0;
    border-radius: 8px;
    border: 1px solid var(--table-border);
}
table {
    width: 100%;
    border-collapse: collapse;
    font-size: 11px;
}
th {
    background: var(--table-th);
    color: white;
    padding: 8px 10px;
    font-weight: 700;
    font-size: 10.5px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    border: 1px solid var(--table-th);
    text-align: left;
}
td {
    padding: 7px 10px;
    border: 1px solid var(--table-border);
    text-align: left;
    color: var(--text-body);
    background: var(--table-row);
}
td:first-child { font-weight: 600; color: var(--text-title); }
tr:nth-child(even) td { background: var(--table-row-alt); }
tr:hover td { background: var(--table-hover); }

.highlight-cell {
    background: rgba(16, 185, 129, 0.18) !important;
    font-weight: 700;
    color: #34d399 !important;
}

/* --- Callout Boxes --- */
.callout {
    background: var(--callout-bg);
    border-left: 4px solid var(--callout-border);
    padding: 10px 14px;
    margin: 12px 0;
    border-radius: 0 6px 6px 0;
    font-size: 12px;
    color: var(--text-body);
}
.callout.warning {
    background: var(--callout-warn-bg);
    border-left-color: var(--callout-warn-border);
}
.callout.danger {
    background: rgba(239, 68, 68, 0.12);
    border-left-color: #ef4444;
}
.callout strong {
    display: block;
    margin-bottom: 3px;
    color: var(--text-title);
    font-weight: 700;
}

/* --- Flowchart Steps --- */
.flowchart-container {
    margin: 16px 0;
    display: flex;
    flex-direction: column;
    gap: 10px;
}
.flow-step {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    background: var(--step-bg);
    border: 1px solid var(--step-border);
    border-left: 4px solid var(--primary);
    border-radius: 8px;
    padding: 12px 14px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.15);
}
.flow-step.warning {
    border-left-color: #f59e0b;
    background: rgba(245, 158, 11, 0.08);
}
.flow-step-number {
    width: 26px;
    height: 26px;
    border-radius: 50%;
    background: var(--primary);
    color: #070b14;
    font-weight: 800;
    font-size: 12px;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 1px;
}
.flow-step.warning .flow-step-number { background: #f59e0b; color: #070b14; }
.flow-step-body { flex: 1; }
.flow-step-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 4px;
}
.flow-step-title {
    font-weight: 800;
    font-size: 13px;
    color: var(--text-title);
}
.flow-step-desc {
    font-size: 12px;
    color: var(--text-muted);
    line-height: 1.5;
}
.flow-step-specs {
    margin-top: 6px;
    padding-top: 6px;
    border-top: 1px dashed var(--divider);
    font-family: 'JetBrains Mono', monospace;
    font-size: 11px;
    color: var(--text-subtitle);
}

/* --- Grid Cards --- */
.grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 12px;
    margin: 12px 0;
}
.grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 10px;
    margin: 12px 0;
}
.card {
    border: 1px solid var(--card-border);
    border-radius: 8px;
    padding: 12px;
    background: var(--card-bg);
}
.card h4 {
    font-size: 12.5px;
    font-weight: 700;
    color: var(--primary);
    margin-bottom: 4px;
}
.card p { font-size: 11.5px; margin-bottom: 0; color: var(--text-muted); }

/* --- Badges --- */
.badge {
    display: inline-block;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 9.5px;
    font-weight: 700;
    text-transform: uppercase;
    font-family: 'JetBrains Mono', monospace;
}
.badge-green  { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
.badge-orange { background: rgba(245, 158, 11, 0.2); color: #f59e0b; border: 1px solid rgba(245, 158, 11, 0.4); }
.badge-blue   { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }

/* --- Footer --- */
.doc-footer {
    margin-top: 36px;
    padding-top: 14px;
    border-top: 2px solid var(--divider);
    font-size: 10.5px;
    color: var(--text-muted);
    display: flex;
    justify-content: space-between;
    align-items: center;
}

@media (max-width: 768px) {
    .document { padding: 24px 16px; margin: 10px; }
    .grid-2, .grid-3 { grid-template-columns: 1fr; }
    .doc-meta { grid-template-columns: 1fr; }
    .quick-toolbar { position: static; margin-bottom: 12px; justify-content: center; }
}
```

---

## JavaScript Snippet (Insert before `</body>`)

```html
<script>
  function toggleTheme() {
    const isLight = document.body.classList.toggle('theme-light');
    const btn = document.getElementById('btn-theme-toggle');
    if (isLight) {
      if (btn) btn.innerHTML = '🌙 Modo Noche';
      localStorage.setItem('doc-theme', 'light');
    } else {
      if (btn) btn.innerHTML = '☀️ Modo Claro';
      localStorage.setItem('doc-theme', 'dark');
    }
  }

  document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('doc-theme');
    const btn = document.getElementById('btn-theme-toggle');
    if (savedTheme === 'light') {
      document.body.classList.add('theme-light');
      if (btn) btn.innerHTML = '🌙 Modo Noche';
    } else {
      document.body.classList.remove('theme-light');
      if (btn) btn.innerHTML = '☀️ Modo Claro';
    }
  });
</script>
```
