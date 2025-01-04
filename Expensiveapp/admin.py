from django.contrib import admin
from .import models
# Register your models here.
admin.site.register(models.users_register)
admin.site.register(models.Feedback)
admin.site.register(models.Income)
admin.site.register(models.Expense)
admin.site.register(models.Bill)