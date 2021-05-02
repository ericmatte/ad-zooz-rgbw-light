import appdaemon.plugins.hass.hassapi as hass
import mqttapi as mqtt
import json


class ZoozRGBWLight(mqtt.Mqtt, hass.Hass):
    def initialize(self):
        self.mqtt = self.get_app('zooz_rgbw_light_mqtt')

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

        command_topic = "zooz/{id}/cmd".format(id=self.unique_id)
        self.state_topic = "zooz/{id}/state".format(id=self.unique_id)
        light_attributes = {
            "schema": "json",
            "name": self.light_name,
            "unique_id": self.unique_id,
            "icon": "mdi:led-strip-variant",
            "command_topic": command_topic,
            "state_topic": self.state_topic,
            "brightness": True,
            "rgb": True,
            "white_value": True,
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
        
        light_config_topic = "homeassistant/light/{id}/config".format(id=self.unique_id)
        self.mqtt_publish(light_config_topic, payload=json.dumps(light_attributes))
        # self.call_service("mqtt/publish", topic=light_config_topic, payload=json.dumps(light_attributes))

        self.listen_event(self.command_new_state, event="call_service", topic=command_topic, domain="mqtt", service="publish")
        for entity in self.dimmer_entities:
            self.listen_state(self.state_changed, entity, attribute="all")
        self.log("Script initialized.")

    def command_new_state(self, event_name, data, kwargs):
        # self.log("command_new_state, payload={}".format(data["service_data"]["payload"]))
        payload = json.loads(data["service_data"]["payload"])
        if payload["state"] == "ON":
            effect = payload.get("effect", None)
            if effect is not None:
                self.set_effect(effect)
            else:
                self.turn_on(payload)
        else:
            self.turn_off()

    def state_changed(self, entity, attribute, old, new, kwargs):
        if self.get_state(self.dimmer_main) == "on":
            states = self.get_current_states()
            attributes = {
                "state": "ON",
                "brightness": states["main"],
                "rgb_color": "{},{},{}".format(states["r"], states["g"], states["b"]),
                "white_value": states["w"]
            }
        else:
            attributes = {"state": "OFF"}
        self.log("state_changed={}".format(attributes))
        self.mqtt_publish(self.state_topic, payload=json.dumps(attributes))


    def set_effect(self, effect):
        value = effect.lower() if effect != "Disabled" else "preset programs disabled"
        self.log("set_effect({})".format(value))
        self.call_service("zwave_js/set_config_parameter", entity_id=self.dimmer_main, parameter="157", value=value)

    def get_current_states(self):
        return {
            "main": self.get_state(self.dimmer_main, attribute="brightness") or 0,
            "r": self.get_state(self.dimmer_r, attribute="brightness") or 0,
            "g": self.get_state(self.dimmer_g, attribute="brightness") or 0,
            "b": self.get_state(self.dimmer_b, attribute="brightness") or 0,
            "w": self.get_state(self.dimmer_w, attribute="brightness") or 0,
        }

    def turn_on(self, payload):
        self.log("turn_on")
        states = self.get_current_states()

        self.log("{entity_id}/{brightness}".format(entity_id=self.dimmer_main, brightness=payload.get("brightness", states["main"])))
        self.log("{entity_id}/{brightness}".format(entity_id=self.dimmer_r, brightness=payload.get("color", states)["r"]))
        self.log("{entity_id}/{brightness}".format(entity_id=self.dimmer_g, brightness=payload.get("color", states)["g"]))
        self.log("{entity_id}/{brightness}".format(entity_id=self.dimmer_b, brightness=payload.get("color", states)["b"]))
        self.log("{entity_id}/{brightness}".format(entity_id=self.dimmer_w, brightness=payload.get("white_value", states["w"])))

        self.call_service("light/turn_on", entity_id=self.dimmer_main, brightness=payload.get("brightness", states["main"]))
        self.call_service("light/turn_on", entity_id=self.dimmer_r, brightness=payload.get("color", states)["r"])
        self.call_service("light/turn_on", entity_id=self.dimmer_g, brightness=payload.get("color", states)["g"])
        self.call_service("light/turn_on", entity_id=self.dimmer_b, brightness=payload.get("color", states)["b"])
        self.call_service("light/turn_on", entity_id=self.dimmer_w, brightness=payload.get("white_value", states["w"]))

    def turn_off(self):
        self.log("turn_off")
        self.call_service("light/turn_off", entity_id=self.dimmer_entities)
