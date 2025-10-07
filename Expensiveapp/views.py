from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from .models import users_register,Income,Feedback,Expense,Bill
from decimal import Decimal
from django.db.models import Sum, Count, Avg, Q
from django.db.models.functions import TruncMonth, TruncYear
from django.contrib import messages
import smtplib
import this
import razorpay
from datetime import datetime, timedelta, date
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import csv
import json
razorpay_client = razorpay.Client(
 auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))  # type: ignore

# Create your views here.
def index(request):
    # Get feedback data for testimonials with error handling
    try:
        feedback_data = Feedback.objects.all().order_by('-created_at')[:10]  # Get latest 10 feedback
        
        # Get total feedback count and average rating from all feedback
        total_feedback_count = Feedback.objects.count()
        avg_rating = Feedback.objects.aggregate(Avg('rating'))['rating__avg'] or 0
    except Exception as e:
        # Handle case where Feedback table doesn't exist yet
        feedback_data = []
        total_feedback_count = 0
        avg_rating = 0
    
    # Add username to each feedback object
    for feedback in feedback_data:
        feedback.username = feedback.email.split('@')[0] if '@' in feedback.email else feedback.email
    
    context = {
        'feedback_data': feedback_data,
        'avg_rating': round(avg_rating, 1),
        'total_feedback': total_feedback_count
    }
    return render(request, 'index.html', context)

# def settings(request):
    # return render(request,'settings.html')

def user_register(request):
    if request.method == "POST":
        firstname=request.POST.get('first_name')
        lastname=request.POST.get('last_name')
        email=request.POST.get('email_id')
        password=request.POST.get('password')
        confirm_password=request.POST.get('confirm_password')
        image=request.FILES.get('profile_image')
        phone=request.POST.get('phone')
        if users_register.objects.filter(email_id=email):
            alert="<script>alert('email id is already is exist');window.location.href='/login/';</script>"
            return HttpResponse(alert, content_type='text/html')
        obj=users_register(first_name=firstname,
            last_name=lastname,
            email_id=email,
            password=password,
            confirm_password=confirm_password,
            image=image,
            phone=phone)
        obj.save()
        return redirect('login')
    return render(request,'user_register.html')
def login(request):
    if request.method == "POST":
       email=request.POST.get('email_id')
       password=request.POST.get('password')

       try:
            us = users_register.objects.get(email_id=email, password=password)
            request.session['email'] = us.email_id
            return redirect('usershome')
       except users_register.DoesNotExist:
            msg = "Invalid user"
            return render(request, 'userlogin.html', {"msg": msg})
    return render(request,'userlogin.html')
def userprofile(request):
    if 'email' in request.session:
        mail=request.session['email']
        user=users_register.objects.get(email_id=mail)
    return render(request,'userprofile.html',{'user':user})
# Simple overview function removed - using the detailed overview function below
def userprofile_edit(request,eid):
    edt=users_register.objects.get(id=eid)
    if request.method=='POST':
       firstname=request.POST.get('first_name')
       lastname=request.POST.get('last_name')
       email=request.POST.get('email_id')
       password=request.POST.get('password')
       image=request.FILES.get('image')

       edt.first_name=firstname
       edt.last_name=lastname
       edt.email_id=email
       edt.password=password
       if image is not None:
           edt.image=image
       imagec=edt.image
       edt.image=imagec
       edt.save()
       return redirect("userprofile")  
    return render(request,'editprofile.html',{'edt':edt})
def admin_dashboard(request):
    return render(request,'admin.html')

def user_list(request):
    users = users_register.objects.all()
    return render(request, 'userlist.html', {'users': users})

def delete_user(request,did):
    x=users_register.objects.get(id=did)
    x.delete()
    return redirect('user_list')
#admin login 
def adminlogin(request):
    if request.method == 'POST':
        email=request.POST.get('email')
        password=request.POST.get('password')
        e='admin2024@gmail.com'
        p='admin@123'
        if email == e:
            if password==p:
                return render(request,'admin.html')
    return render(request,'adminlogin.html')

