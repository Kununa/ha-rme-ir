# CLAUDE.md

A Home Assistant custom integration, `rme_infrared`, that controls RME ADI-2 series devices by sending NEC IR codes through an `infrared` emitter entity, usually an ESPHome `ir_rf_proxy`. See README.md for what users see.

## Layout

- `custom_components/rme_infrared/`: the integration.
  - `const.py`: domain, config keys, `RmeKey` (functions), `KEY_NAMES` (button names), `MODELS` (code tables). Model-specific behaviour belongs here.
  - `entity.py`: `RmeIrEntity`, the base class. It holds the emitter id, the address and the model, and builds `DeviceInfo`. `_send_code(code)` wraps `NECCommand`.
  - `media_player.py`: power, volume step, mute and input selection. The state is assumed.
  - `button.py`: one button per code in the model's table, except the codes in `MEDIA_PLAYER_KEYS`.
  - `config_flow.py`: one user step asking for the model, the emitter and the address in hex.
  - `strings.json` and `translations/en.json`: keep these identical. Edit `en.json`, then copy it over `strings.json`.
  - `brand/`: PNG icons (`icon`, `dark_icon`, each with `@2x`), generated. Don't edit them by hand. There's deliberately no `logo.png`, so Home Assistant falls back to the icon.
- `tests/`: tests built on pytest-homeassistant-custom-component. `conftest.py` provides `MockInfraredEmitterEntity`, which records the commands it is asked to send.
- `brand-src/`: `icon.svg` (original artwork: a simplified half-rack DAC front receiving IR waves) and `make_brand.py`, which renders the light and dark PNGs with headless Edge and Pillow. **Never use RME's own logo or wordmark.** It is copyrighted and was deliberately removed.

## Domain facts

These are verified. Don't "fix" them.

- **The NEC address is `0x3412`.** RME documents the remote ID as `1234`. `NECCommand` sends `address_low` first, so `0x3412` puts `0x12 0x34` on the wire. This was verified on a real ADI-2 DAC FS. `0x1234` doesn't work.
- **The ADI-2 Pro table is the DAC table with bit 7 set**, for every shared function. `MODELS["adi2_pro"]` derives its codes from `_ADI2_COMMON` with `| 0x80`.
- **The COAX, OPT and USB remote keys** select inputs on the DAC (`0x23` to `0x25`). On the Pro the same keys are Remap 5–7 (`0xA3` to `0xA5`), and the Pro selects inputs with its own codes (`0x95` to `0x99`).
- **RME's DAC sheet had a typo for Setup 7:** the correct code is `0x3C`.
- **Power:** "Power On" is really a toggle. "Power Off" is a discrete code. `turn_on` sends the toggle and `turn_off` sends the discrete off.
- **Sources of truth:** RME's code tables are the zip files linked in README.md, each containing an `.ods` file. When you add or change codes, check them against those files, not against memory.

## Home Assistant APIs and conventions

- The pattern mirrors core's `edifier_infrared`. Entities inherit `InfraredEmitterConsumerEntity`, set `_infrared_emitter_entity_id`, and send with `self._send_command(...)`. That base class tracks availability through the emitter's state. Don't call `infrared.async_send_command` directly.
- **Schemas:** the config flow uses `probatio` and falls back to `voluptuous`. Core is migrating to probatio.
- **Unique IDs:**
  - entities: `f"{entry.entry_id}_{suffix}"`, where `suffix` is an `RmeKey` value or `media_player`.
  - config entries: `f"{model}_{emitter_entity_id}"`.
- **Entity names:** buttons take their names from `KEY_NAMES` and don't use translation keys. The device name is `"RME " + model.name.split(" / ")[0]`, which is what entity IDs such as `media_player.rme_adi_2_dac` are built from. Renaming a model's `name` changes users' entity IDs.
- **Brand images:** custom integrations may ship them in `brand/`, supported since HA 2026.3. File names are `icon.png`, `logo.png`, their `dark_` variants and their `@2x` variants.
- **Device registry:** `device_registry.async_get_device` is deprecated and raises in tests. Use `async_entries_for_config_entry` or `async_get_device_by_identifier` instead.

## Testing

Home Assistant imports `fcntl`, so **the tests can't run natively on Windows**. Run them in Docker. If Docker Desktop is stopped, start it first.

```sh
docker build -f Dockerfile.test -t rme-infrared-test .
MSYS_NO_PATHCONV=1 docker run --rm -v "$(pwd -W):/src:ro" rme-infrared-test -q   # Git Bash; PowerShell: -v "${PWD}:/src:ro"
```

- Rebuild the image only when `requirements_test.txt` changes. The source is mounted read-only.
- The version in `requirements_test.txt` follows the Home Assistant version the integration runs on. `pytest-homeassistant-custom-component==X` pins a specific `homeassistant` release, so check PyPI for which one.
- In tests, assert on `mock_emitter.sent_codes()`, a list of `(address, command)` tuples. Look entities up with `entity_id_for(...)` (by unique ID) rather than hard-coding them, except where the test checks the entity ID itself.
- Write expected codes as literals taken from RME's tables, not computed from `const.py`.

## Deploying

The integration is deployed by copying `custom_components/rme_infrared/` into `/config/custom_components/` on the Home Assistant host, then restarting Home Assistant. Python changes need a restart. Exclude `__pycache__`. The host-specific SSH details live in the user's Claude memory, not in this repo.
