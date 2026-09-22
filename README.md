# Beachvolleyball Stats (PWA)

Eine schlanke, offline-fähige Web-App zum Festhalten eures Beachvolleyball-Urlaubs:

- 🏐 **Spieler** anlegen (ein Tap, mit optionalem ♀/♂/⚧-Geschlecht und 📏-Größe unter/ab 175 cm) – mit Bilanz pro Spieler: Siege, Niederlagen, Spiele gesamt, Spiele heute, Gesamtpunkte
- ⚔️ **Neues Match** eintragen – 4 Spieler-Chips antippen (erste zwei = Team A, nächste zwei = Team B), Punkte per **Voreinstellung (15–21)** oder −/＋-Stepper wählen, speichern; optional **Punkte-Details** erfassen (Spieler wählen + Aktion, die zum Punkt geführt hat: 💥 Kill/Aufschlag, 🛡️ Block, 🖐️ Annahme-Fehler, 🎯 Zuspiel-Fehler, ⚔️ Angriffs-Fehler, 🎲 Sonstiges) – **💥 Kill & 🛡️ Block geben den Punkt dem eigenen Team, die Fehler-Typen dem Gegner**; der Punktestand des Punkte-Teams zählt automatisch mit, ohne Einfluss auf Elo/Ranking; „gemischt“ (⚧) wird aus unterschiedlichen Geschlechtern im Team automatisch erkannt
- 🏖️ **Events** – ordne Matches Events zu (z. B. *Beachvolleyballurlaub*, *Casual Play*); Historie & Statistik lassen sich pro Event filtern
- 🏆 **Statistik** – Bilanz aus allen Matches: meiste Siege, bestes Team, längste Siegesserie, höchstes Ergebnis, größter Sieg, seltenste & fehlende Matchups
- 📜 **Historie** – alle gespeicherten Matches mit Punktestand, Datum und Sieger; **Tap öffnet Match-Details** (wer hat Punkte gemacht & wie), **✕ löscht** ein Match inkl. Elo-Rücknahme
- 🏆 **Elo-Ranking** – aktualisiert sich sofort nach jedem Match

## Technik

- Eine einzige `index.html` mit eingebettetem CSS/JS, keine Build-Pipeline
- Daten dauerhaft **verschlüsselt** in `localStorage` (Spieler + Matches) – überleben Browser-Neustart
- 🔐 **Ende-zu-Ende-Verschlüsselung (AES-256-GCM):** Alle Daten werden *vor* dem Speichern im Browser verschlüsselt (Web Crypto: PBKDF2-SHA256 → AES-256-GCM) und erst danach lokal bzw. nach **Supabase** geschrieben. Schlüsselbasis ist das **gemeinsame Passwort**; es wird nie übertragen – ohne es sind die Daten auch für Supabase, den Host und Mitlesende unlesbar.
- ☁️ **Supabase-Synchronisation** über die reine REST-API (PostgREST, kein SDK): eine Zeile pro Passwort in der Tabelle `vault`; Abgleich „neuer gewinnt" über Zeitstempel, manuell per „🔁 Jetzt synchronisieren" oder automatisch beim Start. Offline läuft die App trotzdem komplett weiter (lokales verschlüsseltes Abbild). Optional lässt sich ein **passwortgeschützter Standard-Zugang** fest einbauen (Team-Freischaltung) – eigene Verbindungen bleiben jederzeit möglich.
- Elo-Formel (vereinfacht): Team-Elo = Mittelwert beider Spieler, K = 32, Sieger +Δ / Verlierer −Δ
- PWA: `manifest.json`, `icon.svg`, `sw.js` (Service Worker für Offline-Cache bei https-Hosting); die App-Shell wird per „network-first" geladen – Updates erscheinen also automatisch, sobald eine neue Version veröffentlicht wird

## 🔐 Verschlüsselung & Supabase einrichten (einmalig)

> Die App läuft ohne Supabase weiter (alles wird lokal verschlüsselt gespeichert). Supabase kommt erst mit der Synchronisation ins Spiel.

