import json
import pathlib

from dotenv import load_dotenv

from processor import HuntingExam, process_pdf

ANKI_FILE = "anki/jaegerpruefung_jagdwaffen.apkg"
ANKI_DECK_NAME = "Jägerprüfung::Jagdwaffen"
ANKI_DECK_DESCRIPTION = (
    "Fragen Stand Juli 2022 Fachgebiet 2: "
    '"Jagdwaffen und Fanggeräte" '
    "für die Jägerprüfung Niedersachsen"
)
JSON_FILE = "json/jagdwaffen_3.json"
INPUT_FILE = "assets/jagdwaffen.pdf"
FIRST_PAGE = 1
LAST_PAGE = 61


def main():
    load_dotenv("./keys.env")
    exam = HuntingExam(**{"questions": []})
    try:
        for i in range(FIRST_PAGE, LAST_PAGE + 1):
            exam.questions.extend(process_pdf(INPUT_FILE, f"{i}").questions)
    finally:
        pathlib.Path(JSON_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(JSON_FILE, "w", encoding="utf-8") as file:
            json.dump(exam.model_dump(), file, indent=2, ensure_ascii=False)


if __name__ == "__main__":
    main()
