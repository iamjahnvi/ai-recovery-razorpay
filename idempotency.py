import json


FILE_NAME = "processed_events.json"


def load_processed_events():
    try:
        with open(FILE_NAME, "r") as file:
            return json.load(file)
    except (FileNotFoundError, json.JSONDecodeError):
        return []


def is_processed(event_id):
    processed_events = load_processed_events()
    return event_id in processed_events


def mark_processed(event_id):
    processed_events = load_processed_events()

    if event_id not in processed_events:
        processed_events.append(event_id)

    with open(FILE_NAME, "w") as file:
        json.dump(processed_events, file, indent=4)