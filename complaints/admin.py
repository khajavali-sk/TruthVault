from django.contrib import admin
from .models import StudentClass, Student, Complaint, Vote


@admin.register(StudentClass)
class StudentClassAdmin(admin.ModelAdmin):
    list_display = ("name", "year", "section")
    search_fields = ("name", "year", "section")
    list_filter = ("year",)


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display = ("user", "student_class", "roll_number")
    search_fields = ("user__username", "roll_number")
    list_filter = ("student_class",)


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = (
        "tracking_id",
        "title",
        "category",
        "status",
        "student_class",
        "visibility",
        "created_at",
        "anonymous_student_id",
    )
    list_filter = ("category", "status", "visibility", "student_class")
    search_fields = ("title", "description", "tracking_id", "anonymous_student_id")
    readonly_fields = (
        "tracking_id",
        "created_at",
        "updated_at",
        "anonymous_student_id",
    )


@admin.register(Vote)
class VoteAdmin(admin.ModelAdmin):
    list_display = ("anonymous_student_id", "complaint", "vote_type", "created_at")
    list_filter = ("vote_type", "created_at")
    search_fields = (
        "anonymous_student_id",
        "complaint__title",
        "complaint__tracking_id",
    )
    readonly_fields = ("anonymous_student_id",)
