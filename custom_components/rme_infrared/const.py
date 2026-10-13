"""Constants and IR code tables for the RME infrared integration.

Code tables come from RME's published lists:
https://archiv.rme-audio.de/download/adi2dac_ir_commands.zip
https://archiv.rme-audio.de/download/adi2pro_ir_commands.zip
"""

from dataclasses import dataclass
from enum import StrEnum

DOMAIN = "rme_infrared"
CONF_INFRARED_ENTITY_ID = "infrared_entity_id"
CONF_MODEL = "model"
CONF_ADDRESS = "address"

# RME documents the remote "ID" as 1234 (hex), NEC protocol. The bytes go out
# as 0x12 then 0x34, which is extended-NEC address 0x3412 (verified on device).
DEFAULT_ADDRESS = "3412"


class RmeKey(StrEnum):
    """Functions an RME remote code can trigger."""

    POWER_TOGGLE = "power_toggle"
    POWER_OFF = "power_off"
    VOLUME_DOWN = "volume_down"
    VOLUME_UP = "volume_up"
    MUTE = "mute"
    REMAP_1 = "remap_1"
    REMAP_2 = "remap_2"
    REMAP_3 = "remap_3"
    REMAP_4 = "remap_4"
    REMAP_5 = "remap_5"
    REMAP_6 = "remap_6"
    REMAP_7 = "remap_7"
    BASS_TREBLE = "bass_treble"
    EQ = "eq"
    LOUDNESS = "loudness"
    VOL_PUSH = "vol_push"
    SEL = "sel"
    BASS_UP = "bass_up"
    BASS_DOWN = "bass_down"
    TREBLE_UP = "treble_up"
    TREBLE_DOWN = "treble_down"
    BALANCE_LEFT = "balance_left"
    BALANCE_RIGHT = "balance_right"
    SETUP_1 = "setup_1"
    SETUP_2 = "setup_2"
    SETUP_3 = "setup_3"
    SETUP_4 = "setup_4"
    SETUP_5 = "setup_5"
    SETUP_6 = "setup_6"
    SETUP_7 = "setup_7"
    SETUP_8 = "setup_8"
    SETUP_9 = "setup_9"
    MONO = "mono"
    MONO_TO_LEFT = "mono_to_left"
    MUTE_ALL = "mute_all"
    EQ_BT_LD = "eq_bt_ld"
    TOGGLE_PHONES_LINE = "toggle_phones_line"
    POLARITY = "polarity"
    AUTO_DARK = "auto_dark"
    DIM = "dim"
    TOGGLE_VIEW = "toggle_view"
    CROSSFEED_1 = "crossfeed_1"
    CROSSFEED_2 = "crossfeed_2"
    CROSSFEED_3 = "crossfeed_3"
    CROSSFEED_4 = "crossfeed_4"
    CROSSFEED_5 = "crossfeed_5"
    DAC_SD_SHARP = "dac_sd_sharp"
    DAC_SD_SLOW = "dac_sd_slow"
    DAC_SHARP = "dac_sharp"
    DAC_SLOW = "dac_slow"
    DAC_NOS = "dac_nos"
    DAC_SD_LD = "dac_sd_ld"


KEY_NAMES: dict[RmeKey, str] = {
    RmeKey.POWER_TOGGLE: "Power toggle",
    RmeKey.POWER_OFF: "Power off",
    RmeKey.VOLUME_DOWN: "Volume down",
    RmeKey.VOLUME_UP: "Volume up",
    RmeKey.MUTE: "Mute",
    RmeKey.REMAP_1: "Remap 1",
    RmeKey.REMAP_2: "Remap 2",
    RmeKey.REMAP_3: "Remap 3",
    RmeKey.REMAP_4: "Remap 4",
    RmeKey.REMAP_5: "Remap 5 (COAX key)",
    RmeKey.REMAP_6: "Remap 6 (OPT key)",
    RmeKey.REMAP_7: "Remap 7 (USB key)",
    RmeKey.BASS_TREBLE: "Bass/Treble on/off",
    RmeKey.EQ: "EQ on/off",
    RmeKey.LOUDNESS: "Loudness on/off",
    RmeKey.VOL_PUSH: "VOL push (select)",
    RmeKey.SEL: "SEL",
    RmeKey.BASS_UP: "Bass up",
    RmeKey.BASS_DOWN: "Bass down",
    RmeKey.TREBLE_UP: "Treble up",
    RmeKey.TREBLE_DOWN: "Treble down",
    RmeKey.BALANCE_LEFT: "Balance left",
    RmeKey.BALANCE_RIGHT: "Balance right",
    RmeKey.SETUP_1: "Setup 1",
    RmeKey.SETUP_2: "Setup 2",
    RmeKey.SETUP_3: "Setup 3",
    RmeKey.SETUP_4: "Setup 4",
    RmeKey.SETUP_5: "Setup 5",
    RmeKey.SETUP_6: "Setup 6",
    RmeKey.SETUP_7: "Setup 7",
    RmeKey.SETUP_8: "Setup 8",
    RmeKey.SETUP_9: "Setup 9",
    RmeKey.MONO: "Mono",
    RmeKey.MONO_TO_LEFT: "Mono to left",
    RmeKey.MUTE_ALL: "Mute all",
    RmeKey.EQ_BT_LD: "EQ + Bass/Treble + Loudness",
    RmeKey.TOGGLE_PHONES_LINE: "Toggle phones/line",
    RmeKey.POLARITY: "Polarity",
    RmeKey.AUTO_DARK: "AutoDark",
    RmeKey.DIM: "Dim",
    RmeKey.TOGGLE_VIEW: "Toggle view",
    RmeKey.CROSSFEED_1: "Crossfeed 1",
    RmeKey.CROSSFEED_2: "Crossfeed 2",
    RmeKey.CROSSFEED_3: "Crossfeed 3",
    RmeKey.CROSSFEED_4: "Crossfeed 4",
    RmeKey.CROSSFEED_5: "Crossfeed 5",
    RmeKey.DAC_SD_SHARP: "DAC filter SD Sharp",
    RmeKey.DAC_SD_SLOW: "DAC filter SD Slow",
    RmeKey.DAC_SHARP: "DAC filter Sharp",
    RmeKey.DAC_SLOW: "DAC filter Slow",
    RmeKey.DAC_NOS: "DAC filter NOS",
    RmeKey.DAC_SD_LD: "DAC filter SD LD",
}

