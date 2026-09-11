# Beachvolleyball Stats PWA – Minimalplan

## 1. Ziel

Eine einzige HTML-Datei (plus minimal JS/CSS), die im Handy-Browser läuft, offline funktioniert und drei Dinge kann: Spieler anlegen, Match eintragen, Elo-Ranking anzeigen. Kein Overengineering, keine Module-Aufteilung, kein Service-Worker-Feinschliff – das kann alles später kommen, falls überhaupt nötig.

## 2. Design-Referenz

Das gewünschte visuelle Design liegt als Bild im Projektordner unter `/design/beachvolley-app-design.png`. Farbpalette: sandiges Beige, Ozeanblau, Korallakzent. Große abgerundete Buttons, flaches modernes UI, Bottom-Tab-Bar mit drei Reitern (Spieler, Neues Match, Statistik). Die KI soll sich beim Bauen des UIs an diesem Bild orientieren, muss es aber nicht pixelgenau nachbauen.

## 3. Tech-Stack (reduziert)

- Eine `index.html` mit eingebettetem `<style>` und `<script>` – kein separates Modul-System, keine Build-Pipeline
- Speicherung: `localStorage` statt IndexedDB (reicht für ein paar Dutzend Spieler und Matches, deutlich weniger Code)
- Kein Chart.js, kein externes Package – Elo-Verlauf reicht als einfache Tabelle statt Graph
- Kein Service Worker in Version 1 – "Zum Startbildschirm hinzufügen" funktioniert in Chrome auch ohne, offline-Fähigkeit ist nice-to-have, kein Muss für den Start

## 4. Datenmodell

Zwei Arrays im localStorage, als JSON:

```js
players = [
  { id: "p1", name: "Anna", elo: 1500 }
]

matches = [
  { teamA: ["p1","p2"], teamB: ["p3","p4"], scoreA: 21, scoreB: 15 }
]
```

Kein separates "eloDeltas"-Feld pro Match nötig – die Elo-Werte stehen ja schon aktuell bei den Spielern, ein Verlauf ist optional.

## 5. Elo-Berechnung (vereinfacht)

Team-Elo = Mittelwert beider Spieler. Sieger-Team bekommt +Delta, Verlierer-Team -Delta, gleichmäßig auf beide Spieler verteilt. Kein K-Faktor-Unterschied zwischen neuen und etablierten Spielern, ein fixer K=32 reicht für einen Urlaub.

```js
function updateElo(teamA, teamB, scoreA, scoreB) {
  const rA = (teamA[0].elo + teamA[1].elo) / 2;
  const rB = (teamB[0].elo + teamB[1].elo) / 2;
  const expectedA = 1 / (1 + 10 ** ((rB - rA) / 400));
  const actualA = scoreA > scoreB ? 1 : 0;
  const delta = 32 * (actualA - expectedA);
  teamA.forEach(p => p.elo += delta);
  teamB.forEach(p => p.elo -= delta);
}
```

Punktedifferenz-Gewichtung, theta-Verteilung, tanh-Formel – alles gestrichen. Kann später ergänzt werden, falls das Ranking zu "flach" wirkt.

## 6. UI (drei Screens, eine Datei)

1. **Spieler**: Textfeld + "Hinzufügen"-Button, darunter Liste mit Name und Elo
2. **Neues Match**: Tap auf 4 Spieler-Chips (erste 2 = Team A, nächste 2 = Team B), zwei Zahlenfelder für den Score, "Speichern"-Button
3. **Ranking**: Sortierte Liste Name + Elo, absteigend

Keine Head-to-Head-Auswertung, keine "Beste Chemie"-Statistik, keine Diagramme in Version 1. Diese Metriken lassen sich aus den gespeicherten Rohdaten jederzeit nachträglich ableiten, sobald die Kernfunktion steht.

## 7. Akzeptanzkriterien

- [ ] Spieler anlegen funktioniert mit einem Tap
- [ ] Match-Eintrag dauert unter 10 Sekunden (4 Taps + 2 Zahlen + Speichern)
- [ ] Elo-Ranking aktualisiert sich sofort nach dem Speichern
- [ ] Daten bleiben nach Schließen des Browsers erhalten (localStorage)
- [ ] Optik orientiert sich an `/design/beachvolley-app-design.png`

## 8. Bewusst weggelassen (für später, falls überhaupt gewünscht)

- IndexedDB statt localStorage
- Service Worker / echtes Offline-Caching
- Chart.js-Verlaufsgraph
- Head-to-Head- und Team-Chemie-Statistiken
- Punktedifferenz-gewichtetes Elo, unterschiedliche K-Faktoren
- Modulare Dateistruktur (db.js, elo.js, stats.js getrennt)

Diese Liste ist absichtlich lang, damit klar bleibt: Alles, was hier fehlt, war eine bewusste Entscheidung gegen Komplexität, kein Vergessen.
