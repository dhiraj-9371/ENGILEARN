from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.db.models import Avg, Count, Q
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.http import require_POST

from .forms import (
    AnnouncementForm,
    AssignmentForm,
    ClassroomForm,
    GradeSubmissionForm,
    JoinClassForm,
    LoginForm,
    MaterialForm,
    ProfileUpdateForm,
    QuizForm,
    QuizQuestionForm,
    RegisterForm,
    SubmissionForm,
)
from .models import (
    Announcement,
    Assignment,
    Attendance,
    Classroom,
    Enrollment,
    Material,
    Quiz,
    QuizAttempt,
    Submission,
    VideoWatchStatus,
)


def index(request):
     return render(request, 'core/index.html')

def home(request):
    featured_classes = Classroom.objects.order_by('-created_at')[:6]
    return render(request, 'core/home.html', {'featured_classes': featured_classes})


def register_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = RegisterForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        user = form.save(commit=False)
        user.email = form.cleaned_data['email']
        user.first_name = form.cleaned_data['first_name']
        user.last_name = form.cleaned_data['last_name']
        user.save()
        profile = user.profile
        profile.role = form.cleaned_data['role']
        profile.phone = form.cleaned_data['phone']
        profile.save()
        login(request, user)
        messages.success(request, 'Account created successfully.')
        return redirect('dashboard')
    return render(request, 'core/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    form = LoginForm(request, data=request.POST or None)
    if request.method == 'POST' and form.is_valid():
        login(request, form.get_user())
        messages.success(request, 'Welcome back.')
        return redirect('dashboard')
    return render(request, 'core/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('home')


@login_required
def dashboard(request):
    profile = request.user.profile
    if profile.role == 'teacher':
        classrooms = Classroom.objects.filter(teacher=request.user)
        stats = {
            'classes': classrooms.count(),
            'students': Enrollment.objects.filter(classroom__teacher=request.user).values('student').distinct().count(),
            'assignments': Assignment.objects.filter(classroom__teacher=request.user).count(),
            'materials': Material.objects.filter(classroom__teacher=request.user).count(),
        }
    elif profile.role == 'student':
        classrooms = Classroom.objects.filter(enrollments__student=request.user).distinct()
        stats = {
            'classes': classrooms.count(),
            'assignments': Assignment.objects.filter(classroom__enrollments__student=request.user).distinct().count(),
            'submissions': Submission.objects.filter(student=request.user).count(),
            'videos_watched': VideoWatchStatus.objects.filter(student=request.user, viewed=True).count(),
        }
    else:
        classrooms = Classroom.objects.all()
        stats = {
            'classes': Classroom.objects.count(),
            'teachers': User.objects.filter(profile__role='teacher').count(),
            'students': User.objects.filter(profile__role='student').count(),
            'submissions': Submission.objects.count(),
        }
    announcements = Announcement.objects.order_by('-created_at')[:5]
    return render(request, 'core/dashboard.html', {
        'profile': profile,
        'classrooms': classrooms,
        'stats': stats,
        'announcements': announcements,
    })


@login_required
def profile_view(request):
    form = ProfileUpdateForm(request.POST or None, instance=request.user.profile)
    if request.method == 'POST' and form.is_valid():
        request.user.first_name = request.POST.get('first_name', '')
        request.user.last_name = request.POST.get('last_name', '')
        request.user.email = request.POST.get('email', '')
        request.user.save()
        form.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('profile')
    return render(request, 'core/profile.html', {'form': form})

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib.auth.models import User

from .forms import StudentAcademicProfileForm
from .models import StudentAcademicProfile
from .utils import generate_ai_performance_analysis

@login_required
def student_profile_create_update(request):
    profile_obj, created = StudentAcademicProfile.objects.get_or_create(user=request.user)

    # only student can create/update own profile
    if hasattr(request.user, "profile") and request.user.profile.role != "student":
        messages.error(request, "Only students can edit student profile.")
        return redirect("dashboard")

    if request.method == "POST":
        form = StudentAcademicProfileForm(request.POST, instance=profile_obj)
        if form.is_valid():
            saved_profile = form.save(commit=False)
            predicted_band, risk_level, ai_text = generate_ai_performance_analysis(saved_profile)
            saved_profile.predicted_band = predicted_band
            saved_profile.risk_level = risk_level
            saved_profile.ai_suggestions = ai_text
            saved_profile.save()
            messages.success(request, "Student profile saved successfully.")
            return redirect("student_profile")
    else:
        form = StudentAcademicProfileForm(instance=profile_obj)

    return render(
        request,
        "core/student_profile_form.html",
        {
            "form": form,
            "student_profile_obj": profile_obj,
        },
    )


@login_required
def student_profile_view(request):
    profile_obj, created = StudentAcademicProfile.objects.get_or_create(user=request.user)

    if hasattr(request.user, "profile") and request.user.profile.role != "student":
        messages.error(request, "Only students can view this page.")
        return redirect("dashboard")

    return render(
        request,
        "core/student_profile_view.html",
        {
            "student_profile_obj": profile_obj,
        },
    )


@login_required
def teacher_view_student_profile(request, user_id):
    student_user = get_object_or_404(User, id=user_id)
    student_profile_obj, created = StudentAcademicProfile.objects.get_or_create(user=student_user)

    # teacher/admin only
    allowed = False
    if hasattr(request.user, "profile"):
        if request.user.profile.role in ["teacher", "admin"]:
            allowed = True

    if not allowed:
        messages.error(request, "You are not allowed to view this page.")
        return redirect("dashboard")

    return render(
        request,
        "core/teacher_student_profile_view.html",
        {
            "student_user": student_user,
            "student_profile_obj": student_profile_obj,
        },
    )

@login_required
def create_classroom(request):
    if request.user.profile.role != 'teacher':
        return HttpResponseForbidden('Only teachers can create classrooms.')
    form = ClassroomForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        classroom = form.save(commit=False)
        classroom.teacher = request.user
        classroom.save()
        messages.success(request, f'Classroom created. Code: {classroom.class_code}')
        return redirect('classroom_detail', classroom.id)
    return render(request, 'core/create_classroom.html', {'form': form})


@login_required
def join_classroom(request):
    form = JoinClassForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        code = form.cleaned_data['class_code'].strip().upper()
        classroom = Classroom.objects.filter(class_code=code).first()
        if classroom:
            Enrollment.objects.get_or_create(classroom=classroom, student=request.user)
            messages.success(request, f'Joined {classroom.title} successfully.')
            return redirect('classroom_detail', classroom.id)
        messages.error(request, 'Invalid class code.')
    return render(request, 'core/join_classroom.html', {'form': form})


@login_required
def classroom_list(request):
    if request.user.profile.role == 'teacher':
        classrooms = Classroom.objects.filter(teacher=request.user)
    elif request.user.profile.role == 'student':
        classrooms = Classroom.objects.filter(enrollments__student=request.user).distinct()
    else:
        classrooms = Classroom.objects.all()
    return render(request, 'core/classroom_list.html', {'classrooms': classrooms})


@login_required
def classroom_detail(request, pk):
    classroom = get_object_or_404(Classroom, pk=pk)
    is_teacher = classroom.teacher == request.user
    is_student = Enrollment.objects.filter(classroom=classroom, student=request.user).exists()
    if request.user.profile.role == 'student' and not is_student:
        return HttpResponseForbidden('Join this class first.')
    students = User.objects.filter(enrollments__classroom=classroom).exclude(id=classroom.teacher.id).distinct()
    materials = classroom.materials.order_by('-uploaded_at')

    teacher_video_status = []
    if is_teacher:
        for material in materials:
            if material.is_video:
                watched_count = VideoWatchStatus.objects.filter(material=material, viewed=True).count()
                total_students = students.count()
                teacher_video_status.append({
                    'material': material,
                    'watched_count': watched_count,
                    'total_students': total_students,
                    'pending_count': max(total_students - watched_count, 0),
                    'statuses': VideoWatchStatus.objects.filter(material=material).select_related('student').order_by('student__username'),
                })

    watched_material_ids = []
    if is_student:
        watched_material_ids = list(VideoWatchStatus.objects.filter(material__in=materials, student=request.user, viewed=True).values_list('material_id', flat=True))

    context = {
        'classroom': classroom,
        'is_teacher': is_teacher,
        'is_student': is_student,
        'students': students,
        'materials': materials,
        'assignments': classroom.assignments.order_by('-created_at'),
        'announcements': classroom.announcements.all(),
        'quizzes': classroom.quizzes.order_by('-created_at'),
        'teacher_video_status': teacher_video_status,
        'watched_material_ids': watched_material_ids,
    }
    return render(request, 'core/classroom_detail.html', context)


@login_required
def add_material(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id, teacher=request.user)
    form = MaterialForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        material = form.save(commit=False)
        material.classroom = classroom
        material.save()
        messages.success(request, 'Material uploaded successfully.')
        return redirect('classroom_detail', classroom.id)
    return render(request, 'core/form_page.html', {
        'form': form,
        'title': 'Upload Study Material',
        'subtitle': 'Upload handwritten notes, study materials, previous question papers, or video lessons.'
    })


@login_required
def material_detail(request, material_id):
    material = get_object_or_404(Material.objects.select_related('classroom', 'classroom__teacher'), id=material_id)
    is_student = Enrollment.objects.filter(classroom=material.classroom, student=request.user).exists()
    is_teacher = material.classroom.teacher == request.user
    if not is_teacher and not is_student and request.user.profile.role != 'admin':
        return HttpResponseForbidden('You are not allowed to open this material.')

    watch_status = None
    if material.is_video and is_student:
        watch_status, _ = VideoWatchStatus.objects.get_or_create(material=material, student=request.user)

    return render(request, 'core/material_detail.html', {
        'material': material,
        'is_teacher': is_teacher,
        'is_student': is_student,
        'watch_status': watch_status,
    })


@login_required
@require_POST
def update_video_status(request, material_id):
    material = get_object_or_404(Material, id=material_id)
    if not material.is_video:
        return JsonResponse({'ok': False, 'message': 'Not a video material.'}, status=400)
    if not Enrollment.objects.filter(classroom=material.classroom, student=request.user).exists():
        return JsonResponse({'ok': False, 'message': 'Not enrolled.'}, status=403)

    progress = int(request.POST.get('progress_seconds', '0') or 0)
    completed = request.POST.get('completed') == 'true'
    status_obj, _ = VideoWatchStatus.objects.get_or_create(material=material, student=request.user)
    if progress > status_obj.progress_seconds:
        status_obj.progress_seconds = progress
    if completed:
        status_obj.viewed = True
        status_obj.watched_at = timezone.now()
    status_obj.save()
    return JsonResponse({'ok': True, 'viewed': status_obj.viewed, 'progress_seconds': status_obj.progress_seconds})


@login_required
def add_assignment(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id, teacher=request.user)
    form = AssignmentForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        assignment = form.save(commit=False)
        assignment.classroom = classroom
        assignment.save()
        messages.success(request, 'Assignment created successfully.')
        return redirect('classroom_detail', classroom.id)
    return render(request, 'core/form_page.html', {'form': form, 'title': 'Create Assignment'})


@login_required
def submit_assignment(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id)
    if not Enrollment.objects.filter(classroom=assignment.classroom, student=request.user).exists():
        return HttpResponseForbidden('You are not enrolled in this class.')
    submission = Submission.objects.filter(assignment=assignment, student=request.user).first()
    form = SubmissionForm(request.POST or None, request.FILES or None, instance=submission)
    if request.method == 'POST' and form.is_valid():
        sub = form.save(commit=False)
        sub.assignment = assignment
        sub.student = request.user
        sub.save()
        messages.success(request, 'Assignment submitted successfully.')
        return redirect('classroom_detail', assignment.classroom.id)
    return render(request, 'core/form_page.html', {'form': form, 'title': f'Submit: {assignment.title}'})


@login_required
def submission_list(request, assignment_id):
    assignment = get_object_or_404(Assignment, id=assignment_id, classroom__teacher=request.user)
    submissions = assignment.submissions.select_related('student').order_by('-submitted_at')
    return render(request, 'core/submission_list.html', {'assignment': assignment, 'submissions': submissions})


@login_required
def grade_submission(request, submission_id):
    submission = get_object_or_404(Submission, id=submission_id, assignment__classroom__teacher=request.user)
    form = GradeSubmissionForm(request.POST or None, instance=submission)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Submission graded successfully.')
        return redirect('submission_list', submission.assignment.id)
    return render(request, 'core/form_page.html', {'form': form, 'title': f'Grade: {submission.student.username}'})


@login_required
def add_announcement(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id, teacher=request.user)
    form = AnnouncementForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        obj = form.save(commit=False)
        obj.classroom = classroom
        obj.save()
        messages.success(request, 'Announcement posted.')
        return redirect('classroom_detail', classroom.id)
    return render(request, 'core/form_page.html', {'form': form, 'title': 'Post Announcement'})


@login_required
def mark_attendance(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id, teacher=request.user)
    students = User.objects.filter(enrollments__classroom=classroom).distinct()
    if request.method == 'POST':
        today = timezone.localdate()
        for student in students:
            status = request.POST.get(f'status_{student.id}', 'absent')
            Attendance.objects.update_or_create(
                classroom=classroom,
                student=student,
                date=today,
                defaults={'status': status}
            )
        messages.success(request, 'Attendance saved for today.')
        return redirect('classroom_detail', classroom.id)
    return render(request, 'core/attendance_mark.html', {'classroom': classroom, 'students': students})


@login_required
def create_quiz(request, classroom_id):
    classroom = get_object_or_404(Classroom, id=classroom_id, teacher=request.user)
    form = QuizForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        quiz = form.save(commit=False)
        quiz.classroom = classroom
        quiz.save()
        messages.success(request, 'Quiz created. Add questions now.')
        return redirect('add_quiz_question', quiz.id)
    return render(request, 'core/form_page.html', {'form': form, 'title': 'Create Quiz'})


@login_required
def add_quiz_question(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id, classroom__teacher=request.user)
    form = QuizQuestionForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        question = form.save(commit=False)
        question.quiz = quiz
        question.save()
        messages.success(request, 'Question added.')
        return redirect('add_quiz_question', quiz.id)
    return render(request, 'core/add_quiz_question.html', {'form': form, 'quiz': quiz, 'questions': quiz.questions.all()})


@login_required
def attempt_quiz(request, quiz_id):
    quiz = get_object_or_404(Quiz, id=quiz_id)
    if not Enrollment.objects.filter(classroom=quiz.classroom, student=request.user).exists():
        return HttpResponseForbidden('You are not enrolled in this class.')
    if QuizAttempt.objects.filter(quiz=quiz, student=request.user).exists():
        messages.info(request, 'You already attempted this quiz.')
        return redirect('classroom_detail', quiz.classroom.id)
    questions = quiz.questions.all()
    if request.method == 'POST':
        score = 0
        total = questions.count()
        for q in questions:
            if request.POST.get(f'question_{q.id}') == q.correct_option:
                score += 1
        QuizAttempt.objects.create(quiz=quiz, student=request.user, score=score, total_questions=total)
        messages.success(request, f'Quiz submitted. Score: {score}/{total}')
        return redirect('classroom_detail', quiz.classroom.id)
    return render(request, 'core/attempt_quiz.html', {'quiz': quiz, 'questions': questions})


@login_required
def reports(request):
    profile = request.user.profile
    if profile.role == 'teacher':
        classes = Classroom.objects.filter(teacher=request.user)
        attendance_summary = Attendance.objects.filter(classroom__teacher=request.user).values('status').annotate(total=Count('id'))
        avg_score = QuizAttempt.objects.filter(quiz__classroom__teacher=request.user).aggregate(avg=Avg('score'))['avg'] or 0
        material_stats = Material.objects.filter(classroom__teacher=request.user).values('material_type').annotate(total=Count('id')).order_by('material_type')
        video_view_total = VideoWatchStatus.objects.filter(material__classroom__teacher=request.user, viewed=True).count()
    elif profile.role == 'student':
        classes = Classroom.objects.filter(enrollments__student=request.user).distinct()
        attendance_summary = Attendance.objects.filter(student=request.user).values('status').annotate(total=Count('id'))
        avg_score = QuizAttempt.objects.filter(student=request.user).aggregate(avg=Avg('score'))['avg'] or 0
        material_stats = Material.objects.filter(classroom__enrollments__student=request.user).values('material_type').annotate(total=Count('id')).order_by('material_type')
        video_view_total = VideoWatchStatus.objects.filter(student=request.user, viewed=True).count()
    else:
        classes = Classroom.objects.all()
        attendance_summary = Attendance.objects.values('status').annotate(total=Count('id'))
        avg_score = QuizAttempt.objects.aggregate(avg=Avg('score'))['avg'] or 0
        material_stats = Material.objects.values('material_type').annotate(total=Count('id')).order_by('material_type')
        video_view_total = VideoWatchStatus.objects.filter(viewed=True).count()
    return render(request, 'core/reports.html', {
        'classes': classes,
        'attendance_summary': attendance_summary,
        'avg_score': avg_score,
        'material_stats': material_stats,
        'video_view_total': video_view_total,
    })


@login_required
def demo_seed(request):
    if request.user.profile.role != 'admin' and not request.user.is_superuser:
        return HttpResponseForbidden('Only admin can seed demo data.')
    teacher, _ = User.objects.get_or_create(username='teacher1', defaults={'first_name': 'Asha', 'last_name': 'Patil', 'email': 'teacher@example.com'})
    teacher.set_password('teacher123')
    teacher.save()
    teacher.profile.role = 'teacher'
    teacher.profile.save()
    student, _ = User.objects.get_or_create(username='student1', defaults={'first_name': 'Rahul', 'last_name': 'Sharma', 'email': 'student@example.com'})
    student.set_password('student123')
    student.save()
    student.profile.role = 'student'
    student.profile.save()
    classroom, _ = Classroom.objects.get_or_create(teacher=teacher, title='AI Fundamentals', subject='Artificial Intelligence', description='Introductory AI classroom')
    Enrollment.objects.get_or_create(classroom=classroom, student=student)
    Announcement.objects.get_or_create(classroom=classroom, title='Welcome', message='Welcome to SmartClass demo classroom.')
    Material.objects.get_or_create(classroom=classroom, title='Unit 1 Handwritten Notes', defaults={'material_type': 'handwritten_notes', 'description': 'Scanned handwritten concept notes.'})
    Material.objects.get_or_create(classroom=classroom, title='Previous Year Question Bank', defaults={'material_type': 'previous_question_paper', 'description': 'Practice previous exam questions.'})
    Material.objects.get_or_create(classroom=classroom, title='Introduction Video Lesson', defaults={'material_type': 'video', 'external_link': 'https://www.youtube.com/embed/dQw4w9WgXcQ', 'description': 'Demo embedded lesson video.'})
    messages.success(request, 'Demo data created. Teacher: teacher1/teacher123, Student: student1/student123')
    return redirect('dashboard')
