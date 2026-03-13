# Philips 3000 Series Fan Heater for Home Assistant

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/homevox-logo-dark.png">
  <source media="(prefers-color-scheme: light)" srcset="assets/homevox-logo-light.png">
  <img alt="HomeVox logo" src="assets/homevox-logo-light.png" width="420">
</picture>

Custom integration for the Philips 3000 Series Fan Heater over the local Air+ CoAP interface.

## Features

- Local polling integration with config flow support
- Climate control for power, target temperature, presets, and oscillation
- Extra entities tailored to the CX3120 instead of a generic multi-model abstraction
- Diagnostics support for easier troubleshooting and issue reports
- HACS metadata included for custom-repository installs

## Installation

### Manual

1. Copy this repository or folder to your Home Assistant `custom_components` directory so the integration lives at:

   ```text
   custom_components/philips_cx3120
   ```

2. Restart Home Assistant.
3. Go to `Settings -> Devices & Services -> Add Integration`.
4. Search for `Philips 3000 Series Fan Heater`.

### HACS

1. Add this repository as a custom repository in HACS with category `Integration`.
2. Install `Philips 3000 Series Fan Heater`.
3. Restart Home Assistant.
4. Add the integration from `Settings -> Devices & Services`.

## Configuration

The config flow asks for:

- `Host`: IP address or hostname of the heater
- `Port`: CoAP port, default `5683`
- `Name`: Optional display name for the device

## Exposed entities

### Climate

- HVAC modes: `off`, `auto`, `heat`, `fan_only`
- Presets: `auto_plus`, `ventilation`, `low`, `medium`, `high`
- Swing mode for oscillation
- Target temperature from `1` to `37` degrees Celsius

### Sensors

- Current Temperature
- Heating Action
- Preset
- Timer
- Remaining Time
- WiFi Signal
- WiFi Version
- Free Memory
- Error Code
- Runtime
- Connect Type

### Binary sensors

- Problem
- Heating
- Auto Plus AI

### Number

- Target Temperature Control

### Selects

- Preset Control
- Timer Control

### Switches

- Child Lock
- Beep

## Notes

- This integration uses the local Philips Air+ CoAP interface via `aioairctrl`.
- The device must be reachable on your local network.
- The integration currently targets the `CX3120` specifically.
- Diagnostics export redacts host and device identifiers.
- The repository export intentionally excludes caches and local machine data.
