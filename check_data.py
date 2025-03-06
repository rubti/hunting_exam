from processor import HuntingExam, process_pdf
import json
from dotenv import load_dotenv

SUBJECT = "tiere"
PDF_FILE = f"assets/{SUBJECT}.pdf"
FAILS_FILE = f"json/{SUBJECT}.json"
CORRECT_FILE = f"json/{SUBJECT}_2.json"
OUTPUT_FILE = f"json/{SUBJECT}_correct.json"


def check_for_only_true_answers(data: HuntingExam):
    for q in data.questions:
        all_true = True
        for a in q.answers:
            if not a.correct:
                all_true = False
        if all_true:
            yield q


def correct_fails(false_data: HuntingExam, correct_data: HuntingExam):
    for f in check_for_only_true_answers(false_data):
        for c in correct_data.questions:
            if f.number == c.number:
                f.answers.clear()
                f.answers = c.answers.copy()
                break


def count_only_true_answers(data: HuntingExam):
    true_only = []
    for q in data.questions:
        all_true = True
        all_false = True
        for a in q.answers:
            if not a.correct:
                all_true = False
            else:
                all_false = False
        if all_true or all_false:
            true_only.append(q.number)
    return true_only


def fix_json(failed_file, correct_file, output_file=None):
    with open(failed_file, "r", encoding="utf-8") as file:
        fails = HuntingExam(**json.load(file))
    with open(correct_file, "r", encoding="utf-8") as file:
        correct = HuntingExam(**json.load(file))
    correct_fails(fails, correct)
    if output_file is not None:
        with open(output_file, "x", encoding="utf-8") as file:
            json.dump(fails.model_dump(), file, indent=2, ensure_ascii=False)
    return fails


def extract_pages(pdf_file, output_file, pages_to_extract: list):
    exam = HuntingExam(**{"questions": []})
    for p in pages_to_extract:
        exam.questions.extend(process_pdf(pdf_file, p, model="gpt-4o-mini").questions)
    with open(output_file, "x", encoding="utf-8") as file:
        json.dump(exam.model_dump(), file, indent=2, ensure_ascii=False)
    return exam


def check_continuity(data: HuntingExam):
    for i in range(len(data.questions)):
        if data.questions[i].number != i + 1:
            raise Exception(
                f"Wrong number detected at {data.questions[i].number}. Actual number: {i + 1}"
            )


if __name__ == "__main__":
    # fix_json(FAILS_FILE, CORRECT_FILE, OUTPUT_FILE)
    # load_dotenv("./keys.env")
    # extract_pages(PDF_FILE, CORRECT_FILE, [11, 21, 23, 35, 37, 49])
    with open(FAILS_FILE, "r", encoding="utf-8") as file:
        # print(FAILS_FILE)
        # print(count_only_true_answers(HuntingExam(**json.load(file))))
        check_continuity(HuntingExam(**json.load(file)))
