# Beachvolleyball Stats (PWA)

Eine schlanke, offline-fähige Web-App zum Festhalten eures Beachvolleyball-Urlaubs:

- 🏐 **Spieler** anlegen (ein Tap, mit optionalem ♀/♂-Geschlecht) – mit Bilanz pro Spieler: Siege, Niederlagen, Spiele gesamt, Spiele heute, Gesamtpunkte
- ⚔️ **Neues Match** eintragen – 4 Spieler-Chips antippen (erste zwei = Team A, nächste zwei = Team B), Punkte per **Voreinstellung (15–21)** oder −/＋-Stepper wählen, speichern; optional **Punkte-Details** erfassen (Team → Spieler → Wie: 💥 Kill, 🛡️ Block, 🖐️ Annahme-Fehler, ⚠️ Gegnerfehler, 🎲 Sonstiges) – ohne Einfluss auf Elo/Ranking; „gemischt“ (⚧) wird aus den Geschlechtern automatisch erkannt
- 🏖️ **Events** – ordne Matches Events zu (z. B. *Beachvolleyballurlaub*, *Casual Play*); Historie & Statistik lassen sich pro Event filtern
- 🏆 **Statistik** – Bilanz aus allen Matches: meiste Siege, bestes Team, längste Siegesserie, höchstes Ergebnis, größter Sieg, seltenste & fehlende Matchups
- 📜 **Historie** – alle gespeicherten Matches mit Punktestand, Datum und Sieger; **Tap öffnet Match-Details** (wer hat Punkte gemacht & wie), **✕ löscht** ein Match inkl. Elo-Rücknahme
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
| **GitHub Pages** (diese Repo-Seite) | 🔴 LIVE: **https://Korbiii.github.io/beachvolleyball-stats/** – „Zum Startbildschirm hinzufügen“/„Installieren“ (Android-PWA), **offline** nutzbar |

> Hinweis: Service Worker & Manifest benötigen `https` (oder localhost). Als lokale `file://`-Datei läuft die App trotzdem komplett.

## Screens
Spieler · Neues Match · Historie · Statistik · Events (untere Tab-Leiste)