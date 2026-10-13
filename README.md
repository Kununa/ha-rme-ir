# RME Infrared for Home Assistant

Control RME ADI-2 series converters from Home Assistant over infrared. You need an IR transmitter that Home Assistant exposes as an `infrared` entity, such as an ESPHome IR proxy.

The integration sends the official NEC codes that RME publishes for its remotes. That includes the extended codes for programmable remotes, such as the DAC filters, Crossfeed, the Setup slots and direct input selection.

## Supported devices

| Model in setup | Covers | Inputs in the media player | Tested on hardware |
|---|---|---|---|
| ADI-2 DAC / DAC FS | ADI-2 DAC, ADI-2 DAC FS | Coaxial, Optical, USB | Yes |
| ADI-2 Pro FS / Pro FS R | ADI-2 Pro FS, ADI-2 Pro FS R (Black Edition) | AES, S/PDIF coaxial, Optical, Analog, USB | No |

The code tables come from RME's downloads:
[ADI-2 DAC](https://archiv.rme-audio.de/download/adi2dac_ir_commands.zip) and
[ADI-2 Pro](https://archiv.rme-audio.de/download/adi2pro_ir_commands.zip).
RME publishes no table for the ADI-2/4 Pro SE or the ADI-2 Pro EX, so they aren't listed yet.

## Requirements

- Home Assistant with the `infrared` integration. This integration is developed and tested on 2026.10.1.
- An infrared emitter entity, from ESPHome's [`ir_rf_proxy`](https://esphome.io/components/ir_rf_proxy/) or another integration that provides one.
- A line of sight from the IR LED to the front panel of the RME device.

## Installation

### HACS

1. In HACS, open the menu and choose **Custom repositories**. Add this repository as an **Integration**.
2. Install **RME Infrared**, then restart Home Assistant.

### Manual

1. Copy `custom_components/rme_infrared` to `/config/custom_components/rme_infrared` on your Home Assistant host.
2. Restart Home Assistant.

## Setup

Go to **Settings → Devices & services → Add integration → RME Infrared** and choose:

- **Model**: the code table that matches your device.
- **IR transmitter**: the infrared emitter pointing at the device.
- **NEC address (hex)**: leave this at `3412`.

RME documents the remote ID as `1234`. The NEC address bytes are sent low byte first, so that ID becomes `3412` in Home Assistant's NEC encoder. This was verified on an ADI-2 DAC FS.

You can add each model once per transmitter.

## Entities

**Media player** (for example `media_player.rme_adi_2_dac`):

| Action | Code sent |
|---|---|
| Turn on | Power (a toggle) |
| Turn off | Discrete *Power Off* |
| Volume up / down | Volume + / − |
| Mute | Mute (a toggle) |
| Select source | The model's input codes |

**Buttons:** one for every other code. This covers Power toggle, Remap 1–4, Bass/Treble/EQ/Loudness on/off, VOL push, Bass ±, Treble ±, Balance L/R, Setup 1–9, Mono, Mono to left, Mute all, EQ + B/T + LD, Toggle phones/line, Polarity, AutoDark, Dim, Toggle view, Crossfeed 1–5 and the six DAC filters. The ADI-2 Pro also gets SEL and Remap 5–7, because the COAX, OPT and USB keys on its remote are remap keys.

### Limitations

Infrared is one-way, so every state the integration shows is **assumed**:

- **Power state:** the media player's state is whatever was last sent. A change made on the device's front panel or with the original remote won't appear in Home Assistant.
- **Turn on toggles:** *Turn on* sends the Power toggle. If the device is already on, it switches off. *Turn off* is a discrete command, so it's always safe to send.
- **Mute toggles:** there's no separate mute-on or mute-off code.

## Building an IR proxy

Almost any ESP board with an IR LED works. Here is a minimal ESPHome config for a Wemos D1 mini with the LED on D2:

```yaml
esp8266:
  board: d1_mini

remote_transmitter:
  id: ir_tx
  pin: D2
  carrier_duty_percent: 50%

infrared:
  - platform: ir_rf_proxy
    name: IR Proxy Transmitter
    remote_transmitter_id: ir_tx
```

Add your usual `wifi`, `api` and `ota` blocks. An LED wired straight to a GPIO pin reaches about 1–2 m. Drive it through a transistor if you need room-sized range.

## Development

Home Assistant doesn't run on Windows, so the tests run in a Linux container:

```sh
docker build -f Dockerfile.test -t rme-infrared-test .
docker run --rm -v "${PWD}:/src:ro" rme-infrared-test
```

On Linux or macOS you can also run them directly:

```sh
pip install -r requirements_test.txt
pytest
```

### Adding a model

1. Add an `RmeModel` entry to `MODELS` in [`const.py`](custom_components/rme_infrared/const.py), with its code table and input codes. If the device has a function no existing model has, add an `RmeKey` and a `KEY_NAMES` entry for it.
2. Extend the tests in [`tests/`](tests/), particularly `test_const.py`. Base expected codes on RME's published table, not on the implementation.

The brand images in `custom_components/rme_infrared/brand/` are generated from [`brand-src/rme-logo.svg`](brand-src/rme-logo.svg) with [`brand-src/make_brand.py`](brand-src/make_brand.py).

## Disclaimer

This is an unofficial project and isn't affiliated with or endorsed by RME. *RME* and the RME logo are trademarks of RME Audio AG / Audio AG.
