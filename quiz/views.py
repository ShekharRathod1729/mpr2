from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .models import UserProfile, Quiz, Question, UserQuizHistory
from django.contrib.auth.decorators import login_required
from django.db.models import Sum
import random

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
            return redirect("user_dashboard")
        else:
            messages.error(request, "Invalid username or password.")
            return redirect("login")
    
    return render(request, "login.html")

def home(request):
    return render(request, "home.html")

@login_required
def start_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    all_questions = list(Question.objects.filter(quiz=quiz).order_by('?'))[:5]
    request.session['quiz_questions'] = [q.id for q in all_questions]
    first_q = all_questions[0]
    return redirect("quiz_question", quiz_id=quiz.id, question_id=first_q.id)

@login_required
def quiz_question(request, quiz_id, question_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    question = get_object_or_404(Question, id=question_id, quiz=quiz)
    feedback = None
    correct_answer = None
    selected_option = None

    if request.method == "POST":
        selected_option = int(request.POST.get("selected_option", 0))
        is_correct = selected_option == question.correct_option
        correct_answer = question.correct_option

        if 'quiz_score' not in request.session:
            request.session['quiz_score'] = 0
        
        if is_correct:
            request.session['quiz_score'] += 10
        
        # Store the answer in session or database
        request.session['last_answer'] = {
            'question_id': question_id,
            'is_correct': is_correct,
            'selected_option': selected_option,
            'correct_answer': correct_answer
        }
        
        feedback = {
            'is_correct': is_correct,
            'correct_answer': correct_answer,
            'selected_option': selected_option
        }

    options = [
        {"text": question.option1, "value": 1},
        {"text": question.option2, "value": 2},
        {"text": question.option3, "value": 3},
        {"text": question.option4, "value": 4},
    ]

    question_ids = request.session.get('quiz_questions', [])
    current_index = question_ids.index(question.id) if question.id in question_ids else -1
    next_question_id = question_ids[current_index + 1] if current_index + 1 < len(question_ids) else None
    next_question = Question.objects.filter(id=next_question_id).first() if next_question_id else None
    
    return render(request, "quiz_question.html", {
        "quiz": quiz,
        "question": question,
        "options": options,
        "feedback": feedback,
        "correct_answer": correct_answer,
        "selected_option": selected_option,
        "next_question": next_question
    })

@login_required
def quiz_results(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    
    if 'quiz_score' in request.session:
        quiz_history = UserQuizHistory.objects.create(
            user=request.user,
            quiz=quiz,
            score=request.session['quiz_score']
        )

        user_profile = request.user.userprofile
        user_profile.points += request.session['quiz_score']
        user_profile.save()

    if 'quiz_questions' in request.session:
        del request.session['quiz_questions']
    if 'quiz_score' in request.session:
        del request.session['quiz_score']

    return render(request, "quiz_results.html", {"quiz": quiz, "quiz_history": quiz_history})

@login_required
def user_dashboard(request):
    user_profile = UserProfile.objects.get(user=request.user)
    quizzes_attempted = UserQuizHistory.objects.filter(user=request.user).count()
    total_points = user_profile.points
    recent_attempts = UserQuizHistory.objects.filter(user=request.user).order_by('-timestamp')[:5]

    leaderboard = UserProfile.objects.order_by('-points')[:5]    

    context = {
            "user_profile": user_profile,
            "quizzes_attempted": quizzes_attempted,
            "total_points": total_points,
            "recent_attempts": recent_attempts,
            "leaderboard": leaderboard,
        }
    return render(request, "profile.html", context)

def logout_view(request):
    logout(request)
    return redirect("home")