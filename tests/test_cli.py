"""Tests for the CLI module."""

from newspaper.comics import DEFAULT_COMICS


def test_default_comics_not_empty():
    """Test that we have default comics configured."""
    assert len(DEFAULT_COMICS) > 0


def test_default_comics_have_slugs_and_names():
    """Test that each comic has a slug and name."""
    for slug, name in DEFAULT_COMICS:
        assert slug, "Comic slug should not be empty"
        assert name, "Comic name should not be empty"
        assert " " not in slug, "Slug should not contain spaces"
