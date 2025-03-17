from django.urls import path
from . import views

urlpatterns = [
    path("", views.home, name="home"),
    path("submit/", views.submit_complaint, name="submit_complaint"),
    path("track/", views.track_complaint, name="track_complaint"),
    path("vote/<int:complaint_id>/", views.vote_complaint, name="vote_complaint"),
    path("student-profile/", views.student_profile, name="student_profile"),
    path("my-complaints/", views.my_complaints, name="my_complaints"),
]
