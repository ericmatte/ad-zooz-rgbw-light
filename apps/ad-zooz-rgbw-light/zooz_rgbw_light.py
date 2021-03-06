import appdaemon.plugins.hass.hassapi as hass
import json

from threading import Thread


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

        light_attributes = {
            "schema": "json",
            "name": self.light_name,
            "unique_id": self.unique_id,
            "icon": "mdi:led-strip-variant",
            "command_topic": "zooz/{id}/cmd".format(id=self.unique_id),
            "brightness": True,
            "color_mode": True,
            "supported_color_modes": ["rgbw"],
            "effect": True,
            "effect_list": [
                "Disabled",
                "Fireplace",
                "Storm",
                "Rainbow",
                "Polar Lights",
                "Police"
            ]
        }

        # Create/Update light using mqtt discovery
        light_config_topic = "homeassistant/light/{id}/config".format(id=self.unique_id)
        self.call_service("mqtt/publish", topic=light_config_topic, payload=json.dumps(light_attributes))

        self.listen_state(self.state_changed, self.entity_id, attribute="all")
        self.log("'{}' initialized.".format(self.entity_id))

    def state_changed(self, entity, attribute, old, new, kwargs):
        self.log("'{}' state changed.".format(self.entity_id))
        if new["state"] == 'on':
            effect = new['attributes'].get("effect", "Disabled")
            if old['state'] == 'on' and effect != old['attributes'].get("effect", "Disabled"):
                self.set_effect(effect)
            else:
                self.turn_on(new['attributes'])
        else:
            self.turn_off()

    def set_effect(self, effect):
        self.log("Setting effect: {}".format(effect))
        value = effect.lower() if effect != "Disabled" else "preset programs disabled"
        self.call_service("zwave_js/set_config_parameter", entity_id=self.dimmer_main, parameter="157", value=value)

    def turn_on(self, attributes):
        state = {
            "brightness": attributes.get("brightness", 255),
            "rgbw": attributes.get("rgbw_color", [0, 0, 0, 255]),
        }
        self.log("Turning on with {}".format(state))
        self.turn_on_in_thread(self.dimmer_main, state["brightness"])
        self.turn_on_in_thread(self.dimmer_r, state["rgbw"][0])
        self.turn_on_in_thread(self.dimmer_g, state["rgbw"][1])
        self.turn_on_in_thread(self.dimmer_b, state["rgbw"][2])
        self.turn_on_in_thread(self.dimmer_w, state["rgbw"][3])

    def turn_on_in_thread(self, entity, brightness):
        Thread(target=self.call_service, args=["light/turn_on"], kwargs={"entity_id": entity, "brightness": brightness}).start()

    def turn_off(self):
        self.log("Turning off")
        self.call_service("light/turn_off", entity_id=self.dimmer_entities)