1. **Supabase-Projekt anlegen** (https://supabase.com) → Projekt-URL + **Publishable-Key** (früher „anon public", beginnt mit `sb_publishable_…`) aus den Projekt-Einstellungen („API Keys") kopieren. Der **Secret-/`service_role`-Key wird niemals** verwendet.
2. **Tabelle anlegen:** Im SQL-Editor des Projekts einmalig ausführen:

```sql
create table if not exists vault (
  key_id text primary key,
  payload text not null,
  updated_at timestamptz not null default now()
);
alter table vault enable row level security;
drop policy if exists "vault anon read"   on vault;
drop policy if exists "vault anon insert" on vault;
drop policy if exists "vault anon update" on vault;
create policy "vault anon read"   on vault for select using (true);
create policy "vault anon insert" on vault for insert with check (true);
create policy "vault anon update" on vault for update using (true) with check (true);
```

3. In der App beim Start im Dialog **🔒 Team** das **Team-Passwort** eingeben (Standard-Verbindung) **oder** auf **🌐 Eigene Verbindung** wechseln und dort Projekt-URL + Publishable-Key + ein **gemeinsames Passwort** eintragen. Alle Geräte mit demselben Passwort sehen denselben Bestand.

### 🔑 Ein gemeinsames Passwort für alle

Jede Verbindung (Standard *oder* eigene) wird über **ein einziges gemeinsames Passwort** genutzt. Aus ihm wird abgeleitet:

- die **`key_id`** (deterministisch per PBKDF2) → gleiches Passwort = gleiche Zeile in Supabase,
- der **AES-256-GCM-Schlüssel** → gleiches Passwort = gleiche entschlüsselbare Daten.

So sieht jedes Gerät, das dasselbe Passwort eingibt, automatisch denselben Stand. Das Passwort wird **nie übertragen** – es bleibt auf den Geräten und ist nirgends gespeichert (außer optional lokal, „Auf diesem Gerät merken").

> ⚠️ **Passwort vergessen = Daten weg.** Es gibt keine Hintertür und keinen Reset. Nutzt deshalb eine lange, zufällige Passphrase (4–6 Wörter) und bewahrt sie sicher auf.

### 🔒 Standard-Verbindung (Team) – passwortgeschützt

Damit alle aus eurem Team dieselbe Supabase-Verbindung nutzen können, ohne die Zugangsdaten jedes Mal einzutippen, kann ein **Standard-Zugang fest in die App eingebaut** werden – geschützt durch das **Team-Passwort** (das zugleich das gemeinsame Daten-Passwort ist).

Im Repo liegt dafür der Generator:

```bash
python3 tools/make-team-config.py
# → fragt Projekt-URL, Publishable-Key und Team-Passwort ab
# → gibt das fertige JS-Snippet aus
```

Das Snippet ersetzt den Block `var DEFAULT_CLOUD = { u:'', k:'', p:'' };` oben im `<script>` von `index.html`:

```js
var DEFAULT_CLOUD={
  u:'<base64url der Projekt-URL>',
  k:'<base64url des Publishable-Keys>',
  p:'pbkdf2$150000$<salt>$<hash>'
};
```

Verhalten:
- Bleibt `DEFAULT_CLOUD` leer, zeigt die App beim Start nur **🌐 Eigene Verbindung**; jede/r richtet die eigene Verbindung + Passwort ein.
- Ist es gesetzt, erscheint der Tab **🔒 Team** mit einem Feld **„Team-Passwort"**. Stimmt das Passwort, werden URL + Key automatisch aktiviert **und** der gemeinsame Bestand entschlüsselt.
- Wer das Projekt auf GitHub findet, aber das Team-Passwort nicht kennt, nutzt einfach die eigenen Zugänge – die Struktur der App ist dafür offen ausgelegt.

### ⚠️ Ehrlich zum „Passwort-Schutz"

Eine statische App kann **keine echten Geheimnisse** enthalten: `index.html` ist öffentlich einsehbar, eingebaute Werte sind also auslesbar – hier nur base64url-**verschleiert** und hinter einem Passwort-Abgleich (PBKDF2-SHA256) versteckt. Das Passwort ist damit eine **Hürde, kein Geheimnis** (Rateversuche werden durch die 150k-Iterationen teuer, sind aber möglich).

Das ist trotzdem unkritisch, und zwar aus zwei unabhängigen Gründen:

1. Der **Publishable-Key ist ein öffentlicher Schlüssel** – Supabase rechnet damit, dass er im Client steht. Schutz kommt aus den RLS-Policies, die nur die `vault`-Tabelle freigeben.
2. Die **eigentlichen Daten sind Ende-zu-Ende verschlüsselt** (AES-256-GCM, Passwort). Selbst wer URL + Key kennt, sieht nur Ciphertext und kann nichts entschlüsseln oder fälschen.

**Niemals** den Secret-/`service_role`-Key im Client hinterlegen (das Tool lehnt ihn ab). Wer mehr als eine „Hürde" möchte, kann serverseitig nachschärfen, z. B. eine RLS-Policy, die zusätzlich einen geheimen Request-Header verlangt – dann erzwingt die Datenbank den Zugang, nicht nur die UI.

### Gemeinsames Passwort – Details

- Beim ersten Start das **Team-Passwort** (oder ein eigenes gemeinsames Passwort) eingeben – daraus werden `key_id` und Schlüssel abgeleitet.
- Auf **jedem weiteren Gerät dasselbe Passwort** eingeben: gleicher Bestand, sofort entschlüsselbar.
- Optional lokal gemerkt („Auf diesem Gerät merken", Standard an). Ohne diese Option fragt die App bei jedem Start.
- In „Supabase" liegt nur ein abgeleiteter **Blind-Index** (`key_id`, PBKDF2 des Passworts) – er verrät, *dass* ein Bestand existiert, nicht dessen Inhalt.

### Sicherheitsmodell – kurz

| Was | Wo |
|---|---|
| Klartext (Spieler, Matches …) | nur im entsperrten Browser-Speicher während der Sitzung |
| AES-256-GCM-Ciphertext | lokal (`localStorage`) **und** Supabase (`vault`-Tabelle) |
| Gemeinsames Passwort | nur beim Nutzer + optional lokal gemerkt; **nie** übertragen |
| `key_id` (Blind-Index), Zeitstempel | Supabase (kein Inhalts-Rückschluss) |

> ⚠️ RLS ist für die `vault`-Tabelle bewusst offen („Publishable/anon darf lesen/schreiben"), weil der Inhalt verschlüsselt ist. Falls du das nicht möchtest, ersetze die Policies durch eigene Regeln – die App nutzt nur den Publishable-Zugang mit der Tabelle `vault`.

## Auf dem Handy nutzen

| Weg | Ergebnis |
|---|---|
| `index.html` lokal im Handy-Browser öffnen | Volle Funktion + Speicherung, ohne Hosten |
| **GitHub Pages** (diese Repo-Seite) | 🔴 LIVE: **https://Korbiii.github.io/beachvolleyball-stats/** – „Zum Startbildschirm hinzufügen“/„Installieren“ (Android-PWA), **offline** nutzbar |

> Hinweis: Service Worker & Manifest benötigen `https` (oder localhost). Als lokale `file://`-Datei läuft die App trotzdem komplett.

## Screens
Spieler · Neues Match · Historie · Statistik · Events (untere Tab-Leiste)