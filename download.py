import requests
import time
from pathlib import Path
import csv

data_dir = Path("data")

template_url = "https://ygoprodeck.com/api/decks/getDecks.php?&limit={limit}&offset={offset}"

def get_last_deck_num():
    try:
        with open(data_dir / '_last_deck_num.txt', 'r') as f:
            return int(f.read())
    except:
        return 0

def set_last_deck_num(num):
    with open(data_dir / '_last_deck_num.txt', 'w') as f:
        f.write(str(num))


SECONDS_WAIT = 2
PAGE_SIZE = 20
MAXIMUM_PAGES = 1_000_000

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

def get_decks_for_page(offset, limit = PAGE_SIZE):
    response = requests.get(template_url.format(offset=offset, limit=limit))
    data = response.json()
    if 'error' in data:
        return []
    else:
        return data


QUERY_TS = int(time.time())

RECORDS_PER_FILE = 10000

LAST_DECK_NUM = get_last_deck_num()
# Maximum integer available in 32-bit systems
MINIMUM_CURRENT_DECK_NUM = 2 ** 31 - 1
MAXIMUM_CURRENT_DECK_NUM = 0

print("Last deck number:", LAST_DECK_NUM)

def human_to_seconds_ago(time_string):
    count, unit, _ = time_string.split()
    count = int(count)
    unit = unit.lower().rstrip('s')
    return count * TIME_UNITS[unit]

for offset in range(0, MAXIMUM_PAGES, PAGE_SIZE):

    decks = get_decks_for_page(offset)
    if len(decks) == 0:
        print("No more decks found.")
        break
    for deck in get_decks_for_page(offset):
        deck['deck_num'] = int(deck.pop('deckNum'))
        MINIMUM_CURRENT_DECK_NUM = min(MINIMUM_CURRENT_DECK_NUM, deck['deck_num'])
        MAXIMUM_CURRENT_DECK_NUM = max(MAXIMUM_CURRENT_DECK_NUM, deck['deck_num'])
        if MINIMUM_CURRENT_DECK_NUM <= LAST_DECK_NUM:
            break

        file_number = deck['deck_num'] // RECORDS_PER_FILE
        corresponding_file_name = data_dir / f"{file_number:08}.csv"
        deck['ts_submit_date'] = QUERY_TS - human_to_seconds_ago(deck.get('submit_date'))
        if deck.get('edit_date'):
            deck['ts_edit_date'] = QUERY_TS - human_to_seconds_ago(deck.get('edit_date'))
        else:
            deck['ts_edit_date'] = None

        deck['deck_description'] = deck['deck_description'].replace('\n', ' ').replace('\r', '').strip()
        if deck['deck_excerpt']:
            deck['deck_excerpt'] = deck['deck_excerpt'].replace('\n', ' ').replace('\r', '').strip()

        already_exists = corresponding_file_name.exists()
        with open(corresponding_file_name, "a") as w:
            writer = csv.DictWriter(w, fieldnames=CSV_KEYS, extrasaction='ignore')
            if not already_exists:
                writer.writeheader()
            writer.writerow(deck)
    time.sleep(SECONDS_WAIT)
    if MINIMUM_CURRENT_DECK_NUM <= LAST_DECK_NUM:
        print("Reached last deck number.")
        break

print("Maximum deck number:", MAXIMUM_CURRENT_DECK_NUM)
set_last_deck_num(MAXIMUM_CURRENT_DECK_NUM)
