from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Complaint, StatusUpdate
from .forms import ComplaintForm, StatusUpdateForm, CustomUserCreationForm

def home(request):
    return render(request, 'complaints/base.html')


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = CustomUserCreationForm()
    return render(request, 'complaints/register.html', {'form': form})

@login_required
def complaint_form(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            return redirect('home')
    else:
        form = ComplaintForm()
    return render(request, 'complaints/complaint_form.html', {'form': form})

@login_required
def my_complaints(request):
    complaints = Complaint.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'complaints/my_complaints.html', {'complaints': complaints})

@login_required
def complaint_detail(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id, user=request.user)
    return render(request, 'complaints/complaint_detail.html', {'complaint': complaint})

def is_admin(user):
    return user.is_authenticated and user.role == 'admin'

@login_required
@user_passes_test(is_admin)
def update_status(request, complaint_id):
    complaint = get_object_or_404(Complaint, id=complaint_id)
    if request.method == 'POST':
        form = StatusUpdateForm(request.POST)
        if form.is_valid():
            status_update = form.save(commit=False)
            status_update.complaint = complaint
            status_update.updated_by = request.user
            status_update.save()

            complaint.status = status_update.new_status
            complaint.save()

            return redirect('admin-dashboard')
    else:
        form = StatusUpdateForm()
    return render(request, 'complaints/update_status.html', {'form': form, 'complaint': complaint})

@login_required
def submit_complaint(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save(commit=False)
            complaint.user = request.user
            complaint.save()
            return redirect('complaint_success')
    else:
        form = ComplaintForm()
    return render(request, 'complaints/submit_complaint.html', {'form': form})
from datetime import timedelta

def get_resolution_time(complaint):
    if complaint.status == 'Resolved' and complaint.resolved_at:
        return complaint.resolved_at - complaint.created_at
    return None
@login_required
def filter_complaints(request):
    complaints = Complaint.objects.all()
    status_filter = request.GET.get('status')
    category_filter = request.GET.get('category')

    if status_filter:
        complaints = complaints.filter(status=status_filter)
    if category_filter:
        complaints = complaints.filter(category=category_filter)

    return render(request, 'complaints/filtered_complaints.html', {'complaints': complaints})
