from django.contrib import admin
from django.core.mail import send_mail
from django.conf import settings
import csv
from django.http import HttpResponse
from django.utils.html import format_html
from .models import User, Complaint, StatusUpdate, Officer
from utils.ai_helper import summarize_text, suggest_category
from django.contrib.auth.models import AbstractUser

@admin.register(User)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role')
    list_filter = ('role',)
    search_fields = ('username', 'email')


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ['category', 'short_suggested_category', 'short_summary', 'status', 'user','tone', 'tone_emoji','is_seen', 'assigned_to', 'created_at','flagged_toxic']
    readonly_fields = ('tone', 'priority', 'auto_response')
    list_filter = ['is_seen', 'status', 'category']
    search_fields = ['description', 'address']
    actions = ['mark_as_seen','export_as_csv','regenerate_ai_fields']
        # Truncate summary for display
    def short_summary(self, obj):
        return format_html('<div style="max-width: 250px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{}</div>', obj.summary or '')

    short_summary.short_description = 'Summary'
    def flagged_toxic(self, obj):
        return "⚠️ Toxic" if obj.is_toxic_content else "✅ Clean"
    flagged_toxic.short_description = "Toxic Content"

    # Truncate suggested category
    def short_suggested_category(self, obj):
        return format_html('<div style="max-width: 100px; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;">{}</div>', obj.suggested_category or '')

    short_suggested_category.short_description = 'Suggested Category'
    
    def mark_as_seen(self, request, queryset):
        queryset.update(is_seen=True)
    mark_as_seen.short_description = "Mark selected complaints as seen"

    def save_model(self, request, obj, form, change):
        is_new_assignment = change and 'assigned_to' in form.changed_data
        super().save_model(request, obj, form, change)
        if is_new_assignment:
            self.send_assignment_email(obj)
        if not obj.summary:
            obj.summary = summarize_text(obj.description)
        if not obj.suggested_category:
            obj.suggested_category = suggest_category(obj.description)
        super().save_model(request, obj, form, change)
    @admin.action(description="Regenerate AI Summary and Suggested Category")
    def regenerate_ai_fields(self, request, queryset):
        for complaint in queryset:
            complaint.summary = summarize_text(complaint.description)
            complaint.save()
            
    def send_assignment_email(self, complaint):
        officer = complaint.assigned_to
        if officer and officer.user and officer.user.email:
            subject = f"New Complaint Assigned (ID: {complaint.id})"
            message = f"""
Dear {officer.user.username},

A new complaint has been assigned to you.

Complaint Details:
- ID: {complaint.id}
- Category: {complaint.category}
- Description: {complaint.description}
- Date: {complaint.created_at.strftime('%Y-%m-%d %H:%M')}

Please take the necessary action via the admin panel.

Regards,
SmartComplaint System
"""
            send_mail(
                subject,
                message,
                settings.EMAIL_HOST_USER,
                [officer.user.email],
                fail_silently=False
            )
    def export_as_csv(self, request, queryset):
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename=complaints.csv'
        writer = csv.writer(response)
        writer.writerow(['ID', 'User', 'Category', 'Status', 'Assigned To', 'Created At', 'Address', 'Description'])

        for complaint in queryset:
            writer.writerow([
                complaint.id,
                complaint.user.username,
                complaint.category,
                complaint.status,
                complaint.assigned_to.user.username if complaint.assigned_to else '',
                complaint.created_at.strftime('%Y-%m-%d %H:%M'),
                complaint.address,
                complaint.description,
            ])
        return response

    export_as_csv.short_description = "Export selected complaints to CSV"
            

@admin.register(StatusUpdate)
class StatusUpdateAdmin(admin.ModelAdmin):
    list_display = ['complaint', 'new_status', 'updated_by', 'timestamp']
    list_filter = ['new_status', 'timestamp']
    search_fields = ['note', 'complaint__description']

@admin.register(Officer)

class OfficerAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge_number', 'department', 'created_at']
    search_fields = ['user__username', 'badge_number']
    autocomplete_fields = ['user']