def feedback(request):
    if request.method == "POST":
        feedback_text = request.POST.get('feedback_text', '').strip()
        rating = request.POST.get('rating')
        email = request.POST.get('email', '').strip()

        # Check for missing fields
        if not feedback_text or not rating or not email:
            alert_message = "<script>alert('Please fill in all required fields (email, feedback text, and rating).'); window.location.href='/feedback_rate';</script>"
            return HttpResponse(alert_message, content_type='text/html')

        # Validate email format
        import re
        email_pattern = r'^[^\s@]+@[^\s@]+\.[^\s@]+$'
        if not re.match(email_pattern, email):
            alert_message = "<script>alert('Please enter a valid email address.'); window.location.href='/feedback_rate';</script>"
            return HttpResponse(alert_message, content_type='text/html')

        try:
            rating = int(rating)
            if rating not in [1, 2, 3, 4, 5]:
                raise ValueError("Invalid rating value")
        except (ValueError, TypeError):
            alert_message = "<script>alert('Invalid rating value. Please select a valid rating between 1 and 5.'); window.location.href='/feedback_rate';</script>"
            return HttpResponse(alert_message, content_type='text/html')

        try:
            # Create and save the Feedback instance
            feedback_instance = Feedback(
                feedback_text=feedback_text,
                rating=rating,
                email=email
            )
            feedback_instance.save()

            # Show a success message with JavaScript and reload the form
            success_message = "<script>alert('Feedback submitted successfully! Thank you for your valuable feedback.'); window.location.href='/feedback_rate';</script>"
            return HttpResponse(success_message, content_type='text/html')
        except Exception as e:
            # Handle any database errors
            alert_message = f"<script>alert('An error occurred while saving your feedback. Please try again.'); window.location.href='/feedback_rate';</script>"
            return HttpResponse(alert_message, content_type='text/html')

    # Render the feedback form for GET requests
    return render(request, 'feedback_rate.html')
def usershome(request):
    return render(request,'user.html')
#feedbacklist viewed by admin
def feedback_list_view(request):
    data=Feedback.objects.all()
    return render(request,'feedbacklist.html',{'data':data})
#feedback deleted by admin
def delete_feedbacks(request,did):
    x=Feedback.objects.get(id=did)
    x.delete()
    return redirect('feedbacklist')

#feedback viewed by others
from django.shortcuts import render
from .models import Feedback  # Make sure you import your Feedback model

def userfeedback_list_view(request):
    data = Feedback.objects.all()

    # Prepare stars for each feedback
    for feedback in data:
        feedback.stars = {
            'filled': '★' * feedback.rating,  # Using '★' for filled stars
            'empty': '☆' * (5 - feedback.rating)  # Using '☆' for empty stars
        }

    return render(request, 'userfeedback_list.html', {'data': data})


#user logout
def logout(request):
    request.session.flush()
    return redirect('index')



    
# adding income of user

from django.contrib import messages
from django.core.exceptions import ValidationError



def add_income(request, aid):
    user = users_register.objects.filter(id=aid).first()
    if request.method == 'POST':
        source = request.POST.get('source')
        amount = request.POST.get('amount')
        date = request.POST.get('date')

        if 'email' in request.session: 
            mail = request.session['email']
            
            try:
                register_instance = users_register.objects.get(email_id=mail)
            except users_register.DoesNotExist:
                messages.error(request, 'User does not exist. Please log in again.')
                return redirect('login')

            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValidationError("Income amount must be greater than zero.")
            except ValueError:
                messages.error(request, 'Invalid amount. Please enter a numeric value.')
                return render(request, 'add_income.html',{'user':user})

            # Validate date - should not be in the future
            from datetime import date as date_obj
            try:
                income_date = datetime.strptime(date, '%Y-%m-%d').date()
                if income_date > date_obj.today():
                    messages.error(request, 'Income date cannot be in the future. Please select today or a previous date.')
                    return render(request, 'add_income.html',{'user':user})
            except ValueError:
                messages.error(request, 'Invalid date format.')
                return render(request, 'add_income.html',{'user':user})

            # Create and save the Income instance
            income = Income(
                user=register_instance,
                source=source,
                amount=amount,
                date=date
            )
            income.save()
            messages.success(request, 'Income added successfully.')
            return redirect('usershome')  # Redirect to the user home page

    return render(request, 'add_income.html',{'user':user})


#delete income by user
def delete_income(request,did):
    x=Income.objects.get(id=did)
    x.delete()
    return redirect('view_income')


