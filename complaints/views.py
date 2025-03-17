from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LoginView
from django.urls import reverse_lazy
from django.views.generic import CreateView
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from .models import Complaint, Vote, Student, StudentClass
from .forms import ComplaintForm, VoteForm, CustomUserCreationForm, StudentProfileForm
import random
import string


def generate_tracking_id():
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=8))


def home(request):
    # Show public complaints and class-specific complaints if user is logged in
    complaints = Complaint.objects.filter(visibility="PUBLIC")

    has_student_profile = False
    if request.user.is_authenticated:
        try:
            student = request.user.student
            has_student_profile = True
            class_complaints = Complaint.objects.filter(
                student_class=student.student_class, visibility="CLASS"
            )
            # Use | to combine querysets
            complaints = (complaints | class_complaints).distinct()
        except Student.DoesNotExist:
            # User is authenticated but not a student
            pass

    # Ensure we order the complaints by creation date
    complaints = complaints.order_by("-created_at")
    return render(
        request,
        "complaints/home.html",
        {"complaints": complaints, "has_student_profile": has_student_profile},
    )


@login_required
def submit_complaint(request):
    # Check if student profile exists
    has_student_profile = False
    try:
        student = request.user.student
        has_student_profile = True
    except Student.DoesNotExist:
        messages.error(
            request, "You must be registered as a student to submit complaints."
        )
        return redirect("home")

    # Check if student can submit a complaint
    can_submit, message = student.can_submit_complaint()
    if not can_submit:
        messages.error(request, message)
        return redirect("home")

    if request.method == "POST":
        form = ComplaintForm(request.POST)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.tracking_id = generate_tracking_id()
            complaint.student_class = student.student_class
            complaint.anonymous_student_id = student.get_anonymous_id()
            complaint.save()
            messages.success(
                request,
                f"Your complaint has been submitted successfully! Your tracking ID is {complaint.tracking_id}",
            )
            return redirect("track_complaint")
    else:
        form = ComplaintForm()
    return render(
        request,
        "complaints/submit_complaint.html",
        {"form": form, "has_student_profile": has_student_profile},
    )


def track_complaint(request):
    has_student_profile = False
    if request.user.is_authenticated:
        try:
            request.user.student
            has_student_profile = True
        except Student.DoesNotExist:
            pass

    complaint = None

    # Check if tracking ID is in GET parameters (from direct link)
    tracking_id = request.GET.get("tracking_id")

    # If not in GET, try to get from POST (from form submission)
    if not tracking_id and request.method == "POST":
        tracking_id = request.POST.get("tracking_id")

    if tracking_id:
        try:
            complaint = Complaint.objects.get(tracking_id=tracking_id)
            # Check if user has permission to view this complaint
            if complaint.visibility == "CLASS":
                if not request.user.is_authenticated:
                    messages.error(
                        request, "You don't have permission to view this complaint."
                    )
                    complaint = None
                else:
                    try:
                        student = request.user.student
                        if student.student_class != complaint.student_class:
                            messages.error(
                                request,
                                "You don't have permission to view this complaint.",
                            )
                            complaint = None
                    except Student.DoesNotExist:
                        messages.error(
                            request, "You don't have permission to view this complaint."
                        )
                        complaint = None
        except Complaint.DoesNotExist:
            messages.error(request, "Invalid tracking ID. Please try again.")

    return render(
        request,
        "complaints/track_complaint.html",
        {"complaint": complaint, "has_student_profile": has_student_profile},
    )


@login_required
def vote_complaint(request, complaint_id):
    # Check if student profile exists
    has_student_profile = False
    try:
        # Verify the user is a student
        student = request.user.student
        has_student_profile = True

        complaint = get_object_or_404(Complaint, id=complaint_id)

        # Check if student is in the same class
        if student.student_class != complaint.student_class:
            messages.error(request, "You can only vote on complaints from your class.")
            return redirect("home")

        # Check if complaint is still in CLASS visibility mode
        if complaint.visibility != "CLASS":
            messages.error(
                request,
                "This complaint has already been made public and can no longer be voted on.",
            )
            return redirect("home")

        # Get anonymous ID for the student
        anonymous_id = student.get_anonymous_id()

        if request.method == "POST":
            vote_type_raw = request.POST.get("vote_type")
            if vote_type_raw not in ["upvote", "downvote"]:
                messages.error(request, "Invalid vote type.")
                return redirect("home")

            vote_type = vote_type_raw == "upvote"

            # Check if student has already voted
            existing_vote = Vote.objects.filter(
                anonymous_student_id=anonymous_id, complaint=complaint
            ).first()
            if existing_vote:
                if existing_vote.vote_type != vote_type:
                    existing_vote.vote_type = vote_type
                    existing_vote.save()
                    messages.success(request, "Your vote has been updated.")
                else:
                    messages.info(request, "You have already voted this way.")
            else:
                Vote.objects.create(
                    anonymous_student_id=anonymous_id,
                    complaint=complaint,
                    vote_type=vote_type,
                )
                messages.success(request, "Your vote has been recorded.")

            # Check if complaint should be made public
            complaint.check_and_update_visibility()
        else:
            messages.error(request, "Invalid request method.")

    except Student.DoesNotExist:
        messages.error(request, "You must be registered as a student to vote.")
    except Complaint.DoesNotExist:
        messages.error(
            request, "The complaint you are trying to vote on does not exist."
        )
    except Exception as e:
        messages.error(
            request, f"An error occurred while processing your vote: {str(e)}"
        )

    return redirect("home")


