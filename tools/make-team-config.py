#!/usr/bin/env python3
"""Erzeugt die drei DEFAULT_CLOUD-Werte für index.html (Standard-Verbindung / Team).

Aufruf:
    python3 tools/make-team-config.py
    python3 tools/make-team-config.py --url https://xxxx.supabase.co --publishable sb_publishable_... --password 'mein-team-passwort'

Ergebnis: ein JS-Snippet, das du 1:1 in index.html in den Block
    var DEFAULT_CLOUD = { u:'', k:'', p:'' };
einsetzt.

Das Team-Passwort ist zugleich das gemeinsame Daten-Passwort: Aus ihm wird die
key_id (PBKDF2) und der AES-256-GCM-Schlüssel abgeleitet. Alle Geräte mit
demselben Passwort teilen denselben verschlüsselten Bestand.

WICHTIG / ehrlich: Eine statische App kann keine echten Geheimnisse enthalten –
der Quelltext ist öffentlich. Diese Werte sind nur verschleiert (base64url) und
das Passwort ist nur eine Hürde, kein Geheimnis. Das ist unkritisch, weil der
Publishable-Key ohnehin öffentlich ist (Schutz über RLS) und alle Nutzerdaten
mit dem Passwort Ende-zu-Ende verschlüsselt sind.
NIEMALS den Secret-/service_role-Key verwenden!
"""
import argparse
import base64
import getpass
import hashlib
import os
import sys

ITER_DEFAULT = 150000  # muss zum App-Default passen (nur Info – der Wert steht im Verifier)


def b64u(raw: bytes) -> str:
    return base64.urlsafe_b64encode(raw).decode('ascii').rstrip('=')


def make_verifier(password: str, iterations: int = ITER_DEFAULT) -> str:
    """pbkdf2$<iter>$<saltB64u>$<hashB64u> – identisch zur JS-Prüfung in index.html."""
    salt = os.urandom(16)
    h = hashlib.pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, 32)
    return 'pbkdf2$%d$%s$%s' % (iterations, b64u(salt), b64u(h))


def main() -> int:
    p = argparse.ArgumentParser(description='DEFAULT_CLOUD-Werte für BV Stats erzeugen')
    p.add_argument('--url', help='Supabase-Projekt-URL, z. B. https://abcd.supabase.co')
    p.add_argument('--anon', '--publishable', dest='anon', help='Supabase Publishable-Key (sb_publishable_…, früher anon public) – NICHT service_role/Secret')
    p.add_argument('--password', help='Team-Passwort (ansonsten interaktive Abfrage)')
    p.add_argument('--iterations', type=int, default=ITER_DEFAULT, help='PBKDF2-Iterationen (Standard %d)' % ITER_DEFAULT)
    a = p.parse_args()

    url = a.url or input('Supabase-Projekt-URL: ').strip()
    anon = a.anon or input('Supabase Publishable-Key (sb_publishable_…): ').strip()
    pw = a.password if a.password is not None else getpass.getpass('Team-Passwort: ')

    if not url or not anon or not pw:
        print('FEHLER: URL, Anon-Key und Passwort dürfen nicht leer sein.', file=sys.stderr)
        return 1
    if url.startswith('http://'):
        print('HINWEIS: http:// ist unsicher – im Browser nur mit https nutzbar.', file=sys.stderr)
    if url and not url.startswith('http'):
        url = 'https://' + url
    if 'service_role' in anon or anon.startswith('sb_secret_'):
        print('FEHLER: Das sieht nach einem Secret-Key aus (service_role / sb_secret_...) – dieser darf NIEMALS in den Client!', file=sys.stderr)
        return 1
    if len(pw) < 8:
        print('WARNUNG: Ein langes, zufälliges Passwort ist deutlich besser (empfohlen: 4+ Wörter).', file=sys.stderr)

    snippet = (
        "var DEFAULT_CLOUD={\n"
        "  u:'%s',\n"
        "  k:'%s',\n"
        "  p:'%s'\n"
        "};" % (b64u(url.encode('utf-8')), b64u(anon.encode('utf-8')), make_verifier(pw, a.iterations))
    )

    print('\n--- In index.html bei DEFAULT_CLOUD einsetzen -------------------------\n')
    print(snippet)
    print('\n---------------------------------------------------------------------')
    print('Passwort NICHT hier vergessen – es schützt die Verbindung UND verschlüsselt')
    print('alle Daten. Ohne es ist der gemeinsame Bestand unwiederbringlich verloren.')
    print('Es ist nirgendwo sonst gespeichert.')
    return 0


if __name__ == '__main__':
    sys.exit(main())