#add button to decide whether to add income or expense
def add(request):
    if 'email' in request.session:
        mail=request.session['email']
        user=users_register.objects.get(email_id=mail)
    return render(request, 'add.html',{'user':user})

#delete income by user
def delete_expense(request,did):
    x=Expense.objects.get(id=did)
    x.delete()
    return redirect('view_expense')


#user adding expense
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import Expense, users_register



def add_expense(request, aid):    
    user = users_register.objects.filter(id=aid).first()
    
    if not user:
        messages.error(request, "User does not exist.")
        return redirect('usershome') 
    
    if request.method == 'POST':
        category = request.POST.get('category')
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        date = request.POST.get('date')

        # Ensure the user is logged in via session (or handle another way)
        if 'email' in request.session:
            mail = request.session['email']

            try:
                # Fetch the user from the email in the session
                register_instance = users_register.objects.get(email_id=mail)
            except users_register.DoesNotExist:
                messages.error(request, 'User does not exist. Please log in again.')
                return redirect('login')

            try:
                # Validate the amount as a positive number
                amount = float(amount)
                if amount <= 0:
                    raise ValidationError("Expense amount must be greater than zero.")
            except ValueError:
                messages.error(request, 'Invalid amount. Please enter a numeric value.')
                return render(request, 'add_expense.html', {'user': user})

            # Validate date - should not be in the future
            from datetime import date as date_obj
            try:
                expense_date = datetime.strptime(date, '%Y-%m-%d').date()
                if expense_date > date_obj.today():
                    messages.error(request, 'Expense date cannot be in the future. Please select today or a previous date.')
                    return render(request, 'add_expense.html', {'user': user})
            except ValueError:
                messages.error(request, 'Invalid date format.')
                return render(request, 'add_expense.html', {'user': user})

            # Create and save the Expense instance
            expense = Expense(
                user=register_instance,  # Attach the user
                category=category,
                description=description,
                amount=amount,
                date=date
            )
            expense.save()  # Save to the database
            messages.success(request, 'Expense added successfully.')
            return redirect('usershome')  # Redirect to user home after saving

    return render(request, 'add_expense.html', {'user': user})

#view income or expense 
def view(request):
    if 'email' in request.session:
        mail=request.session['email']
        user=users_register.objects.get(email_id=mail)
    return render(request, 'view.html',{'user':user})


from django.shortcuts import render, get_object_or_404, redirect
from collections import defaultdict
from django.utils.dateformat import DateFormat
from .models import Income, users_register  # Adjust the import based on your actual models

def viewincome(request):
    if 'email' in request.session:
        mail = request.session['email']
        current_user = get_object_or_404(users_register, email_id=mail)

        # Filter income to show only previous and present dates (no future dates)
        from datetime import date as date_obj
        today = date_obj.today()
        income = Income.objects.filter(user=current_user, date__lte=today).order_by('date')
   
        incomes_by_month = defaultdict(list)
        for record in income:
            month = DateFormat(record.date).format('F Y')  
            incomes_by_month[month].append(record) 
            
       
        context = {
            'incomes_by_month': dict(incomes_by_month), 
        }
        
        return render(request, 'view_income.html', context)
    
    return redirect('add_income')

#user viewing his expense
from django.db.models.functions import TruncMonth
from collections import defaultdict

def viewexpense(request):
    if 'email' in request.session:
        mail = request.session['email']
        current_user = get_object_or_404(users_register, email_id=mail)

        # Filter expenses to show only previous and present dates (no future dates)
        from datetime import date as date_obj
        today = date_obj.today()
        expenses = Expense.objects.filter(user=current_user, date__lte=today).annotate(month=TruncMonth('date')).order_by('-date')
        
        # Organize expenses into a dictionary by month without totals
        expenses_by_month = defaultdict(list)
        
        for expense in expenses:
            month_key = expense.month.strftime('%B %Y')
            expenses_by_month[month_key].append(expense)

        return render(request, 'view_expense.html', {
            'expenses_by_month': dict(expenses_by_month),
        })
        
    return redirect('add_expense')




#view expense in pie chart
import json

