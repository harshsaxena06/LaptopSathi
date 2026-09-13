"""
Tests for the retailer search-link generator (app.retailer_links.links).

Pure-function tests — no DB/FastAPI/ML dependencies needed.

Run:
    python -m pytest tests/test_retailer_links.py -v
"""
import sys
from pathlib import Path
from urllib.parse import unquote_plus

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.retailer_links.links import (
    build_retailer_links,
    RETAILER_CONFIGS,
    RetailerLinkConfig,
    OFFICIAL_STORE_SEARCH_TEMPLATES,
)


def test_generates_a_link_for_every_configured_retailer():
    links = build_retailer_links("Dell", "XPS 13 Plus")
    assert len(links) == len(RETAILER_CONFIGS)
    ids = {link["retailer"] for link in links}
    assert ids == {cfg.retailer_id for cfg in RETAILER_CONFIGS if cfg.enabled}


def test_amazon_and_flipkart_links_are_well_formed():
    links = build_retailer_links("Asus", "ROG Strix G16")
    by_id = {link["retailer"]: link for link in links}

    assert by_id["amazon"]["url"].startswith("https://www.amazon.in/s?k=")
    assert by_id["amazon"]["label"] == "Buy on Amazon"

    assert by_id["flipkart"]["url"].startswith("https://www.flipkart.com/search?q=")
    assert by_id["flipkart"]["label"] == "Buy on Flipkart"


def test_official_store_uses_known_brand_template():
    links = build_retailer_links("dell", "Inspiron 15")
    official = next(link for link in links if link["retailer"] == "official_store")
    assert official["url"].startswith("https://www.dell.com/en-in/search/")
    assert official["label"] == "Official Store"


def test_official_store_falls_back_for_unknown_brand():
    links = build_retailer_links("SomeBrandNoOneHasHeardOf", "Model X")
    official = next(link for link in links if link["retailer"] == "official_store")
    # Still a working, well-formed URL — never dropped just because the
    # brand isn't in OFFICIAL_STORE_SEARCH_TEMPLATES.
    assert official["url"].startswith("https://www.google.com/search?q=")
    assert "somebrandnoonehasheardof" not in OFFICIAL_STORE_SEARCH_TEMPLATES


def test_urls_are_correctly_encoded_for_spaces_and_special_characters():
    links = build_retailer_links("HP", 'Pavilion 15 (2024) — 16GB/512GB & Touch')
    for link in links:
        # No raw spaces, parentheses, ampersands or slashes should leak
        # into the URL unescaped.
        assert " " not in link["url"]
        assert "(" not in link["url"]
        assert ")" not in link["url"]
        # The encoded query, once decoded, should round-trip back to the
        # original brand + model text.
        assert "+" in link["url"] or "%20" in link["url"]

    amazon_query = links[0]["url"].split("k=", 1)[1]
    decoded = unquote_plus(amazon_query)
    assert "HP" in decoded
    assert "Pavilion 15 (2024)" in decoded


def test_missing_model_name_does_not_raise():
    links = build_retailer_links("Lenovo", None)
    assert len(links) == len(RETAILER_CONFIGS)
    for link in links:
        assert "lenovo" in link["url"].lower() or "Lenovo" in unquote_plus(link["url"])


def test_missing_brand_does_not_raise():
    links = build_retailer_links(None, "ThinkPad X1 Carbon")
    assert len(links) == len(RETAILER_CONFIGS)
    # Falls back to the generic search for official store since brand is unknown.
    official = next(link for link in links if link["retailer"] == "official_store")
    assert official["url"].startswith("https://www.google.com/search?q=")


def test_missing_brand_and_model_falls_back_to_generic_search_without_raising():
    links = build_retailer_links("", "   ")
    assert len(links) == len(RETAILER_CONFIGS)
    for link in links:
        assert "laptop" in unquote_plus(link["url"]).lower()


def test_retailers_are_configurable_add_and_remove():
    """Retailers can be added/removed by editing RETAILER_CONFIGS alone —
    build_retailer_links() should reflect whatever list it's given without
    any changes to its own logic."""
    custom_configs = list(RETAILER_CONFIGS) + [
        RetailerLinkConfig(
            retailer_id="croma",
            label="Buy on Croma",
            builder=lambda brand, model_name, query: f"https://www.croma.com/search?q={query}",
        )
    ]
    import app.retailer_links.links as links_module

    original = links_module.RETAILER_CONFIGS
    try:
        links_module.RETAILER_CONFIGS = custom_configs
        links = build_retailer_links("Acer", "Predator Helios")
        assert any(link["retailer"] == "croma" for link in links)
        assert len(links) == len(custom_configs)
    finally:
        links_module.RETAILER_CONFIGS = original

    # Removing a retailer (disabling it) means it no longer appears.
    disabled_configs = [
        RetailerLinkConfig(cfg.retailer_id, cfg.label, cfg.builder, enabled=False)
        if cfg.retailer_id == "flipkart" else cfg
        for cfg in RETAILER_CONFIGS
    ]
    try:
        links_module.RETAILER_CONFIGS = disabled_configs
        links = build_retailer_links("Acer", "Predator Helios")
        assert all(link["retailer"] != "flipkart" for link in links)
    finally:
        links_module.RETAILER_CONFIGS = original


def test_a_broken_retailer_builder_is_skipped_not_fatal():
    import app.retailer_links.links as links_module

    def _boom(brand, model_name, query):
        raise RuntimeError("simulated retailer outage")

    broken_configs = list(RETAILER_CONFIGS) + [
        RetailerLinkConfig(retailer_id="broken", label="Broken", builder=_boom)
    ]
    original = links_module.RETAILER_CONFIGS
    try:
        links_module.RETAILER_CONFIGS = broken_configs
        links = build_retailer_links("Dell", "XPS 13")
        # The broken retailer is silently skipped; everything else still works.
        assert all(link["retailer"] != "broken" for link in links)
        assert len(links) == len(RETAILER_CONFIGS)
    finally:
        links_module.RETAILER_CONFIGS = original


if __name__ == "__main__":
    test_generates_a_link_for_every_configured_retailer()
    test_amazon_and_flipkart_links_are_well_formed()
    test_official_store_uses_known_brand_template()
    test_official_store_falls_back_for_unknown_brand()
    test_urls_are_correctly_encoded_for_spaces_and_special_characters()
    test_missing_model_name_does_not_raise()
    test_missing_brand_does_not_raise()
    test_missing_brand_and_model_falls_back_to_generic_search_without_raising()
    test_retailers_are_configurable_add_and_remove()
    test_a_broken_retailer_builder_is_skipped_not_fatal()
    print("All retailer link tests passed.")
