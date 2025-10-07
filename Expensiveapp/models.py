from django.db import models
from django.core.exceptions import ValidationError
from django.utils import timezone


# Create your models here.
class users_register(models.Model):
    first_name=models.CharField(max_length=100,null=True)
    last_name=models.CharField(max_length=100,null=True)
    email_id=models.EmailField(unique=True,null=True,blank=True)
    password=models.CharField(max_length=100,null=True,blank=True)
    confirm_password=models.CharField(max_length=100,null=True,blank=True)
    image=models.ImageField(upload_to='media',null=True,blank=True)
    phone=models.IntegerField(null=True,blank=True)

    def __str__(self):
        return str(self.first_name)

class Feedback(models.Model):
    RATING_CHOICES = [
    (1, '1'),
    (2, '2'),
    (3, '3'),
    (4, '4'),
    (5, '5'),
    ]
    feedback_text = models.TextField()
    rating = models.IntegerField(choices=RATING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    email=models.EmailField()
    def __str__(self):
        return self.email
    
class Income(models.Model):
    user = models.ForeignKey(users_register, on_delete=models.CASCADE)
    source = models.CharField(max_length=100,null=True,blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    def __str__(self):
        return self.user.first_name
    


class Expense(models.Model):
    user = models.ForeignKey(users_register, on_delete=models.CASCADE) 
    category = models.CharField(max_length=150) 
    description = models.TextField(null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)

    def clean(self):
        if self.amount <= 0:
            raise ValidationError("Expense amount must be greater than zero.")

    def __str__(self):
        return self.user.first_name
    



class Bill(models.Model):
    CATEGORY_CHOICES = [
        ('Electricity', 'Electricity'),
        ('Water', 'Water'),
        ('Internet', 'Internet'),
        ('Rent', 'Rent'),
        ('Other', 'Other'),
    ]

    user = models.ForeignKey(users_register, on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    description = models.TextField(blank=True, null=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)  # Automatically set when bill is created
    image = models.ImageField(upload_to='bill_images/', blank=True, null=True)
    is_paid = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(max_length=255, null=True, blank=True) 

    def clean(self):
        """Validate bill data"""
        if self.amount <= 0:
            raise ValidationError("Bill amount must be greater than zero.")
        
        # Validate due date is not too far in the past
        from datetime import date, timedelta
        if self.due_date < date.today() - timedelta(days=365):
            raise ValidationError("Due date cannot be more than 1 year in the past.")

    def __str__(self):
        return f"{self.user.first_name}'s Bill - {self.category} ({self.amount})"
    
    
from django.db import models
from django.conf import settings

class Payment(models.Model):
    bill = models.ForeignKey(Bill, on_delete=models.CASCADE)
    payment_id = models.CharField(max_length=255) 
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=10, default='INR')
    is_successful = models.BooleanField(default=False)  
    created_at = models.DateTimeField(auto_now_add=True) 
    updated_at = models.DateTimeField(auto_now=True) 

    def __str__(self):
        return f"Payment {self.payment_id} for Bill {self.bill.id} - {'Successful' if self.is_successful else 'Failed'}"




    

   
    

