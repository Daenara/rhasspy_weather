import json


def output_response(response, intent_message):
    intent_message["speech"] = {"text": response}
    print(json.dumps(intent_message))
