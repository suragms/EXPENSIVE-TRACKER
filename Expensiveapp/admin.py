"""
Expense App Admin Configuration
Author: Surag
Description: This file configures the Django admin interface for the Expense App,
providing customized views and functionality for managing users, feedback,
income, expenses, bills, and payments.
"""

from django.contrib import admin
from .models import users_register, Feedback, Income, Expense, Bill, Payment


# Custom Admin for users_register
@admin.register(users_register)
class UsersRegisterAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name', 'email_id', 'phone', 'image')
    search_fields = ('first_name', 'last_name', 'email_id')
    list_filter = ('email_id',)
    ordering = ('first_name',)
    fieldsets = (
        (None, {
            'fields': ('first_name', 'last_name', 'email_id', 'phone', 'image')
        }),
        ('Authentication', {
            'fields': ('password', 'confirm_password'),
            'description': 'Manage user authentication details.',
        }),
    )
    readonly_fields = ('password', 'confirm_password')  # Prevent editing passwords directly
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related()


# Custom Admin for Feedback
@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ('email', 'rating', 'created_at', 'feedback_text_preview')
    search_fields = ('email', 'feedback_text')
    list_filter = ('rating', 'created_at')
    ordering = ('-created_at',)
    date_hierarchy = 'created_at'
    list_per_page = 25

    def feedback_text_preview(self, obj):
        """Display a truncated version of feedback text."""
        return obj.feedback_text[:50] + '...' if len(obj.feedback_text) > 50 else obj.feedback_text

    feedback_text_preview.short_description = 'Feedback Preview'


# Custom Admin for Income
@admin.register(Income)
class IncomeAdmin(admin.ModelAdmin):
    list_display = ('user', 'source', 'amount', 'date')
    search_fields = ('user__first_name', 'user__email_id', 'source')
    list_filter = ('date', 'source')
    date_hierarchy = 'date'
    ordering = ('-date',)
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Custom Admin for Expense
@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'date', 'description_preview')
    search_fields = ('user__first_name', 'user__email_id', 'category', 'description')
    list_filter = ('category', 'date')
    date_hierarchy = 'date'
    ordering = ('-date',)
    list_per_page = 25

    def description_preview(self, obj):
        """Display a truncated version of expense description."""
        return obj.description[:50] + '...' if obj.description and len(obj.description) > 50 else obj.description or ''

    description_preview.short_description = 'Description'

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Custom Admin for Bill
@admin.register(Bill)
class BillAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'due_date', 'is_paid', 'created_at')
    search_fields = ('user__first_name', 'user__email_id', 'category', 'description')
    list_filter = ('category', 'is_paid', 'due_date')
    date_hierarchy = 'due_date'
    ordering = ('-due_date',)
    list_per_page = 25
    actions = ['mark_as_paid', 'mark_as_unpaid']

    def mark_as_paid(self, request, queryset):
        """Custom action to mark selected bills as paid."""
        queryset.update(is_paid=True)
        self.message_user(request, "Selected bills have been marked as paid.")

    mark_as_paid.short_description = "Mark selected bills as paid"

    def mark_as_unpaid(self, request, queryset):
        """Custom action to mark selected bills as unpaid."""
        queryset.update(is_paid=False)
        self.message_user(request, "Selected bills have been marked as unpaid.")

    mark_as_unpaid.short_description = "Mark selected bills as unpaid"

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


# Custom Admin for Payment
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('payment_id', 'bill', 'amount', 'currency', 'is_successful', 'created_at')
    search_fields = ('payment_id', 'bill__user__first_name', 'bill__user__email_id')
    list_filter = ('is_successful', 'currency', 'created_at')
    date_hierarchy = 'created_at'
    ordering = ('-created_at',)
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('bill__user')