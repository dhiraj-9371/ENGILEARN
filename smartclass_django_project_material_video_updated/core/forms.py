from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Classroom, Material, Assignment, Submission, Announcement, Quiz, QuizQuestion, Profile


class StyledFormMixin:
    field_placeholders = {}

    def _apply_common_styles(self):
        for name, field in self.fields.items():
            widget = field.widget
            existing = widget.attrs.get('class', '')
            if isinstance(widget, forms.Select):
                widget.attrs['class'] = (existing + ' form-select').strip()
            elif not isinstance(widget, (forms.CheckboxInput, forms.RadioSelect, forms.CheckboxSelectMultiple)):
                widget.attrs['class'] = (existing + ' form-control').strip()
            placeholder = self.field_placeholders.get(name, field.label)
            if not isinstance(widget, (forms.ClearableFileInput, forms.CheckboxInput, forms.RadioSelect, forms.CheckboxSelectMultiple, forms.Select)):
                widget.attrs.setdefault('placeholder', placeholder)


class RegisterForm(StyledFormMixin, UserCreationForm):
    email = forms.EmailField()
    role = forms.ChoiceField(choices=(('teacher', 'Teacher'), ('student', 'Student')))
    phone = forms.CharField(required=False)

    field_placeholders = {
        'first_name': 'Enter first name',
        'last_name': 'Enter last name',
        'username': 'Choose a username',
        'email': 'Enter email address',
        'phone': 'Enter phone number',
        'password1': 'Create password',
        'password2': 'Confirm password',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_common_styles()

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email', 'role', 'phone', 'password1', 'password2')


class LoginForm(StyledFormMixin, AuthenticationForm):
    username = forms.CharField(widget=forms.TextInput(attrs={'placeholder': 'Username'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_common_styles()


from django import forms
from .models import StudentAcademicProfile


class StudentAcademicProfileForm(forms.ModelForm):
    class Meta:
        model = StudentAcademicProfile
        fields = [
            "student_name",
            "roll_number",
            "division",
            "batch",
            "department",
            "semester",
            "internship",
            "internship_company",
            "internship_domain",
            "marks",
            "attendance_percentage",
            "quiz_average",
            "assignment_average",
            "skills",
            "strengths",
            "improvement_areas",
            "career_goal",
            "guardian_name",
            "guardian_contact",
        ]
        widgets = {
            "student_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter student name"}),
            "roll_number": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter roll number"}),
            "division": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter division"}),
            "batch": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter batch"}),
            "department": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter department"}),
            "semester": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter semester"}),
            "internship": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "internship_company": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter internship company"}),
            "internship_domain": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter internship domain"}),
            "marks": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "attendance_percentage": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "quiz_average": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "assignment_average": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "skills": forms.Textarea(attrs={"class": "form-control", "rows": 3, "placeholder": "Python, Communication, ML, etc."}),
            "strengths": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "improvement_areas": forms.Textarea(attrs={"class": "form-control", "rows": 3}),
            "career_goal": forms.TextInput(attrs={"class": "form-control", "placeholder": "Software Engineer / Data Scientist / etc."}),
            "guardian_name": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter guardian name"}),
            "guardian_contact": forms.TextInput(attrs={"class": "form-control", "placeholder": "Enter guardian contact"}),
        }
        
class ClassroomForm(StyledFormMixin, forms.ModelForm):
    field_placeholders = {
        'title': 'Enter classroom title',
        'subject': 'Enter subject name',
        'description': 'Add classroom description',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_common_styles()

    class Meta:
        model = Classroom
        fields = ['title', 'subject', 'description']


class JoinClassForm(StyledFormMixin, forms.Form):
    class_code = forms.CharField(max_length=12)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_common_styles()
        self.fields['class_code'].widget.attrs.setdefault('placeholder', 'Enter classroom code')


class MaterialForm(StyledFormMixin, forms.ModelForm):
    field_placeholders = {
        'title': 'Enter material title',
        'description': 'Add short description',
        'external_link': 'Paste external reference link or video URL',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_common_styles()
        self.fields['material_type'].help_text = 'Choose the correct category for the uploaded content.'
        self.fields['file'].help_text = 'Upload PDF, DOC, image, question paper, or video file.'

    class Meta:
        model = Material
        fields = ['title', 'material_type', 'description', 'file', 'external_link']


class AssignmentForm(StyledFormMixin, forms.ModelForm):
    deadline = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))

    field_placeholders = {
        'title': 'Enter assignment title',
        'description': 'Write assignment details',
        'total_marks': 'Enter total marks',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_common_styles()

    class Meta:
        model = Assignment
        fields = ['title', 'description', 'deadline', 'total_marks']


class SubmissionForm(StyledFormMixin, forms.ModelForm):
    field_placeholders = {
        'note': 'Optional note for teacher',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_common_styles()

    class Meta:
        model = Submission
        fields = ['answer_file', 'note']


class GradeSubmissionForm(StyledFormMixin, forms.ModelForm):
    field_placeholders = {
        'marks': 'Enter marks',
        'feedback': 'Write feedback for student',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_common_styles()

    class Meta:
        model = Submission
        fields = ['marks', 'feedback']


class AnnouncementForm(StyledFormMixin, forms.ModelForm):
    field_placeholders = {
        'title': 'Enter announcement title',
        'message': 'Write your announcement message',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_common_styles()

    class Meta:
        model = Announcement
        fields = ['title', 'message']


class QuizForm(StyledFormMixin, forms.ModelForm):
    field_placeholders = {
        'title': 'Enter quiz title',
        'description': 'Add quiz description',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_common_styles()

    class Meta:
        model = Quiz
        fields = ['title', 'description']


class QuizQuestionForm(StyledFormMixin, forms.ModelForm):
    field_placeholders = {
        'question_text': 'Enter the question',
        'option_a': 'Option A',
        'option_b': 'Option B',
        'option_c': 'Option C',
        'option_d': 'Option D',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_common_styles()

    class Meta:
        model = QuizQuestion
        fields = ['question_text', 'option_a', 'option_b', 'option_c', 'option_d', 'correct_option']


class ProfileUpdateForm(StyledFormMixin, forms.ModelForm):
    field_placeholders = {
        'phone': 'Enter phone number',
        'bio': 'Write a short bio',
    }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._apply_common_styles()

    class Meta:
        model = Profile
        fields = ['phone', 'bio']
