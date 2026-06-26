from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='home'),

    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('profile/', views.profile_view, name='profile'),
    path('classrooms/', views.classroom_list, name='classroom_list'),
    path('classrooms/create/', views.create_classroom, name='create_classroom'),
    path('classrooms/join/', views.join_classroom, name='join_classroom'),
    path('classrooms/<int:pk>/', views.classroom_detail, name='classroom_detail'),
    path('classrooms/<int:classroom_id>/material/add/', views.add_material, name='add_material'),
    path('materials/<int:material_id>/', views.material_detail, name='material_detail'),
    path('materials/<int:material_id>/video-status/', views.update_video_status, name='update_video_status'),
    path('classrooms/<int:classroom_id>/assignment/add/', views.add_assignment, name='add_assignment'),
    path('classrooms/<int:classroom_id>/announcement/add/', views.add_announcement, name='add_announcement'),
    path('classrooms/<int:classroom_id>/attendance/', views.mark_attendance, name='mark_attendance'),
    path('classrooms/<int:classroom_id>/quiz/create/', views.create_quiz, name='create_quiz'),
    path('assignments/<int:assignment_id>/submit/', views.submit_assignment, name='submit_assignment'),
    path('assignments/<int:assignment_id>/submissions/', views.submission_list, name='submission_list'),
    path('submissions/<int:submission_id>/grade/', views.grade_submission, name='grade_submission'),
    path('quiz/<int:quiz_id>/questions/add/', views.add_quiz_question, name='add_quiz_question'),
    path('quiz/<int:quiz_id>/attempt/', views.attempt_quiz, name='attempt_quiz'),
    path('reports/', views.reports, name='reports'),
    path('demo-seed/', views.demo_seed, name='demo_seed'),

    path("student/profile/", views.student_profile_view, name="student_profile"),
    path("student/profile/edit/", views.student_profile_create_update, name="student_profile_edit"),
    path("teacher/student-profile/<int:user_id>/", views.teacher_view_student_profile, name="teacher_view_student_profile"),
]