# Codes shared by the ADI-2 DAC and ADI-2 Pro, as listed for the DAC.
_ADI2_COMMON: dict[RmeKey, int] = {
    RmeKey.POWER_TOGGLE: 0x20,
    RmeKey.POWER_OFF: 0x14,
    RmeKey.VOLUME_DOWN: 0x21,
    RmeKey.VOLUME_UP: 0x22,
    RmeKey.REMAP_1: 0x26,
    RmeKey.REMAP_2: 0x27,
    RmeKey.REMAP_3: 0x28,
    RmeKey.REMAP_4: 0x29,
    RmeKey.MUTE: 0x2A,
    RmeKey.BASS_TREBLE: 0x2B,
    RmeKey.EQ: 0x2C,
    RmeKey.LOUDNESS: 0x2D,
    RmeKey.VOL_PUSH: 0x2E,
    RmeKey.BASS_UP: 0x2F,
    RmeKey.BASS_DOWN: 0x30,
    RmeKey.TREBLE_UP: 0x31,
    RmeKey.TREBLE_DOWN: 0x32,
    RmeKey.BALANCE_LEFT: 0x33,
    RmeKey.BALANCE_RIGHT: 0x34,
    RmeKey.SETUP_1: 0x36,
    RmeKey.SETUP_2: 0x37,
    RmeKey.SETUP_3: 0x38,
    RmeKey.SETUP_4: 0x39,
    RmeKey.SETUP_5: 0x3A,
    RmeKey.SETUP_6: 0x3B,
    RmeKey.SETUP_7: 0x3C,
    RmeKey.SETUP_8: 0x3D,
    RmeKey.SETUP_9: 0x3E,
    RmeKey.MONO: 0x00,
    RmeKey.MONO_TO_LEFT: 0x01,
    RmeKey.MUTE_ALL: 0x02,
    RmeKey.EQ_BT_LD: 0x03,
    RmeKey.TOGGLE_PHONES_LINE: 0x04,
    RmeKey.POLARITY: 0x05,
    RmeKey.AUTO_DARK: 0x06,
    RmeKey.DIM: 0x07,
    RmeKey.TOGGLE_VIEW: 0x08,
    RmeKey.CROSSFEED_1: 0x09,
    RmeKey.CROSSFEED_2: 0x0A,
    RmeKey.CROSSFEED_3: 0x0B,
    RmeKey.CROSSFEED_4: 0x0C,
    RmeKey.CROSSFEED_5: 0x0D,
    RmeKey.DAC_SD_SHARP: 0x0E,
    RmeKey.DAC_SD_SLOW: 0x0F,
    RmeKey.DAC_SHARP: 0x10,
    RmeKey.DAC_SLOW: 0x11,
    RmeKey.DAC_NOS: 0x12,
    RmeKey.DAC_SD_LD: 0x13,
}


@dataclass(frozen=True, kw_only=True)
class RmeModel:
    """An RME device family that shares one IR code table."""

    name: str
    codes: dict[RmeKey, int]
    # Source name -> NEC command code, shown in the media player.
    sources: dict[str, int]


MODELS: dict[str, RmeModel] = {
    "adi2_dac": RmeModel(
        name="ADI-2 DAC / DAC FS",
        codes=_ADI2_COMMON,
        sources={"Coaxial": 0x23, "Optical": 0x24, "USB": 0x25},
    ),
    # RME's Pro table is the DAC table with bit 7 set. On the Pro the
    # COAX/OPT/USB keys are remap keys 5-7, and inputs have their own codes.
    "adi2_pro": RmeModel(
        name="ADI-2 Pro FS / Pro FS R",
        codes={key: code | 0x80 for key, code in _ADI2_COMMON.items()}
        | {
            RmeKey.REMAP_5: 0xA3,
            RmeKey.REMAP_6: 0xA4,
            RmeKey.REMAP_7: 0xA5,
            RmeKey.SEL: 0xB5,
        },
        sources={
            "AES": 0x95,
            "S/PDIF coaxial": 0x96,
            "Optical": 0x97,
            "Analog": 0x98,
            "USB": 0x99,
        },
    ),
}