def pie_chart(request, aid):
    user = users_register.objects.filter(id=aid).first()
    
    if not user:
        messages.error(request, "User does not exist.")
        return redirect('usershome') 

    # Filter expenses to show only previous and present dates (no future dates)
    from datetime import date as date_obj
    today = date_obj.today()
    
    # Aggregate expenses by category for the logged-in user
    expenses = Expense.objects.filter(user=user, date__lte=today)
    
    # Initialize dictionaries to hold the category labels and amounts
    expense_data = {}

    for expense in expenses:
        if expense.category in expense_data:
            expense_data[expense.category] += expense.amount
        else:
            expense_data[expense.category] = expense.amount

    # Prepare data for JSON serialization
    labels = list(expense_data.keys())
    amounts = [float(amount) for amount in expense_data.values()]

    # Check if there are no expenses and set a flag
    has_expenses = len(amounts) > 0

    # Render the pie chart template and pass the labels and amounts
    return render(request, 'pie.html', {
        'labels': json.dumps(labels),
        'amounts': json.dumps(amounts),
        'user': user,
        'has_expenses': has_expenses,  # Pass the flag to the template
    })


#overview of the income and expense

def overview(request, aid):
    user = users_register.objects.filter(id=aid).first()
    
    if not user:
        messages.error(request, "User does not exist.")
        return redirect('usershome')

    if 'email' not in request.session:
        messages.error(request, "You must be logged in to view your overview.")
        return redirect('login')

    mail = request.session['email']

    try:
        register_instance = users_register.objects.get(email_id=mail)
    except users_register.DoesNotExist:
        messages.error(request, 'User does not exist. Please log in again.')
        return redirect('login')


    # Filter income and expenses to show only previous and present dates (no future dates)
    from datetime import date as date_obj
    today = date_obj.today()
    income_sources = Income.objects.filter(user=register_instance, date__lte=today)
    expenses = Expense.objects.filter(user=register_instance, date__lte=today)

    total_income = sum(Decimal(income.amount) for income in income_sources)
    total_expenses = sum(Decimal(expense.amount) for expense in expenses)
    current_balance = total_income - total_expenses


    if total_expenses > total_income * Decimal(0.7):
        messages.warning(request, "Alert: Your expenses have exceeded 70% of your income!")

    recent_transactions = expenses.order_by('-date')[:5] 

    total_budget = Decimal(total_income)  
    used_budget = total_expenses
    remaining_budget = total_budget - used_budget

    context = {
        'user': user,
        'income_sources': income_sources,
        'expenses': expenses,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'current_balance': current_balance,
        'recent_transactions': recent_transactions,
        'used_budget': used_budget,
        'total_budget': total_budget,
        'remaining_budget': remaining_budget,
    }

    return render(request, 'overview.html', context)

#transaction history

def all_transactions(request, aid):
    user = users_register.objects.filter(id=aid).first()
    
    if not user:
        messages.error(request, "User does not exist.")
        return redirect('usershome')

    if 'email' not in request.session:
        messages.error(request, "You must be logged in to view your transactions.")
        return redirect('login')

    mail = request.session['email']

    try:
        register_instance = users_register.objects.get(email_id=mail)
    except users_register.DoesNotExist:
        messages.error(request, 'User does not exist. Please log in again.')
        return redirect('login')

    # Filter income and expenses to show only previous and present dates (no future dates)
    from datetime import date as date_obj
    today = date_obj.today()
    income_sources = Income.objects.filter(user=register_instance, date__lte=today).order_by('-date')
    expenses = Expense.objects.filter(user=register_instance, date__lte=today).order_by('-date')

    total_income = sum(Decimal(income.amount) for income in income_sources)
    total_expense = sum(Decimal(expense.amount) for expense in expenses)

    context = {
        'user': user,
        'income_sources': income_sources,
        'expenses': expenses,
        'total_income': total_income,
        'total_expense': total_expense,
    }

    return render(request, 'all_transactions.html', context)



#bar chart representation
import json
from django.shortcuts import render, redirect
from django.contrib import messages
from django.db.models import Sum
from calendar import month_name
from django.db.models.functions import ExtractMonth


