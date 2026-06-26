from django.contrib import admin
from .models import Profile, Classroom, Enrollment, Material, Assignment, Submission, Announcement, Attendance, Quiz, QuizQuestion, QuizAttempt

admin.site.register(Profile)
admin.site.register(Classroom)
admin.site.register(Enrollment)
admin.site.register(Material)
admin.site.register(Assignment)
admin.site.register(Submission)
admin.site.register(Announcement)
admin.site.register(Attendance)
admin.site.register(Quiz)
admin.site.register(QuizQuestion)
admin.site.register(QuizAttempt)
