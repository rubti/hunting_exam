import main
import json


def main_function():
    with open(main.JSON_FILE, encoding="utf-8") as file:
        exam = main.HuntingExam(**json.load(file))

    main.generate_flashcards(exam)


if __name__ == "__main__":
    main_function()
