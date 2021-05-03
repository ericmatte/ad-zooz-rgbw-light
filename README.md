# Zooz RGBW Light

_Simple AppDaemon App to fix Zooz ZEN31 RGBW dimmer light in Home Assistant with Z-Wave JS._

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg?style=for-the-badge)](https://github.com/custom-components/hacs)

## Explanation

As of May 3rd 2021, the Zooz ZEN31 RGBW dimmer controller does not create one single entity in Home Assistant with Z-Wave JS that can control all the whole RGBW at once.

The controller outputs five lights entities:

| Entity                | Control on/off and brightness of |
| --------------------- | -------------------------------- |
| `light.rgbw_dimmer`   | global                           |
| `light.rgbw_dimmer_2` | red channel                      |
| `light.rgbw_dimmer_3` | green channel                    |
| `light.rgbw_dimmer_4` | blue channel                     |
| `light.rgbw_dimmer_5` | white channel                    |

This small AppDaemon creates and control an optimist [MQTT RGBW light](https://www.home-assistant.io/integrations/light.mqtt/) that can control all channel into a single entity.
The light is automatically added to Home Assistant using [MQTT discovery](https://www.home-assistant.io/docs/mqtt/discovery).

It supports all effects provided by the ZEN31 controller:

- Disabled
- Fireplace
- Storm
- Rainbow
- Polar Lights
- Police

It also can be used with multiple Zooz ZEN31 controllers by adding a configuration for each controllers.

## Installation

### Using [HACS](https://hacs.xyz/)

- In HACS, select `Custom repositories`
- Enter the url of this repository: `https://github.com/ericmatte/ad-zooz-rgbw-light`
- Select category `AppDaemon` and click <kbd>Add</kbd>

### Manual installation

- Download the `ad-zooz-rgbw-light` directory from inside the `apps` directory here to your local `apps` directory
- Then add the configuration to enable the `zooz_rgbw_light` module.

## App configuration

`config/appdaemon/apps/apps.yaml`

```yaml
zooz_rgbw_light:
  module: zooz_rgbw_light
  class: ZoozRGBWLight
  light_name: "Under bed"
  unique_id: under_bed
  zooz_entities:
    main: light.rgbw_dimmer
    r: light.rgbw_dimmer_r
    g: light.rgbw_dimmer_g
    b: light.rgbw_dimmer_b
    w: light.rgbw_dimmer_w
```
