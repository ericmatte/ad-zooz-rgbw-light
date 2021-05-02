ad-zooz-rgbw-light

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