def bar_chart(request, aid):
    user = users_register.objects.filter(id=aid).first()
    
    if not user:
        messages.error(request, "User does not exist.")
        return redirect('usershome') 

    # Filter expenses to show only previous and present dates (no future dates)
    from datetime import date as date_obj
    today = date_obj.today()
    
    # Aggregate expenses by month for the logged-in user
    expenses_by_month = (
        Expense.objects
        .filter(user=user, date__lte=today)
        .annotate(month=ExtractMonth('date'))  # Extract the month from the date field
        .values('month')
        .annotate(total_amount=Sum('amount'))
        .order_by('month')
    )

    # Prepare data for JSON serialization
    labels = [month_name[entry['month']] for entry in expenses_by_month]
    amounts = [float(entry['total_amount']) for entry in expenses_by_month]

    # Check if there are no expenses and set a flag
    has_expenses = len(amounts) > 0

    # Render the bar chart template and pass the labels and amounts
    return render(request, 'bar_chart.html', {
        'labels': json.dumps(labels),
        'amounts': json.dumps(amounts),
        'user': user,
        'has_expenses': has_expenses,  # Pass the flag to the template
    })

#user adding bill
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.core.exceptions import ValidationError
from .models import users_register, Bill

def add_bill(request, aid):
    user = get_object_or_404(users_register, id=aid)  # Use get_object_or_404 for cleaner code

    if request.method == 'POST':
        category = request.POST.get('category')
        custom_category = request.POST.get('customCategory')  
        description = request.POST.get('description')
        amount = request.POST.get('amount')
        due_date = request.POST.get('due_date')
        image = request.FILES.get('image') 

        # If the user chooses 'Other' as category and provides a custom category, use it.
        if category == "Other" and custom_category:
            category = custom_category

        # Check if user is in the session
        if 'email' in request.session:
            mail = request.session['email']
            
            try:
                # Get the user instance
                register_instance = users_register.objects.get(email_id=mail)
            except users_register.DoesNotExist:
                messages.error(request, 'User does not exist. Please log in again.')
                return redirect('login')
            
            # Validate and convert amount
            try:
                amount = float(amount)
                if amount <= 0:
                    raise ValidationError("Bill amount must be greater than zero.")
            except ValueError:
                messages.error(request, 'Invalid amount. Please enter a numeric value.')
                return render(request, 'add_bill.html', {'user': user})

            # Validate due date format
            try:
                from datetime import datetime, date as date_obj
                due_date_parsed = datetime.strptime(due_date, '%Y-%m-%d').date()
                
                # Due date can be in the future (that's normal for bills)
                # But we should validate it's not too far in the past (e.g., more than 1 year ago)
                one_year_ago = date_obj.today() - timedelta(days=365)
                if due_date_parsed < one_year_ago:
                    messages.error(request, 'Due date cannot be more than 1 year in the past.')
                    return render(request, 'add_bill.html', {'user': user})
                    
            except ValueError:
                messages.error(request, 'Invalid due date format.')
                return render(request, 'add_bill.html', {'user': user})

            # Create and save the Bill instance
            # Note: created_at will be automatically set to current timestamp by auto_now_add=True
            bill = Bill(
                user=register_instance,
                category=category,
                description=description,
                amount=amount,
                due_date=due_date_parsed,  # Use the parsed date object
                image=image,
                is_paid=False,  # Explicitly set to False when adding a new bill
                razorpay_order_id=None  # Initially, we may not have a Razorpay order ID
            )
            
            # Validate the bill using the model's clean method
            try:
                bill.full_clean()  # This calls the clean() method and validates the model
                bill.save()
                messages.success(request, 'Bill added successfully.')
                return redirect('usershome')
            except ValidationError as e:
                # Handle validation errors from the model
                for field, errors in e.message_dict.items():
                    for error in errors:
                        messages.error(request, f"{field}: {error}")
                return render(request, 'add_bill.html', {'user': user})

    return render(request, 'add_bill.html', {'user': user})




def view_bill(request):
    if 'email' in request.session:
        mail = request.session['email']
        current_user = get_object_or_404(users_register, email_id=mail)
        
        # Filter bills based on creation date (not due date) - show only bills created today or before
        from datetime import date as date_obj
        today = date_obj.today()
        bills = Bill.objects.filter(user=current_user, created_at__date__lte=today).order_by('-created_at')
        return render(request, 'view_bill.html', {'bills': bills})
    
    return redirect('add_bill')



