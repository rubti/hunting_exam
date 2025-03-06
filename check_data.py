from processor import HuntingExam, process_pdf
import json
from dotenv import load_dotenv

PDF_FILE = "assets/jagdwaffen.pdf"
FAILS_FILE = "json/jagdwaffen.json"
CORRECT_FILE = "json/jagdwaffen_2.json"
OUTPUT_FILE = "json/jagdwaffen_correct.json"


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
        for a in q.answers:
            if not a.correct:
                all_true = False
        if all_true:
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


def extract_pages(pages_to_extract: list):
    exam = HuntingExam(**{"questions": []})
    for p in pages_to_extract:
        exam.questions.extend(process_pdf(PDF_FILE, p, model="gpt-4o-mini").questions)
    with open(CORRECT_FILE, "x", encoding="utf-8") as file:
        json.dump(exam.model_dump(), file, indent=2, ensure_ascii=False)
    return exam


if __name__ == "__main__":
    # fix_json(FAILS_FILE, CORRECT_FILE, OUTPUT_FILE)
    with open(OUTPUT_FILE, "r", encoding="utf-8") as file:
        print(count_only_true_answers(HuntingExam(**json.load(file))))
