import appdaemon.plugins.hass.hassapi as hass


class ZoozRGBWLight(hass.Hass):
    def initialize(self):
        args = self.args
        self.light_name = args["light_name"]
        self.unique_id = args["unique_id"]
        self.entity_id = "light.{}".format(self.unique_id)
        self.dimmer_main = args["zooz_entities"]["main"]
        self.dimmer_r = args["zooz_entities"]["r"]
        self.dimmer_g = args["zooz_entities"]["g"]
        self.dimmer_b = args["zooz_entities"]["b"]
        self.dimmer_w = args["zooz_entities"]["w"]
        self.dimmer_entities = [self.dimmer_main, self.dimmer_r, self.dimmer_g, self.dimmer_b, self.dimmer_w]

        self.listen_state(self.state_changed, self.entity_id, attribute="all")
        self.log("Script initialized.")

    def state_changed(self, entity, attribute, old, new, kwargs):
        self.log("{} state changed.".format(self.entity_id))
        if new["state"] == 'on':
            effect = new['attributes'].get("effect", "Disabled")
            if old['state'] == 'on' and effect != old['attributes'].get("effect", "Disabled"):
                self.set_effect(effect)
            else:
                self.turn_on(new['attributes'])
        else:
            self.turn_off()

    def set_effect(self, effect):
        value = effect.lower() if effect != "Disabled" else "preset programs disabled"
        self.log("set_effect({})".format(value))
        self.call_service("zwave_js/set_config_parameter", entity_id=self.dimmer_main, parameter="157", value=value)

    def turn_on(self, attributes):
        self.log("turn_on")
        self.call_service("light/turn_on", entity_id=self.dimmer_main, brightness=attributes["brightness"])
        self.call_service("light/turn_on", entity_id=self.dimmer_r, brightness=attributes["rgb_color"][0])
        self.call_service("light/turn_on", entity_id=self.dimmer_g, brightness=attributes["rgb_color"][1])
        self.call_service("light/turn_on", entity_id=self.dimmer_b, brightness=attributes["rgb_color"][2])
        self.call_service("light/turn_on", entity_id=self.dimmer_w, brightness=attributes.get("white_value", 0))

    def turn_off(self):
        self.log("turn_off")
        self.call_service("light/turn_off", entity_id=self.dimmer_entities)
