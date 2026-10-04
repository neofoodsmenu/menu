# NEO FOODS – Decap CMS Setup

Die Website ist für Decap CMS vorbereitet.

## Was bereits eingebaut ist

- `/admin/` als Decap-CMS-Oberfläche
- `content/speisekarte.json`
- `content/getraenkekarte.json`
- `content/eiskarte.json`
- `menu-cms.js` rendert die bestehenden Karten aus den CMS-Daten
- Upload-Ordner `uploads/`
- Das bestehende Design (`readable-menu.css`) bleibt erhalten

## Wichtig: einmalig GitHub-Login aktivieren

GitHub verlangt für den Decap-GitHub-Backend-Login einen OAuth-Server. Cloudflare Pages ist dafür **nicht** nötig.

## PDFs

Änderungen im CMS aktualisieren die HTML-Karten sofort nach dem GitHub-Pages-Deploy, aber **nicht** die vorhandenen PDF-Dateien (`speisekarte.pdf`, `getraenkekarte.pdf`, `eiskarte.pdf`).


## ing. Tayyib Erdem, BSc
