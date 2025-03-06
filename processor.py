import json
import pathlib

import genanki
from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import (ChatPromptTemplate, HumanMessagePromptTemplate,
                               SystemMessagePromptTemplate)
from langchain_openai import ChatOpenAI
from pydantic import BaseModel, Field
from unstract.llmwhisperer.client_v2 import LLMWhispererClientV2


class Answer(BaseModel):
    text: str = Field(description="Answer text without enumeration")
    correct: bool = Field(description="True if the answer is correct false if not")


class Question(BaseModel):
    question: str = Field(description="Text of the question")
    number: int = Field(description="Number of the question")
    answers: list[Answer] = Field(description="List of the possible answers")


class HuntingExam(BaseModel):
    questions: list[Question] = Field(description="List of questions in the catalog")


def process_hunting_exam(extracted_text, model):
    preamble = (
        "What you are seeing are questions from an exam for the hunting license in Lower Saxony, Germany. "
        "Your job is to extract only the questions without chapter headings to the given format."
        "An [X] preceding the answer means that the answer is correct. Put all answers in the output and mark incorrect answers with false."
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
    chat = ChatOpenAI(model=model)
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


def process_pdf(file_path, pages_list, model="gpt-3.5-turbo") -> HuntingExam:
    extracted_text = extract_text_from_pdf(file_path, pages_list)
    response = process_hunting_exam(extracted_text, model)
    return HuntingExam(**json.loads(response))


def generate_flashcards(
    data: HuntingExam,
    anki_deck_name: str,
    deck_id: int,
    output_file,
    anki_deck_description="",
    model_id=1566095810,
):
    template_dir = "templates/"
    with open(f"{template_dir}afmt.html", encoding="utf-8") as file:
        afmt = file.read()
    with open(f"{template_dir}qfmt.html", encoding="utf-8") as file:
        qfmt = file.read()
    with open(f"{template_dir}style.css", encoding="utf-8") as file:
        style = file.read()
    model = genanki.Model(
        model_id,
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
        deck_id,
        anki_deck_name,
        description=anki_deck_description,
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
    pathlib.Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    genanki.Package(my_deck).write_to_file(output_file)
