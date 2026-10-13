"""Tests for the RME IR code tables."""

import pytest

from custom_components.rme_infrared.const import KEY_NAMES, MODELS, RmeKey


def test_every_key_has_a_name() -> None:
    """Every function has a display name for its button."""
    assert set(KEY_NAMES) == set(RmeKey)


@pytest.mark.parametrize("model_key", list(MODELS))
def test_codes_are_unique_bytes(model_key: str) -> None:
    """Within a model, every key and source maps to a distinct 8-bit code."""
    model = MODELS[model_key]
    codes = [*model.codes.values(), *model.sources.values()]
    assert all(0 <= code <= 0xFF for code in codes)
    assert len(codes) == len(set(codes))


def test_table_sizes_match_rme_lists() -> None:
    """RME lists 51 codes for the ADI-2 DAC and 57 for the ADI-2 Pro."""
    for key, expected in (("adi2_dac", 51), ("adi2_pro", 57)):
        model = MODELS[key]
        assert len(model.codes) + len(model.sources) == expected


def test_pro_is_dac_with_bit7_set() -> None:
    """Every function both models share is the DAC code with bit 7 set."""
    dac, pro = MODELS["adi2_dac"].codes, MODELS["adi2_pro"].codes
    assert set(dac) <= set(pro)
    for key, code in dac.items():
        assert pro[key] == code | 0x80, key


@pytest.mark.parametrize(
    ("model_key", "key", "code"),
    [
        # Spot checks against RME's published tables.
        ("adi2_dac", RmeKey.POWER_TOGGLE, 0x20),
        ("adi2_dac", RmeKey.POWER_OFF, 0x14),
        ("adi2_dac", RmeKey.MUTE, 0x2A),
        ("adi2_dac", RmeKey.SETUP_7, 0x3C),  # corrected typo in RME's list
        ("adi2_dac", RmeKey.MONO, 0x00),
        ("adi2_dac", RmeKey.DAC_SD_LD, 0x13),
        ("adi2_pro", RmeKey.POWER_TOGGLE, 0xA0),
        ("adi2_pro", RmeKey.REMAP_5, 0xA3),
        ("adi2_pro", RmeKey.SEL, 0xB5),
        ("adi2_pro", RmeKey.DAC_SD_LD, 0x93),
    ],
)
def test_known_codes(model_key: str, key: RmeKey, code: int) -> None:
    """Selected codes match RME's documentation."""
    assert MODELS[model_key].codes[key] == code


def test_sources() -> None:
    """Each model exposes its own input codes."""
    assert MODELS["adi2_dac"].sources == {"Coaxial": 0x23, "Optical": 0x24, "USB": 0x25}
    assert MODELS["adi2_pro"].sources == {
        "AES": 0x95,
        "S/PDIF coaxial": 0x96,
        "Optical": 0x97,
        "Analog": 0x98,
        "USB": 0x99,
    }


def test_dac_has_no_pro_only_keys() -> None:
    """The DAC's COAX/OPT/USB keys select inputs, so it has no remap 5-7 or SEL."""
    dac = MODELS["adi2_dac"].codes
    for key in (RmeKey.REMAP_5, RmeKey.REMAP_6, RmeKey.REMAP_7, RmeKey.SEL):
        assert key not in dac