#User searching for bill
def search_bills(request):
    query = request.GET.get('query', '')
    if 'email' in request.session:
        mail = request.session['email']
        current_user = get_object_or_404(users_register, email_id=mail)
        
        # Filter bills based on creation date (not due date) and search query
        from datetime import date as date_obj
        today = date_obj.today()
        
        if query:
            bills = Bill.objects.filter(
                user=current_user, 
                category__icontains=query,
                created_at__date__lte=today
            ).order_by('-created_at')
        else:
            bills = Bill.objects.filter(
                user=current_user,
                created_at__date__lte=today
            ).order_by('-created_at')
    else:
        bills = None  

    context = {
        'bills': bills,
    }
    return render(request, 'view_bill.html', context)


def delete_bill(request,bid):
    x=Bill.objects.get(id=bid)
    x.delete()
    return redirect('view_bill')

from django.shortcuts import get_object_or_404, render
from django.contrib import messages
from django.http import HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from .models import Bill, Payment  # Import your models
from django.conf import settings
import razorpay

# Initialize Razorpay client
razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))  # type: ignore

def payment(request, bill_id):
    # Get the bill for the user based on the provided bill_id
    bill = get_object_or_404(Bill, id=bill_id, user__email_id=request.session['email'])
    
    # Calculate the amount to be paid (convert to smallest currency unit, e.g., paise)
    amount = int(bill.amount * 100)  # Amount in paise
    
    # Create an order with Razorpay
    razorpay_order = razorpay_client.order.create({  # type: ignore
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '0'  # Set to '0' for manual capture
    })
    
    # Get the order ID
    razorpay_order_id = razorpay_order['id']

    # Prepare context for rendering the payment template
    context = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': amount,
        'currency': 'INR',
        'callback_url': '/paymenthandler/',  # Use the endpoint you will create
        'bill_id': bill_id  # Pass the bill ID to identify the bill after payment
    }
    
    # Save the razorpay_order_id to the bill instance
    bill.razorpay_order_id = razorpay_order_id
    bill.save()

    return render(request, 'payment.html', context=context)


@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')

            # Create a dictionary to verify the payment signature
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }

            # Verify the payment signature
            result = razorpay_client.utility.verify_payment_signature(params_dict)  # type: ignore

            if result is not None:
                # Fetch the bill associated with the razorpay_order_id
                bill = get_object_or_404(Bill, razorpay_order_id=razorpay_order_id)

                # Amount should match the bill amount
                amount = int(bill.amount * 100)  # Convert to paise

                # Capture the payment
                try:
                    razorpay_client.payment.capture(payment_id, amount)  # type: ignore

                    # Save payment details in Payment model
                    payment = Payment(
                        bill=bill,
                        payment_id=payment_id,
                        amount=bill.amount,
                        is_successful=True
                    )
                    payment.save()

                    # Mark the bill as paid
                    bill.is_paid = True
                    bill.save()

                    messages.success(request, "Payment successful!")
                    return render(request, 'pay_success.html')
                except Exception as e:
                    messages.error(request, f"Payment capture failed: {str(e)}")
                    return render(request, 'pay_failed.html')
            else:
                messages.error(request, "Payment verification failed.")
                return render(request, 'pay_failed.html')
        except Exception as e:
            messages.error(request, f"Error processing payment: {str(e)}")
            return HttpResponseBadRequest()
    else:
        return HttpResponseBadRequest()

def add_user_admin(request):
    if request.method == 'POST':
        firstname = request.POST.get('first_name')
        lastname = request.POST.get('last_name')
        email = request.POST.get('email_id')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        image = request.FILES.get('profile_image')
        phone = request.POST.get('phone')
        
        # Validation
        if not all([firstname, lastname, email, password, confirm_password]):
            messages.error(request, 'Please fill in all required fields.')
            return render(request, 'add_user_admin.html')
        
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'add_user_admin.html')
        
        if users_register.objects.filter(email_id=email).exists():
            messages.error(request, 'Email ID already exists.')
            return render(request, 'add_user_admin.html')
        
        # Create new user
        try:
            obj = users_register(
                first_name=firstname,
                last_name=lastname,
                email_id=email,
                password=password,
                confirm_password=confirm_password,
                image=image,
                phone=phone
            )
            obj.save()
            messages.success(request, f'User "{firstname} {lastname}" has been successfully created!')
            return redirect('user_list')
        except Exception as e:
            messages.error(request, f'Error creating user: {str(e)}')
            return render(request, 'add_user_admin.html')
    
    return render(request, 'add_user_admin.html')

