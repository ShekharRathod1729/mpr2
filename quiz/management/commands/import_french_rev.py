from django.core.management.base import BaseCommand
from quiz.models import Quiz, Question

class Command(BaseCommand):
    def handle(self, *args, **kwargs):
        quiz = Quiz.objects.get(title="French Revolution")
        with open("FrenchRev.txt", "r") as file:
            lines = file.readlines()
        question_text = None
        options = []
        correct_option = None

        for i in range(10):
            question_text = lines[i * 5]
            
            for j in range(4):
                curr = lines[i * 5 + j + 1]
                if curr[1] == ')':
                    options.append(curr[3:])
                else:
                    options.append(curr[4:])
                    correct_option = ord(curr[1]) - ord('a') + 1
            
            Question.objects.create(
                    quiz = quiz,
                    text = question_text,
                    option1 = options[0],
                    option2 = options[1],
                    option3 = options[2],
                    option4 =  options[3],
                    correct_option = correct_option
                    
            )
            self.stdout.write(self.style.SUCCESS(f"Added question: {question_text}"))

            options = []

        self.stdout.write(self.style.SUCCESS("French Revolution questions added successfully!"))
