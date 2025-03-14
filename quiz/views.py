from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login
from django.contrib import messages
from .models import UserProfile, Quiz, Question, UserQuizHistory
from django.contrib.auth.decorators import login_required

def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        full_name = request.POST["full_name"]
        email = request.POST["email"]
        password = request.POST["password"]
        confirm_password = request.POST["confirm_password"]

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect("register")

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already taken.")
            return redirect("register")

        name_parts = full_name.strip().split(" ", 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else ""

        user = User.objects.create_user(username=username, password=password, first_name=first_name, last_name=last_name)
        
        UserProfile.objects.create(user=user)
        
        login(request, user)
        messages.success(request, "Registration successful!")
        return redirect("home")
    return render(request, "register.html")

def login_view(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect("home")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")
    
    return render(request, "login.html")

def home(request):
    return render(request, "home.html")

@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    questions= Question.objects.filter(quiz=quiz)

    if request.method == "POST":
        question_id = int(request.POST["question_id"])
        selected_option = int(request.POST["selected_option"])

        question = get_object_or_404(Question, id=question_id)

        quiz_history, created = UserQuizHistory.objects.get_or_create(user=request.user, quiz=quiz)

        if selected_option == question.correct_option:
            quiz_history.score += 10
            quiz_history.save()

        next_question = questions.filter(id__gt=question_id).first()

        if next_question:
            return redirect("quiz_question", quiz_id=quiz.id, question_id=next_question.id)

        else:
            quiz_history.completed = True
            quiz_history.save()

            user_profile = request.user.userprofile
            user_profile.points += quiz_history.score
            user_profile.save()

            messages.success(request, f"Quiz completed! Your score: {quiz_history.score}")       
            return redirect("quiz_results", quiz_id=quiz.id)
        
    first_question = questions.first()
    return redirect("quiz_question", quiz_id=quiz.id, question_id=first_question.id)

@login_required
def quiz_question(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)

    return render(request, "quiz_question.html", {"quiz": quiz, "question": question})

@login_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    quiz_history = get_object_or_404(UserQuizHistory, user=request.user, quiz=quiz)

    return render(request, "quiz_results.html", {"quiz": quiz, "quiz_history": quiz_history})