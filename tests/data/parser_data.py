import argparse

from rhasspyhermes.intent import Intent, Slot
from rhasspyhermes.nlu import NluIntent

rhasspy_intent = {
        "request_weather_full_day": '{"entities": [{"end": 25, "entity": "when_day", "raw_end": 25, "raw_start": 20, "raw_value": "heute", '
                                    '"start": 20, "value": "heute", "value_details": {"kind": "Unknown", "value": "heute"}}], '
                                    '"intent": {"confidence": 1, "name": "GetWeatherForecast"}, "raw_text": "wie wird das wetter heute", '
                                    '"raw_tokens": ["wie", "wird", "das", "wetter", "heute"], "recognize_seconds": 0.16436054417863488, '
                                    '"slots": {"when_day": "heute"}, "speech_confidence": 1, "text": "wie wird das wetter heute", '
                                    '"tokens": ["wie", "wird", "das", "wetter", "heute"], "wakeword_id": null}',
        "request_weather_full_time": '{"entities": [{"end": 25, "entity": "when_day", "raw_end": 25, "raw_start": 20, "raw_value": "heute", '
                                     '"start": 20, "value": "heute", "value_details": {"kind": "Unknown", "value": "heute"}}, '
                                     '{"end": 28, "entity": "when_time", "raw_end": 37, "raw_start": 26, "raw_value": "um zehn uhr", "start": 26, '
                                     '"value": 10, "value_details": {"kind": "Number", "value": 10}}], '
                                     '"intent": {"confidence": 1, "name": "GetWeatherForecast"}, '
                                     '"raw_text": "wie wird das wetter heute um 10 uhr", '
                                     '"raw_tokens": ["wie", "wird", "das", "wetter", "heute", "um", "10", "uhr"], '
                                     '"recognize_seconds": 0.17279156856238842, "slots": {"when_day": "heute", "when_time": 10}, '
                                     '"speech_confidence": 1, "text": "wie wird das wetter heute 10", '
                                     '"tokens": ["wie", "wird", "das", "wetter", "heute", "10"], "wakeword_id": null}',
        "request_weather_full_interval": '{"entities": [{"end": 25, "entity": "when_day", "raw_end": 25, "raw_start": 20, "raw_value": "heute", '
                                         '"start": 20, "value": "heute", "value_details": {"kind": "Unknown", "value": "heute"}}, {"end": 32, '
                                         '"entity": "when_time", "raw_end": 32, "raw_start": 26, "raw_value": "mittag", "start": 26, '
                                         '"value": "Mittag", "value_details": {"kind": "Unknown", "value": "Mittag"}}], '
                                         '"intent": {"confidence": 1, "name": "GetWeatherForecast"}, "raw_text": "wie wird das wetter heute mittag", '
                                         '"raw_tokens": ["wie", "wird", "das", "wetter", "heute", "mittag"], "recognize_seconds": 0.11356039298698306, '
                                         '"slots": {"when_day": "heute", "when_time": "Mittag"}, "speech_confidence": 1, '
                                         '"text": "wie wird das wetter heute Mittag", "tokens": ["wie", "wird", "das", "wetter", "heute", "Mittag"], '
                                         '"wakeword_id": null}'
    }

day_slot = Slot(entity="test", slot_name="when_day", value={"value": "heute"}, raw_value="heute")
nlu_intent = {
        "request_weather_full_day": NluIntent("Wie wird das Wetter heute?", Intent("GetWeatherForecastFull", 1), slots=[day_slot]),
        "request_weather_full_time": NluIntent("Wie wird das Wetter heute um 10 Uhr?", Intent("GetWeatherForecastFull", 1), slots=[day_slot, Slot(entity="test", slot_name="when_time", value={"value": 10}, raw_value="zehn")]),
        "request_weather_full_interval": NluIntent("Wie wird das Wetter heute mittag?", Intent("GetWeatherForecastFull", 1), slots=[day_slot, Slot(entity="test", slot_name="when_time", value={"value": "mittag"}, raw_value="mittag")])
    }
console_args = {
        "request_weather_full_day": argparse.ArgumentParser("-d", "heute", "-t", "mittag"),
        "request_weather_full_time": argparse.ArgumentParser("-d", "heute", "-t", "10"),
        "request_weather_full_interval": argparse.ArgumentParser("-d", "heute", "-t", "mittag")
    }
intents = {
    "rhasspy_intent": rhasspy_intent,
    "nlu_intent": nlu_intent,
    "console_args": console_args
    }

