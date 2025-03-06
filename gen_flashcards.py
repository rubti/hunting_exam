import json

from processor import HuntingExam, generate_flashcards

TIERE_DECK_ID = 1996064686
JAGDWAFFEN_DECK_ID = 1124361525
NATURSCHUTZ_DECK_ID = 1197899700
BRAUCHTUM_DECK_ID = 1125307580
RECHT_DECK_ID = 1679226623

ANKI_FILE = "anki/jaegerpruefung_naturschutz.apkg"
ANKI_DECK_NAME = "Jägerprüfung::Naturschutz"
ANKI_DECK_DESCRIPTION = (
    "Fragen Stand Juli 2022 Fachgebiet 3: "
    '"Naturschutz, Hege und Jagdbetrieb" '
    "für die Jägerprüfung Niedersachsen"
)
JSON_FILE = "json/naturschutz.json"

if __name__ == "__main__":
    with open(JSON_FILE, encoding="utf-8") as file:
        data = HuntingExam(**json.load(file))
    generate_flashcards(
        data, ANKI_DECK_NAME, NATURSCHUTZ_DECK_ID, ANKI_FILE, ANKI_DECK_DESCRIPTION
    )
