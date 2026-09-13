"""
Retailer Search-Link Generator.

Builds outbound "search for this laptop on X" links from a laptop's brand +
exact model name, so recommendation cards can offer one-click "Buy on
Amazon", "Buy on Flipkart" and "Official Store" buttons WITHOUT storing any
retailer URLs in the Knowledge Base itself. Links are generated on the fly,
at request time, from fields the KB already has (brand, model_name).

Kept as a small, dependency-free, pure-function utility (no DB session, no
ORM models) so any router/service can reuse it — recommendations today,
search/saved-laptops/comparison tomorrow — without extra coupling.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, List, Optional
from urllib.parse import quote_plus

# ---------------------------------------------------------------------------
# Official brand-store search URLs.
#
# Each entry maps a lower-cased brand name to a URL *template* containing a
# single "{query}" placeholder for the URL-encoded search text. Add, remove,
# or repoint a brand here without touching any generation logic below.
# Brands not listed here still get a working "Official Store" link via the
# generic fallback search below.
# ---------------------------------------------------------------------------
OFFICIAL_STORE_SEARCH_TEMPLATES = {
    "dell": "https://www.dell.com/en-in/search/{query}",
    "hp": "https://www.hp.com/in-en/shop/search?q={query}",
    "lenovo": "https://www.lenovo.com/in/en/search?text={query}",
    "asus": "https://www.asus.com/in/search/?keyword={query}",
    "acer": "https://www.acer.com/in-en/search#q={query}",
    "apple": "https://www.apple.com/in/shop/search?q={query}",
    "msi": "https://www.msi.com/search?q={query}",
    "samsung": "https://www.samsung.com/in/search/?searchvalue={query}",
    "microsoft": "https://www.microsoft.com/en-in/search/shop/devices?q={query}",
    "lg": "https://www.lg.com/in/search/?search={query}",
    "infinix": "https://www.infinixmobility.com/in/search?q={query}",
    "realme": "https://www.realme.com/in/search?q={query}",
}

# Used for brands with no known storefront above, so "Official Store" still
# resolves to a useful, working link instead of being skipped.
_FALLBACK_OFFICIAL_STORE_URL = "https://www.google.com/search?q={query}"

# Used when both brand and model_name are missing/blank, so link generation
# never has to raise or return nothing.
_UNKNOWN_SEARCH_TEXT = "laptop"


def _encode(text: str) -> str:
    """URL-encode text for a query string — spaces become '+', and symbols
    like '/', '(', ')', '&' are percent-escaped so the link doesn't break."""
    return quote_plus(text.strip())


def _search_text(brand: Optional[str], model_name: Optional[str]) -> str:
    """Builds the human-readable search phrase from brand + model, tolerating
    either being missing/blank so callers never have to special-case it."""
    parts = [p.strip() for p in (brand, model_name) if p and p.strip()]
    return " ".join(parts) if parts else _UNKNOWN_SEARCH_TEXT


def _amazon_url(query: str) -> str:
    return f"https://www.amazon.in/s?k={_encode(query)}"


def _flipkart_url(query: str) -> str:
    return f"https://www.flipkart.com/search?q={_encode(query)}"


def _official_store_url(brand: Optional[str], query: str) -> str:
    key = (brand or "").strip().lower()
    template = OFFICIAL_STORE_SEARCH_TEMPLATES.get(key, _FALLBACK_OFFICIAL_STORE_URL)
    return template.format(query=_encode(query))


@dataclass(frozen=True)
class RetailerLinkConfig:
    """One configurable retailer entry.

    `builder` receives (brand, model_name, search_text) and returns the
    fully-formed URL. To add a new retailer: append a RetailerLinkConfig to
    RETAILER_CONFIGS below. To remove one: delete its entry, or set
    enabled=False. Nothing else in this module (or its callers) needs to
    change either way.
    """
    retailer_id: str
    label: str
    builder: Callable[[Optional[str], Optional[str], str], str]
    enabled: bool = True


RETAILER_CONFIGS: List[RetailerLinkConfig] = [
    RetailerLinkConfig(
        retailer_id="amazon",
        label="Buy on Amazon",
        builder=lambda brand, model_name, query: _amazon_url(query),
    ),
    RetailerLinkConfig(
        retailer_id="flipkart",
        label="Buy on Flipkart",
        builder=lambda brand, model_name, query: _flipkart_url(query),
    ),
    RetailerLinkConfig(
        retailer_id="official_store",
        label="Official Store",
        builder=lambda brand, model_name, query: _official_store_url(brand, query),
    ),
]


def build_retailer_links(brand: Optional[str], model_name: Optional[str]) -> List[dict]:
    """Generates search-link entries for every enabled retailer in
    RETAILER_CONFIGS for the given brand + exact model name.

    Never raises: a missing/blank brand and/or model_name degrades
    gracefully to whatever text is available (or a generic "laptop" search)
    instead of breaking the caller's recommendation flow. Likewise, if one
    retailer's builder ever misbehaves, that single link is skipped rather
    than failing the whole response.

    Returns a list of {"retailer": str, "label": str, "url": str} dicts,
    e.g.:
        [
          {"retailer": "amazon", "label": "Buy on Amazon", "url": "..."},
          {"retailer": "flipkart", "label": "Buy on Flipkart", "url": "..."},
          {"retailer": "official_store", "label": "Official Store", "url": "..."},
        ]
    """
    query = _search_text(brand, model_name)

    links: List[dict] = []
    for cfg in RETAILER_CONFIGS:
        if not cfg.enabled:
            continue
        try:
            url = cfg.builder(brand, model_name, query)
        except Exception:
            continue
        links.append({"retailer": cfg.retailer_id, "label": cfg.label, "url": url})
    return links
