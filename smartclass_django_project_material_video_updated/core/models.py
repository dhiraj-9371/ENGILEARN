from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
import uuid


class Profile(models.Model):
    ROLE_CHOICES = (
        ('admin', 'Admin'),
        ('teacher', 'Teacher'),
        ('student', 'Student'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True)
    bio = models.TextField(blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.role}"

from django.conf import settings
from django.db import models


class StudentAcademicProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="student_academic_profile")
    student_name = models.CharField(max_length=150, blank=True)
    roll_number = models.CharField(max_length=50, blank=True)
    division = models.CharField(max_length=30, blank=True)
    batch = models.CharField(max_length=50, blank=True)
    department = models.CharField(max_length=100, blank=True)
    semester = models.CharField(max_length=30, blank=True)

    internship = models.BooleanField(default=False)
    internship_company = models.CharField(max_length=150, blank=True)
    internship_domain = models.CharField(max_length=150, blank=True)

    marks = models.FloatField(default=0.0)
    attendance_percentage = models.FloatField(default=0.0)
    quiz_average = models.FloatField(default=0.0)
    assignment_average = models.FloatField(default=0.0)

    skills = models.TextField(blank=True)
    strengths = models.TextField(blank=True)
    improvement_areas = models.TextField(blank=True)
    career_goal = models.CharField(max_length=200, blank=True)

    guardian_name = models.CharField(max_length=150, blank=True)
    guardian_contact = models.CharField(max_length=20, blank=True)

    predicted_band = models.CharField(max_length=50, blank=True, default="Not generated")
    risk_level = models.CharField(max_length=50, blank=True, default="Unknown")
    ai_suggestions = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} Student Profile"
    
    
class Classroom(models.Model):
    teacher = models.ForeignKey(User, on_delete=models.CASCADE, related_name='teaching_classes')
    title = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    class_code = models.CharField(max_length=12, unique=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.class_code:
            self.class_code = uuid.uuid4().hex[:8].upper()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.title} ({self.subject})"


class Enrollment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='enrollments')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='enrollments')
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('classroom', 'student')

    def __str__(self):
        return f"{self.student.username} -> {self.classroom.title}"


class Material(models.Model):
    MATERIAL_TYPE_CHOICES = (
        ('handwritten_notes', 'Handwritten Notes'),
        ('study_material', 'Study Material'),
        ('previous_question_paper', 'Previous Question Paper'),
        ('video', 'Video'),
    )

    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='materials')
    title = models.CharField(max_length=200)
    material_type = models.CharField(max_length=40, choices=MATERIAL_TYPE_CHOICES, default='study_material')
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='materials/', blank=True, null=True)
    external_link = models.URLField(blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def is_video(self):
        if self.material_type == 'video':
            return True
        if self.file:
            lower = self.file.name.lower()
            return lower.endswith(('.mp4', '.webm', '.ogg', '.mov', '.m4v'))
        return False


class VideoWatchStatus(models.Model):
    material = models.ForeignKey(Material, on_delete=models.CASCADE, related_name='watch_statuses')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='video_watch_statuses')
    viewed = models.BooleanField(default=False)
    progress_seconds = models.PositiveIntegerField(default=0)
    watched_at = models.DateTimeField(blank=True, null=True)
    last_interaction_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('material', 'student')

    def __str__(self):
        return f"{self.student.username} - {self.material.title}"


class Assignment(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='assignments')
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    total_marks = models.PositiveIntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def is_overdue(self):
        return timezone.now() > self.deadline

    def __str__(self):
        return self.title


class Submission(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='submissions')
    answer_file = models.FileField(upload_to='submissions/')
    note = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    marks = models.PositiveIntegerField(blank=True, null=True)
    feedback = models.TextField(blank=True)

    class Meta:
        unique_together = ('assignment', 'student')


class Announcement(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='announcements')
    title = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title


class Attendance(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='attendance_records')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    date = models.DateField(default=timezone.localdate)
    status = models.CharField(max_length=10, choices=(('present', 'Present'), ('absent', 'Absent')))

    class Meta:
        unique_together = ('classroom', 'student', 'date')


class Quiz(models.Model):
    classroom = models.ForeignKey(Classroom, on_delete=models.CASCADE, related_name='quizzes')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class QuizQuestion(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='questions')
    question_text = models.CharField(max_length=255)
    option_a = models.CharField(max_length=255)
    option_b = models.CharField(max_length=255)
    option_c = models.CharField(max_length=255)
    option_d = models.CharField(max_length=255)
    correct_option = models.CharField(max_length=1, choices=(('A', 'A'), ('B', 'B'), ('C', 'C'), ('D', 'D')))


class QuizAttempt(models.Model):
    quiz = models.ForeignKey(Quiz, on_delete=models.CASCADE, related_name='attempts')
    student = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quiz_attempts')
    score = models.PositiveIntegerField(default=0)
    total_questions = models.PositiveIntegerField(default=0)
    attempted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('quiz', 'student')