# Custom register view that redirects authenticated users
class CustomRegisterView(CreateView):
    template_name = "complaints/auth/register.html"
    form_class = CustomUserCreationForm
    success_url = reverse_lazy("student_profile")

    @method_decorator(never_cache)
    def dispatch(self, request, *args, **kwargs):
        # Redirect authenticated users
        if request.user.is_authenticated:
            # If the user already has a profile, take them to home
            try:
                request.user.student
                messages.info(
                    request, "You are already logged in and have a student profile."
                )
                return redirect("home")
            # If they don't have a profile yet, direct them to complete it
            except:
                messages.info(request, "Please complete your student profile.")
                return redirect("student_profile")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_student_profile"] = False
        # Check if the user is authenticated and has a student profile
        if self.request.user.is_authenticated:
            try:
                self.request.user.student
                context["has_student_profile"] = True
            except Student.DoesNotExist:
                pass
        return context

    def form_valid(self, form):
        # Save the user
        user = form.save()
        username = form.cleaned_data.get("username")
        messages.success(
            self.request,
            f"Account created for {username}! Please complete your student profile.",
        )

        # Log the user in
        raw_password = form.cleaned_data.get("password1")
        user = authenticate(username=username, password=raw_password)
        login(self.request, user)

        return redirect("student_profile")


@login_required
def student_profile(request):
    # Check if student profile already exists
    has_student_profile = False
    try:
        request.user.student
        has_student_profile = True
        messages.info(request, "You already have a student profile.")
        return redirect("home")
    except Student.DoesNotExist:
        pass

    # Check if there are any student classes available
    if StudentClass.objects.count() == 0:
        # Create sample classes if none exist
        sample_classes = [
            {"name": "Computer Science", "year": 1, "section": "A"},
            {"name": "Computer Science", "year": 2, "section": "A"},
            {"name": "Computer Science", "year": 3, "section": "A"},
            {"name": "Computer Science", "year": 4, "section": "A"},
            {"name": "Electronics", "year": 1, "section": "B"},
            {"name": "Electronics", "year": 2, "section": "B"},
            {"name": "Mechanical", "year": 1, "section": "C"},
            {"name": "Civil", "year": 1, "section": "D"},
        ]
        for cls in sample_classes:
            StudentClass.objects.create(
                name=cls["name"], year=cls["year"], section=cls["section"]
            )
        messages.info(
            request, "Sample student classes have been created for demonstration."
        )

    if request.method == "POST":
        form = StudentProfileForm(request.POST)
        if form.is_valid():
            student = form.save(commit=False)
            student.user = request.user
            student.save()
            messages.success(
                request, "Your student profile has been created successfully!"
            )
            return redirect("home")
    else:
        form = StudentProfileForm()

    return render(
        request,
        "complaints/auth/student_profile.html",
        {"form": form, "has_student_profile": has_student_profile},
    )


@login_required
def my_complaints(request):
    has_student_profile = False
    complaints = []

    try:
        # Verify the user is a student
        student = request.user.student
        has_student_profile = True

        # Get complaints submitted by this student
        anonymous_id = student.get_anonymous_id()
        complaints = Complaint.objects.filter(
            anonymous_student_id=anonymous_id
        ).order_by("-created_at")

        if not complaints:
            messages.info(request, "You haven't submitted any complaints yet.")

    except Student.DoesNotExist:
        messages.warning(request, "You need to complete your student profile first.")

    return render(
        request,
        "complaints/my_complaints.html",
        {"complaints": complaints, "has_student_profile": has_student_profile},
    )


# Custom login view that redirects authenticated users
class CustomLoginView(LoginView):
    template_name = "complaints/auth/login.html"
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("home")

    def dispatch(self, request, *args, **kwargs):
        # If user is already authenticated, redirect them
        if self.request.user.is_authenticated:
            return redirect(self.get_success_url())
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["has_student_profile"] = False
        # Check if the user is authenticated and has a student profile
        if self.request.user.is_authenticated:
            try:
                self.request.user.student
                context["has_student_profile"] = True
            except Student.DoesNotExist:
                pass
        return context