# Admin Reports View
def admin_reports(request):
    # Get current date and calculate date ranges
    today = datetime.now().date()
    current_month = today.replace(day=1)
    current_year = today.replace(month=1, day=1)
    
    # Last 30 days
    last_30_days = today - timedelta(days=30)
    # Last 90 days
    last_90_days = today - timedelta(days=90)
    
    # User Statistics
    total_users = users_register.objects.count()
    new_users_this_month = users_register.objects.filter(
        id__in=users_register.objects.values_list('id', flat=True)[:10]  # Simulate new users
    ).count()
    
    # Financial Statistics - filter out future dates
    total_income = Income.objects.filter(date__lte=today).aggregate(total=Sum('amount'))['total'] or 0
    total_expenses = Expense.objects.filter(date__lte=today).aggregate(total=Sum('amount'))['total'] or 0
    total_bills = Bill.objects.aggregate(total=Sum('amount'))['total'] or 0
    paid_bills = Bill.objects.filter(is_paid=True).aggregate(total=Sum('amount'))['total'] or 0
    
    # Monthly trends (last 12 months) - filter out future dates
    monthly_income = Income.objects.filter(
        date__gte=current_year,
        date__lte=today
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    monthly_expenses = Expense.objects.filter(
        date__gte=current_year,
        date__lte=today
    ).annotate(
        month=TruncMonth('date')
    ).values('month').annotate(
        total=Sum('amount')
    ).order_by('month')
    
    # Category breakdown - filter out future dates
    expense_categories = Expense.objects.filter(date__lte=today).values('category').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:10]
    
    income_sources = Income.objects.filter(date__lte=today).values('source').annotate(
        total=Sum('amount'),
        count=Count('id')
    ).order_by('-total')[:10]
    
    # Bill statistics
    bill_categories = Bill.objects.values('category').annotate(
        total=Sum('amount'),
        count=Count('id'),
        paid_count=Count('id', filter=Q(is_paid=True))
    ).order_by('-total')
    
    # Feedback statistics
    total_feedback = Feedback.objects.count()
    avg_rating = Feedback.objects.aggregate(avg=Avg('rating'))['avg'] or 0
    rating_distribution = Feedback.objects.values('rating').annotate(
        count=Count('id')
    ).order_by('rating')
    
    # Recent activity - filter out future dates
    recent_expenses = Expense.objects.filter(date__lte=today).select_related('user').order_by('-date')[:10]
    recent_income = Income.objects.filter(date__lte=today).select_related('user').order_by('-date')[:10]
    recent_bills = Bill.objects.filter(created_at__date__lte=today).select_related('user').order_by('-created_at')[:10]
    recent_feedback = Feedback.objects.order_by('-created_at')[:10]
    
    # Top users by transaction volume
    top_users_expenses = users_register.objects.annotate(
        total_expenses=Sum('expense__amount'),
        expense_count=Count('expense')
    ).filter(total_expenses__isnull=False).order_by('-total_expenses')[:10]

    # Add avg_per_transaction to each user
    for user in top_users_expenses:
        if user.expense_count:
            user.avg_per_transaction = float(user.total_expenses) / user.expense_count
        else:
            user.avg_per_transaction = 0.0

    top_users_income = users_register.objects.annotate(
        total_income=Sum('income__amount'),
        income_count=Count('income')
    ).filter(total_income__isnull=False).order_by('-total_income')[:10]
    
    # Prepare chart data
    chart_data = {
        'monthly_income': list(monthly_income),
        'monthly_expenses': list(monthly_expenses),
        'expense_categories': list(expense_categories),
        'income_sources': list(income_sources),
        'rating_distribution': list(rating_distribution),
    }
    chart_data = convert_decimal(chart_data)
    context = {
        'total_users': total_users,
        'new_users_this_month': new_users_this_month,
        'total_income': total_income,
        'total_expenses': total_expenses,
        'total_bills': total_bills,
        'paid_bills': paid_bills,
        'monthly_income': monthly_income,
        'monthly_expenses': monthly_expenses,
        'expense_categories': expense_categories,
        'income_sources': income_sources,
        'bill_categories': bill_categories,
        'total_feedback': total_feedback,
        'avg_rating': round(avg_rating, 1),
        'rating_distribution': rating_distribution,
        'recent_expenses': recent_expenses,
        'recent_income': recent_income,
        'recent_bills': recent_bills,
        'recent_feedback': recent_feedback,
        'top_users_expenses': top_users_expenses,
        'top_users_income': top_users_income,
        'chart_data': json.dumps(chart_data),
        'current_month': current_month,
        'current_year': current_year,
        'last_30_days': last_30_days,
        'last_90_days': last_90_days,
    }
    
    return render(request, 'admin_reports.html', context)

