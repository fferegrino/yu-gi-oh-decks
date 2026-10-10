import csv
import os
import sys
import time
from pathlib import Path

import requests

data_dir = Path("data")
cursor_file = data_dir / "_last_deck_num.txt"

template_url = "https://ygoprodeck.com/api/decks/getDecks.php?&limit={limit}&offset={offset}"

SECONDS_WAIT = 2
PAGE_SIZE = 20
MAXIMUM_PAGES = 1_000_000
RECORDS_PER_FILE = 10000
RETRY_DELAYS_SECONDS = (1, 2, 4, 8, 16)
RETRY_STATUSES = (403, 408, 429, 500, 502, 503, 504)

TIME_UNITS = {
    'second': 1,
    'minute': 60,
    'hour': 3600,
    'day': 86400, # 24 * 3600
    'week': 604800, # 7 * 24 * 3600
    'month': 2592000, # 30 * 24 * 3600 (approximately)
    'year': 31536000 # 365 * 24 * 3600
}

CSV_KEYS = [
    'deck_num', 'pretty_url', 'deck_name',  'cover_card', 'userid', 'format', 'main_deck', 'extra_deck', 'side_deck',
    'ts_submit_date', 'submit_date', 'ts_edit_date', 'edit_date', 'comments','deck_excerpt', 'deck_description',
]


def get_last_deck_num():
    # A missing cursor means a fresh dataset; an unreadable one must not silently restart from 0,
    # because that would re-append every deck ever published.
    if not cursor_file.exists():
        return 0
    try:
        return int(cursor_file.read_text().strip())
    except ValueError:
        raise SystemExit(f"{cursor_file} does not contain a deck number; refusing to re-download everything")


def set_last_deck_num(num):
    temporary = cursor_file.with_suffix(".tmp")
    temporary.write_text(str(num))
    os.replace(temporary, cursor_file)


def fetch_page(session, offset, limit=PAGE_SIZE):
    """Return one page of decks, newest first; an empty list means there are no more pages."""
    url = template_url.format(offset=offset, limit=limit)
    last_error = None
    for attempt, delay in enumerate(RETRY_DELAYS_SECONDS, start=1):
        try:
            response = session.get(url, timeout=(10, 60))
        except requests.RequestException as exc:
            last_error = str(exc)
        else:
            if response.status_code not in RETRY_STATUSES:
                return decode_page(response, url)
            last_error = f"HTTP {response.status_code}: {response.text[:300]}"

        print(f"Attempt {attempt} failed for {url}: {last_error}", file=sys.stderr)
        if attempt < len(RETRY_DELAYS_SECONDS):
            time.sleep(delay)

    raise SystemExit(f"Giving up on {url}: {last_error}")


def decode_page(response, url):
    try:
        payload = response.json()
    except ValueError:
        body = response.text[:300].replace("\n", " ")
        raise SystemExit(f"Non-JSON response from {url} (HTTP {response.status_code}): {body}")

    # The API signals "past the last page" with an error object rather than an empty list.
    if isinstance(payload, dict) and "error" in payload:
        return []
    if response.status_code >= 400 or not isinstance(payload, list):
        raise SystemExit(f"Unexpected response from {url} (HTTP {response.status_code}): {str(payload)[:300]}")
    return payload


def human_to_seconds_ago(time_string):
    """Convert strings like '6 minutes ago' or 'an hour ago' to seconds; None if unparseable."""
    try:
        count, unit, _ = time_string.split()
        count = 1 if count.lower() in ("a", "an") else int(count)
        return count * TIME_UNITS[unit.lower().rstrip('s')]
    except (AttributeError, ValueError, KeyError):
        return None


def flatten(text):
    if not text:
        return text
    return text.replace('\n', ' ').replace('\r', '').strip()


def prepare_deck(deck, query_ts):
    deck['deck_num'] = int(deck.pop('deckNum'))

    for field, ts_field in (('submit_date', 'ts_submit_date'), ('edit_date', 'ts_edit_date')):
        value = deck.get(field)
        seconds_ago = human_to_seconds_ago(value) if value else None
        if value and seconds_ago is None:
            print(f"Deck {deck['deck_num']}: could not parse {field} {value!r}", file=sys.stderr)
        deck[ts_field] = query_ts - seconds_ago if seconds_ago is not None else None

    deck['deck_description'] = flatten(deck.get('deck_description'))
    deck['deck_excerpt'] = flatten(deck.get('deck_excerpt'))
    return deck


def write_decks(decks):
    by_file = {}
    for deck in sorted(decks, key=lambda d: d['deck_num']):
        file_number = deck['deck_num'] // RECORDS_PER_FILE
        by_file.setdefault(data_dir / f"{file_number:08}.csv", []).append(deck)

    for path, rows in by_file.items():
        already_exists = path.exists()
        # newline="" keeps csv's CRLF terminators byte-identical to the existing files on every OS.
        with open(path, "a", newline="") as w:
            writer = csv.DictWriter(w, fieldnames=CSV_KEYS, extrasaction='ignore')
            if not already_exists:
                writer.writeheader()
            writer.writerows(rows)


def main():
    session = requests.Session()
    session.headers["User-Agent"] = "fferegrino-yu-gi-oh-decks-dataset"

    query_ts = int(time.time())
    last_deck_num = get_last_deck_num()
    print("Last deck number:", last_deck_num)

    new_decks = {}
    for offset in range(0, MAXIMUM_PAGES * PAGE_SIZE, PAGE_SIZE):
        page = fetch_page(session, offset)
        if not page:
            print("No more decks found.")
            break

        page_nums = [int(raw_deck['deckNum']) for raw_deck in page]
        for raw_deck in page:
            if int(raw_deck['deckNum']) <= last_deck_num:
                continue
            deck = prepare_deck(raw_deck, query_ts)
            # Pages shift while we read them, so the same deck can show up on two consecutive pages.
            new_decks[deck['deck_num']] = deck

        if min(page_nums) <= last_deck_num:
            print("Reached last deck number.")
            break
        time.sleep(SECONDS_WAIT)

    if not new_decks:
        print("No new decks.")
        return

    write_decks(new_decks.values())
    # The cursor only moves after the data is on disk, so a crash never skips decks.
    max_deck_num = max(new_decks)
    set_last_deck_num(max_deck_num)
    print(f"Wrote {len(new_decks)} decks; maximum deck number: {max_deck_num}")


if __name__ == "__main__":
    main()
