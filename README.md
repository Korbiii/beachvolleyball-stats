# Beachvolleyball Stats (PWA)

Eine schlanke, offline-fähige Web-App zum Festhalten eures Beachvolleyball-Urlaubs:

- 🏐 **Spieler** anlegen (ein Tap) und verwalten
- ⚔️ **Neues Match** eintragen – 4 Spieler-Chips antippen (erste zwei = Team A, nächste zwei = Team B), Punkte per **Voreinstellung (15–21)** oder −/＋-Stepper wählen, speichern
- 📜 **Historie** – alle gespeicherten Matches mit Punktestand, Datum und Sieger
- 🏆 **Elo-Ranking** – aktualisiert sich sofort nach jedem Match

## Technik

- Eine einzige `index.html` mit eingebettetem CSS/JS, keine Build-Pipeline
- Daten dauerhaft in `localStorage` (Spieler + Matches) – überleben Browser-Neustart
- Elo-Formel (vereinfacht): Team-Elo = Mittelwert beider Spieler, K = 32, Sieger +Δ / Verlierer −Δ
- PWA: `manifest.json`, `icon.svg`, `sw.js` (Service Worker für Offline-Cache bei https-Hosting)

## Auf dem Handy nutzen

| Weg | Ergebnis |
|---|---|
| `index.html` lokal im Handy-Browser öffnen | Volle Funktion + Speicherung, ohne Hosten |
| Dieses Repo auf HTTPS-Hosting (GitHub Pages, Netlify, …) | „Zum Startbildschirm hinzufügen“/„Installieren“, **offline** nutzbar |

> Hinweis: Service Worker & Manifest benötigen `https` (oder localhost). Als lokale `file://`-Datei läuft die App trotzdem komplett.

## Screens
Spieler · Neues Match · Historie · Statistik (untere Tab-Leiste)