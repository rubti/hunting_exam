import json
import pathlib
import sys

import genanki
from dotenv import load_dotenv
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               SystemMessagePromptTemplate)
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from unstract.llmwhisperer.client_v2 import LLMWhispererClientV2

ANKI_FILE = "anki/jaegerpruefung_tiere.apkg"
ANKI_DECK_NAME = "Jägerprüfung::Tiere"
ANKI_DECK_DESCRIPTION = (
    "Fragen Stand Juli 2022 Fachgebiet 1: "
    '"Dem Jagdrecht unterliegende und andere frei lebende Tiere" '
    "für die Jägerprüfung Niedersachsen"
)
JSON_FILE = "json/tiere.json"
INPUT_FILE = "assets/tiere.pdf"
LAST_PAGE = 52


class Answer(BaseModel):
    text: str = Field(description="Answer text without enumeration")
    correct: bool = Field(description="True if the answer is correct false if not")


class Question(BaseModel):
    question: str = Field(description="Text of the question")
    number: int = Field(description="Number of the question")
    answers: list[Answer] = Field(description="List of the possible answers")


class HuntingExam(BaseModel):
    questions: list[Question] = Field(description="List of questions in the catalog")


def error_exit(error_message):
    print(error_message)
    sys.exit(1)


def process_hunting_exam(extracted_text):
    preamble = (
        "What you are seeing are questions from an exam for the hunting license in Lower Saxony, Germany. "
        "Your job is to extract only the questions without chapter headings to the given format."
        "An [X] preceding the answer means that the answer is correct."
    )
    postamble = (
        "Do not include any explanation in the reply. "
        "Only include the extracted information in the reply. "
        "Only output the plain JSON without markdown formatting instructions like ```json"
    )
    system_template = "{preamble}"
    system_message_prompt = SystemMessagePromptTemplate.from_template(system_template)
    human_template = "{format_instructions}\n\n{extracted_text}\n\n{postamble}"
    human_message_prompt = HumanMessagePromptTemplate.from_template(human_template)

    parser = PydanticOutputParser(pydantic_object=HuntingExam)
    chat_prompt = ChatPromptTemplate.from_messages(
        [system_message_prompt, human_message_prompt]
    )
    request = chat_prompt.format_prompt(
        preamble=preamble,
        format_instructions=parser.get_format_instructions(),
        extracted_text=extracted_text,
        postamble=postamble,
    ).to_messages()
    chat = ChatOpenAI()
    response = chat(request, temperature=0.0)
    return response.content


def extract_text_from_pdf(file_path, pages_list=None):
    llmw = LLMWhispererClientV2()
    result = llmw.whisper(
        file_path=file_path,
        pages_to_extract=pages_list,
        wait_for_completion=True,
        output_mode="text",
        page_seperator="",
    )
    return result


def process_pdf(file_path, pages_list) -> HuntingExam:
    extracted_text = extract_text_from_pdf(file_path, pages_list)
    response = process_hunting_exam(extracted_text)
    return HuntingExam(**json.loads(response))


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
    exam = process_pdf(INPUT_FILE, 1)
    try:
        for i in range(2, LAST_PAGE + 1):
            exam.questions.extend(process_pdf(INPUT_FILE, f"{i}").questions)
    finally:
        pathlib.Path(JSON_FILE).parent.mkdir(parents=True, exist_ok=True)
        with open(JSON_FILE, "w", encoding="utf-8") as file:
            json.dump(exam.model_dump(), file, indent=2, ensure_ascii=False)
    generate_flashcards(exam)


if __name__ == "__main__":
    main()
