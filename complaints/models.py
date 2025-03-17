from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User
from django.db.models import Count
import hashlib
from datetime import timedelta


class StudentClass(models.Model):
    name = models.CharField(max_length=50)
    year = models.IntegerField()
    section = models.CharField(max_length=1)

    class Meta:
        unique_together = ["name", "year", "section"]

    def __str__(self):
        return f"{self.name} - Year {self.year} Section {self.section}"


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    roll_number = models.CharField(max_length=20, unique=True)

    def __str__(self):
        return f"Student - {self.student_class}"

    def get_anonymous_id(self):
        # Create a unique but anonymous identifier
        unique_string = f"{self.user.id}{self.roll_number}{self.student_class.id}"
        return hashlib.sha256(unique_string.encode()).hexdigest()[:10]

    def can_submit_complaint(self):
        # Check monthly limit (2 complaints)
        month_start = timezone.now() - timedelta(days=30)
        monthly_complaints = Complaint.objects.filter(
            anonymous_student_id=self.get_anonymous_id(), created_at__gte=month_start
        ).count()
        if monthly_complaints >= 2:
            return False, "Monthly limit reached (2 complaints per month)"

        # Check yearly limit (8 complaints)
        year_start = timezone.now() - timedelta(days=365)
        yearly_complaints = Complaint.objects.filter(
            anonymous_student_id=self.get_anonymous_id(), created_at__gte=year_start
        ).count()
        if yearly_complaints >= 8:
            return False, "Yearly limit reached (8 complaints per year)"

        return True, "You can submit a complaint"


class Complaint(models.Model):
    CATEGORY_CHOICES = [
        ("ACADEMIC", "Academic Issues"),
        ("INFRASTRUCTURE", "Infrastructure"),
        ("FACULTY", "Faculty Related"),
        ("ADMINISTRATION", "Administration"),
        ("OTHER", "Other"),
    ]

    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("IN_PROGRESS", "In Progress"),
        ("RESOLVED", "Resolved"),
        ("REJECTED", "Rejected"),
    ]

    VISIBILITY_CHOICES = [
        ("CLASS", "Class Only"),
        ("PUBLIC", "Public"),
    ]

    title = models.CharField(max_length=200)
    description = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="PENDING")
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    tracking_id = models.CharField(max_length=10, unique=True)
    admin_response = models.TextField(blank=True, null=True)
    student_class = models.ForeignKey(StudentClass, on_delete=models.CASCADE)
    visibility = models.CharField(
        max_length=10, choices=VISIBILITY_CHOICES, default="CLASS"
    )
    anonymous_student_id = models.CharField(max_length=10)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.tracking_id} - {self.title}"

    def get_vote_percentage(self):
        total_votes = self.votes.count()
        if total_votes == 0:
            return 0
        upvotes = self.votes.filter(vote_type=True).count()
        return (upvotes / total_votes) * 100

    def check_and_update_visibility(self):
        if self.visibility == "CLASS":
            vote_percentage = self.get_vote_percentage()
            total_class_students = Student.objects.filter(
                student_class=self.student_class
            ).count()
            total_votes = self.votes.count()

            # Only update if we have at least 60% participation and 60% positive votes
            if total_class_students > 0:
                participation_rate = (total_votes / total_class_students) * 100
                # Check if at least 60% of class has voted and 60% of votes are positive
                if participation_rate >= 60 and vote_percentage >= 60:
                    self.visibility = "PUBLIC"
                    self.save()
                    return True

        return False


class Vote(models.Model):
    anonymous_student_id = models.CharField(max_length=10)
    complaint = models.ForeignKey(
        Complaint, related_name="votes", on_delete=models.CASCADE
    )
    vote_type = models.BooleanField()  # True for upvote, False for downvote
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ["anonymous_student_id", "complaint"]

    def __str__(self):
        return f"Anonymous Vote on {self.complaint.tracking_id}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.complaint.check_and_update_visibility()
