#!/usr/bin/env python3
"""Laedt eine Datei von einem durch Anubis geschuetzten Server.

www.gen2vdr.de setzt seit kurzem Anubis (https://anubis.techaro.lol/) als
Bot-Abwehr ein. Ein einfaches wget bekommt dadurch nur noch die HTML-Seite
"Making sure you're not a bot!" statt des Tarballs.

Anubis stellt eine Proof-of-Work-Aufgabe: gesucht ist eine Nonce, sodass
sha256(randomData + nonce) mit <difficulty> Hex-Nullen beginnt. Dieses Skript
loest sie genauso wie der JavaScript-Client im Browser, holt sich damit das
Auth-Cookie und laedt anschliessend die eigentliche Datei.

Verwendung:
    anubis-fetch.py <url> <zieldatei>

Nur Python-Standardbibliothek, keine zusaetzlichen Pakete noetig.
"""
import hashlib
import http.cookiejar
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

# Anubis bindet die Challenge an den User-Agent des Anforderers, daher muss
# fuer Challenge und Loesung derselbe UA verwendet werden.
USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/140.0.0.0 Safari/537.36"
)
CHALLENGE_RE = re.compile(
    rb'<script id="anubis_challenge" type="application/json">(.*?)</script>', re.S
)
PASS_CHALLENGE_PATH = "/.within.website/x/cmd/anubis/api/pass-challenge"
# Obergrenze gegen Endlosschleifen, falls der Betreiber die Difficulty stark
# anhebt. Bei Difficulty 5 werden im Mittel rund 1 Mio. Versuche gebraucht.
MAX_ATTEMPTS = 100_000_000
# Serverfehler und Netzwerkaussetzer sind bei einer kleinen, privat betriebenen
# Seite nicht ungewoehnlich. Wartezeit waechst pro Versuch (10s, 20s).
RETRY_ATTEMPTS = 3
RETRY_DELAY_SECONDS = 10


class ChallengeRejected(Exception):
    """Anubis hat die eingereichte Loesung nicht akzeptiert."""


def solve_challenge(random_data, difficulty):
    """Sucht eine Nonce, deren SHA-256 mit <difficulty> Nullen beginnt."""
    prefix = "0" * difficulty
    for nonce in range(MAX_ATTEMPTS):
        digest = hashlib.sha256(f"{random_data}{nonce}".encode()).hexdigest()
        if digest.startswith(prefix):
            return digest, nonce
    raise RuntimeError(f"Keine Loesung nach {MAX_ATTEMPTS} Versuchen gefunden")


def fetch(url, outfile):
    opener = urllib.request.build_opener(
        urllib.request.HTTPCookieProcessor(http.cookiejar.CookieJar())
    )
    opener.addheaders = [("User-Agent", USER_AGENT)]

    body = opener.open(url).read()
    challenge_match = CHALLENGE_RE.search(body)

    if challenge_match:
        payload = json.loads(challenge_match.group(1))
        challenge = payload["challenge"]
        difficulty = payload["rules"]["difficulty"]
        print(
            f"Anubis-Challenge erkannt (Difficulty {difficulty}), loese Proof-of-Work ...",
            file=sys.stderr,
        )

        digest, nonce = solve_challenge(challenge["randomData"], difficulty)
        print(f"Loesung nach {nonce} Versuchen: {digest}", file=sys.stderr)

        query = urllib.parse.urlencode(
            {
                "id": challenge["id"],
                "response": digest,
                "nonce": nonce,
                "redir": url,
                # Anubis protokolliert die Rechendauer nur, ein Wert in einer
                # plausiblen Groessenordnung genuegt.
                "elapsedTime": 4000,
            }
        )
        pass_url = urllib.parse.urljoin(url, f"{PASS_CHALLENGE_PATH}?{query}")
        body = opener.open(pass_url).read()

        if CHALLENGE_RE.search(body):
            # Kommt die Challenge-Seite zurueck, war die Loesung ungueltig oder
            # die Challenge abgelaufen -- ein neuer Anlauf kann helfen.
            raise ChallengeRejected("Anubis hat die Loesung nicht akzeptiert")

    with open(outfile, "wb") as handle:
        handle.write(body)
    print(f"{len(body)} Bytes nach {outfile} geschrieben", file=sys.stderr)


def describe(error):
    """Fehlermeldung, die erkennen laesst, welche Anfrage gescheitert ist."""
    if isinstance(error, urllib.error.HTTPError):
        return f"HTTP {error.code} bei {error.url}"
    if isinstance(error, urllib.error.URLError):
        return f"Netzwerkfehler: {error.reason}"
    return str(error)


def is_transient(error):
    """Nur Serverfehler und Netzwerkaussetzer sind einen neuen Versuch wert.

    Ein 404 oder 403 wird durch Warten nicht besser -- HTTPError zuerst
    pruefen, da es von URLError erbt.
    """
    if isinstance(error, urllib.error.HTTPError):
        return error.code >= 500
    return isinstance(error, (urllib.error.URLError, ChallengeRejected))


def fetch_with_retry(url, outfile):
    for attempt in range(1, RETRY_ATTEMPTS + 1):
        try:
            fetch(url, outfile)
            return
        except (urllib.error.URLError, ChallengeRejected) as error:
            message = describe(error)
            if not is_transient(error) or attempt == RETRY_ATTEMPTS:
                sys.exit(f"Fehler: {message}")
            delay = RETRY_DELAY_SECONDS * attempt
            print(
                f"{message} (Versuch {attempt}/{RETRY_ATTEMPTS}), "
                f"neuer Versuch in {delay}s ...",
                file=sys.stderr,
            )
            time.sleep(delay)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(f"Verwendung: {sys.argv[0]} <url> <zieldatei>")
    fetch_with_retry(sys.argv[1], sys.argv[2])
