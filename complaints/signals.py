# complaints/signals.py
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Complaint, StatusUpdate

@receiver(pre_save, sender=Complaint)
def create_status_update(sender, instance, **kwargs):
    # If this is a new complaint, there's no previous status to compare to.
    if not instance.pk:
        return

    try:
        previous = Complaint.objects.get(pk=instance.pk)
    except Complaint.DoesNotExist:
        return

    if previous.status != instance.status:
        StatusUpdate.objects.create(
            complaint=instance,
            updated_by=instance.user,  # Make sure this is set properly
            new_status=instance.status,
            note=f"Status changed from {previous.status} to {instance.status}"
        )
# complaints/signals.py

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Complaint
from utils.genai import get_tone, get_priority, generate_auto_response, model


@receiver(post_save, sender=Complaint)
def enrich_complaint_with_ai(sender, instance, created, **kwargs):
    if created:  # Only on creation
        instance.tone = get_tone(instance.description)
        instance.priority = get_priority(instance.description)
        instance.priority = extract_priority(instance.description)

        instance.auto_response = generate_auto_response(instance.description)
        instance.save()
def extract_priority(description):
    prompt = f"""Classify this complaint description into a priority from 1 (least urgent) to 5 (most urgent). Only return the number.
Complaint: {description}"""

    try:
        response = model.generate_content(prompt)  # Ensure genai_client is properly initialized in utils.genai
        priority_str = response.get("text", "").strip()
        # Filter only digits and ensure it's between 1–5
        for char in priority_str:
            if char.isdigit():
                priority = int(char)
                if 1 <= priority <= 5:
                    return priority
    except Exception as e:
        print("Priority GenAI Error:", e)
    return 3  # Default medium priority
# complaints/signals.py

from django.core.mail import send_mail
from django.conf import settings

@receiver(post_save, sender=Complaint)
def send_complaint_created_email(sender, instance, created, **kwargs):
    if created and instance.user.email:
        subject = f"Complaint Registered (ID: {instance.id})"
        message = f"""
Dear {instance.user.username},

Your complaint has been registered successfully.

Details:
- ID: {instance.id}
- Category: {instance.category}
- Description: {instance.description}
- Status: {instance.status}

You can track your complaint in your account.

Regards,
SmartComplaint System
"""
        send_mail(subject, message, settings.EMAIL_HOST_USER, [instance.user.email])

@receiver(post_save, sender=StatusUpdate)
def send_status_update_email(sender, instance, created, **kwargs):
    complaint = instance.complaint
    if created and complaint.user.email:
        subject = f"Complaint Status Updated (ID: {complaint.id})"
        message = f"""
Dear {complaint.user.username},

Your complaint has been updated.

New Status: {instance.new_status}
Note: {instance.note or 'No additional notes'}

You can check further details in your account.

Regards,
SmartComplaint System
"""
        send_mail(subject, message, settings.EMAIL_HOST_USER, [complaint.user.email])
