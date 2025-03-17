from django import forms
from .models import Complaint, Vote, StudentClass, Student
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User


class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ["title", "description", "category"]
        widgets = {
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Enter a brief title for your complaint",
                }
            ),
            "description": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 5,
                    "placeholder": "Describe your complaint in detail",
                }
            ),
            "category": forms.Select(attrs={"class": "form-control"}),
        }


class VoteForm(forms.ModelForm):
    class Meta:
        model = Vote
        fields = ["vote_type"]
        widgets = {"vote_type": forms.HiddenInput()}


class StudentProfileForm(forms.ModelForm):
    class Meta:
        model = Student
        fields = ["student_class", "roll_number"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["student_class"].widget.attrs.update({"class": "form-select"})
        self.fields["student_class"].label = "Select Your Class"
        self.fields["student_class"].empty_label = "-- Select Class --"
        self.fields["roll_number"].widget.attrs.update({"class": "form-control"})
        self.fields["roll_number"].label = "Roll Number"
        self.fields["roll_number"].help_text = (
            "Enter your unique roll number or student ID"
        )


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]