def convert_decimal(obj):
    if isinstance(obj, list):
        return [convert_decimal(i) for i in obj]
    elif isinstance(obj, dict):
        return {k: convert_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, (date, datetime)):
        return obj.isoformat()
    elif hasattr(obj, '__iter__') and not isinstance(obj, (str, bytes, bytearray)):
        # Handle QuerySet and other iterable objects
        return [convert_decimal(i) for i in obj]
    return obj

def export_user_data(request):
    if 'email' not in request.session:
        return redirect('login')
    mail = request.session['email']
    try:
        user = users_register.objects.get(email_id=mail)
    except users_register.DoesNotExist:
        return redirect('login')

    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="user_profile_{user.id}.csv"'
    writer = csv.writer(response)
    writer.writerow(['First Name', 'Last Name', 'Email', 'Phone'])
    writer.writerow([user.first_name, user.last_name, user.email_id, getattr(user, 'phone', '')])
    return response

def export_user_data_page(request):
    if 'email' not in request.session:
        return redirect('login')
    return render(request, 'export_user_data.html')

def download_user_data(request):
    if 'email' not in request.session:
        return redirect('login')
    if request.method == 'GET':
        return render(request, 'download_user_data.html')
    if request.method != 'POST':
        return redirect('download_user_data')
    mail = request.session['email']
    try:
        user = users_register.objects.get(email_id=mail)
    except users_register.DoesNotExist:
        return redirect('login')

    # Prepare CSV response
    from io import StringIO
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="user_data_{user.id}.csv"'
    csvfile = StringIO()
    writer = csv.writer(csvfile)

    # Profile info (always included)
    writer.writerow(['Profile Information'])
    writer.writerow(['First Name', 'Last Name', 'Email', 'Phone'])
    writer.writerow([user.first_name, user.last_name, user.email_id, getattr(user, 'phone', '')])
    writer.writerow([])

    # Filter out future dates for exports
    from datetime import date as date_obj
    today = date_obj.today()
    
    # Expenses
    if request.POST.get('export_expenses'):
        writer.writerow(['Expenses'])
        writer.writerow(['Date', 'Amount', 'Category', 'Description'])
        expenses = Expense.objects.filter(user=user, date__lte=today)
        for exp in expenses:
            writer.writerow([getattr(exp, 'date', ''), getattr(exp, 'amount', ''), getattr(exp, 'category', ''), getattr(exp, 'description', '')])
        writer.writerow([])

    # Income
    if request.POST.get('export_income'):
        writer.writerow(['Income'])
        writer.writerow(['Date', 'Amount', 'Source', 'Description'])
        incomes = Income.objects.filter(user=user, date__lte=today)
        for inc in incomes:
            writer.writerow([getattr(inc, 'date', ''), getattr(inc, 'amount', ''), getattr(inc, 'source', ''), getattr(inc, 'description', '')])
        writer.writerow([])

    # Feedback
    if request.POST.get('export_feedback'):
        writer.writerow(['Feedback'])
        writer.writerow(['Date', 'Rating', 'Feedback Text'])
        feedbacks = Feedback.objects.filter(email=user.email_id)
        for fb in feedbacks:
            writer.writerow([getattr(fb, 'created_at', ''), getattr(fb, 'rating', ''), getattr(fb, 'feedback_text', '')])
        writer.writerow([])

    response.write(csvfile.getvalue())
    return response





