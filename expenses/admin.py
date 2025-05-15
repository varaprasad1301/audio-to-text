from django.contrib import admin

# Register your models here.
from .models import Expense

@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ('description', 'amount', 'created_at')  # Show these fields in admin list view
    search_fields = ('description',)  # Optional: Add search by description
    ordering = ('-created_at',)     
    change_form_template = 'admin/expense_add_form.html'

