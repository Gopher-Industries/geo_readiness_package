# address_cleaning.py
# Normalize and standardize address fields

import re
from postal.expand import expand_address  # from python-postal

STREET_ABBREVS = {
    r'\bSt\b': 'Street',
    r'\bRd\b': 'Road',
    r'\bAve\b': 'Avenue',
    r'\bBlvd\b': 'Boulevard',
    r'\bDr\b': 'Drive',
    r'\bLn\b': 'Lane'
}

def normalize_component(text: str) -> str:
    """Trim, collapse whitespace, standardize common abbreviations, title-case."""
    if not text:
        return ''
    t = text.strip()
    # expand via libpostal
    try:
        variants = expand_address(t)
        t = variants[0] if variants else t
    except Exception:
        pass
    # replace our own abbreviations
    for pattern, full in STREET_ABBREVS.items():
        t = re.sub(pattern, full, t, flags=re.IGNORECASE)
    # collapse multiple spaces
    t = re.sub(r'\s+', ' ', t)
    return t.title()

def clean_address_row(row: dict) -> dict:
    """
    Given a dict with keys street, city, postcode, country,
    return a new dict with cleaned values.
    """
    return {
        'street': normalize_component(row.get('street')),
        'city':   normalize_component(row.get('city')),
        'postcode': normalize_component(row.get('postcode')),
        'country': normalize_component(row.get('country'))
    }

if __name__ == "__main__":
    # quick test
    sample = {'street': '123  main St.', 'city': 'melbourne', 'postcode': ' 3000 ', 'country': 'au'}
    print(clean_address_row(sample))
