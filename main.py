import json
import pathlib

from processor import HuntingExam, process_pdf

import genanki
from dotenv import load_dotenv

ANKI_FILE = "anki/jaegerpruefung_jagdwaffen.apkg"
ANKI_DECK_NAME = "Jägerprüfung::Jagdwaffen"
ANKI_DECK_DESCRIPTION = (
    "Fragen Stand Juli 2022 Fachgebiet 2: "
    '"Jagdwaffen und Fanggeräte" '
    "für die Jägerprüfung Niedersachsen"
)
JSON_FILE = "json/jagdwaffen_3.json"
INPUT_FILE = "assets/jagdwaffen.pdf"
FIRST_PAGE = 45
LAST_PAGE = 61


def generate_flashcards(data: HuntingExam):
    template_dir = "templates/"
    with open(f"{template_dir}afmt.html", encoding="utf-8") as file:
        afmt = file.read()
    with open(f"{template_dir}qfmt.html", encoding="utf-8") as file:
        qfmt = file.read()
    with open(f"{template_dir}style.css", encoding="utf-8") as file:
        style = file.read()
    MODEL_ID = 1566095810
    DECK_ID = 1996064686
    model = genanki.Model(
        MODEL_ID,
        "Mulitple Choice",
        fields=[
            {"name": "Question"},
            {"name": "Title"},
            {"name": "QType (0=kprim,1=mc,2=sc)"},
            {"name": "Q_1"},
            {"name": "Q_2"},
            {"name": "Q_3"},
            {"name": "Q_4"},
            {"name": "Q_5"},
            {"name": "Q_6"},
            {"name": "Answers"},
            {"name": "Sources"},
            {"name": "Extra 1"},
        ],
        templates=[{"name": "AllInOne", "qfmt": f"{qfmt}", "afmt": f"{afmt}"}],
        css=f"{style}",
    )
    my_deck = genanki.Deck(
        DECK_ID,
        ANKI_DECK_NAME,
        description=ANKI_DECK_DESCRIPTION,
    )
    for q in data.questions:
        answers = []
        correct = ""
        for a in q.answers:
            answers.append(a.text)
            if a.correct:
                correct += "1 "
            else:
                correct += "0 "
        while len(answers) < 6:
            answers.append("")
        answers.append(correct.strip())
        fields = [f"{q.question}", f"{q.number}", "1"]
        fields.extend(answers)
        fields.extend(["", ""])
        my_deck.add_note(
            genanki.Note(
                model=model,
                fields=fields,
            )
        )
    pathlib.Path(ANKI_FILE).parent.mkdir(parents=True, exist_ok=True)
    genanki.Package(my_deck).write_to_file(ANKI_FILE)


def main():
    load_dotenv("./keys.env")
    exam = process_pdf(INPUT_FILE, FIRST_PAGE)
    try:
        for i in range(FIRST_PAGE + 1, LAST_PAGE + 1):
            exam.questions.extend(process_pdf(INPUT_FILE, f"{i}").questions)
    finally:
        pathlib.Path(JSON_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(JSON_FILE, "w", encoding="utf-8") as file:
            json.dump(exam.model_dump(), file, indent=2, ensure_ascii=False)
    # generate_flashcards(exam)


if __name__ == "__main__":
    main()
