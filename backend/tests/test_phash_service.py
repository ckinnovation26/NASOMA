"""Tests pHash — détection d'images similaires."""

from __future__ import annotations

import io

import pytest
from PIL import Image

from app.services.phash_service import compute_phash, hamming_distance


def _make_image_bytes(size=(64, 64), color=(255, 255, 255)) -> bytes:
    img = Image.new("RGB", size, color)
    buf = io.BytesIO()
    img.save(buf, format="JPEG", quality=90)
    return buf.getvalue()


def test_identical_images_have_same_phash() -> None:
    bytes_1 = _make_image_bytes()
    bytes_2 = _make_image_bytes()
    assert compute_phash(bytes_1) == compute_phash(bytes_2)


def test_different_images_have_different_phash() -> None:
    bytes_white = _make_image_bytes(color=(255, 255, 255))
    bytes_black = _make_image_bytes(color=(0, 0, 0))
    distance = hamming_distance(
        compute_phash(bytes_white),
        compute_phash(bytes_black),
    )
    assert distance > 5


def test_phash_length_64_bits() -> None:
    """pHash format hex 16 chars = 64 bits."""
    h = compute_phash(_make_image_bytes())
    assert len(h) == 16


def test_hamming_distance_same_hash_zero() -> None:
    h = "abcd1234ef567890"
    assert hamming_distance(h, h) == 0


def test_hamming_distance_different_length_returns_max() -> None:
    assert hamming_distance("abc", "abcd") == 64
