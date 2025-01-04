from django.shortcuts import render,redirect,HttpResponse,get_object_or_404
from .models import users_register,Income,Feedback,Expense,Bill
from decimal import Decimal
from django.db.models import Sum
from django.db.models.functions import TruncMonth
from django.contrib import messages
import smtplib
import this
import razorpay
from datetime import datetime
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
razorpay_client = razorpay.Client(
 auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

# Create your views here.
def index(request):
    return render(request,'index.html')

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
            return HttpResponse(alert)
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
def overview(request):
    return render(request,'overview.html')
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
        feedback_text = request.POST.get('feedback_text')
        rating = request.POST.get('rating')
        email = request.POST.get('email')  # Get the email field

        # Check for missing fields
        if not feedback_text or not rating or not email:
            alert_message = "<script>alert('Please fill in all required fields.'); window.location.href='/feedback_rate';</script>"
            return HttpResponse(alert_message)

        try:
            rating = int(rating)
            if rating not in [1, 2, 3, 4, 5]:
                raise ValueError("Invalid rating value")
        except (ValueError, TypeError):
            alert_message = "<script>alert('Invalid rating value. Please select a valid rating.'); window.location.href='/feedback_rate';</script>"
            return HttpResponse(alert_message)

        # Create and save the Feedback instance
        feedback_instance = Feedback(
            feedback_text=feedback_text,
            rating=rating,
            email=email  # Save the email
        )
        feedback_instance.save()

        # Show a success message with JavaScript and reload the form
        success_message = "<script>alert('Feedback submitted successfully! Thank you for using our website! We’d post your valuable feedback and suggestions'); window.location.href='/feedback_rate';</script>"
        return HttpResponse(success_message)

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

        income = Income.objects.filter(user=current_user).order_by('date')
   
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

        # Fetch expenses and annotate each with its month, then order by date
        expenses = Expense.objects.filter(user=current_user).annotate(month=TruncMonth('date')).order_by('-date')
        
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

    # Aggregate expenses by category for the logged-in user
    expenses = Expense.objects.filter(user=user)
    
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


    income_sources = Income.objects.filter(user=register_instance)


    expenses = Expense.objects.filter(user=register_instance)

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

    income_sources = Income.objects.filter(user=register_instance).order_by('-date')
    expenses = Expense.objects.filter(user=register_instance).order_by('-date')

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

    # Aggregate expenses by month for the logged-in user
    expenses_by_month = (
        Expense.objects
        .filter(user=user)
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

            # Create and save the Bill instance
            bill = Bill(
                user=register_instance,
                category=category,
                description=description,
                amount=amount,
                due_date=due_date,
                image=image,
                is_paid=False,  # Explicitly set to False when adding a new bill
                razorpay_order_id=None  # Initially, we may not have a Razorpay order ID
            )
            bill.save()
            messages.success(request, 'Bill added successfully.')
            return redirect('usershome')

    return render(request, 'add_bill.html', {'user': user})




def view_bill(request):
    if 'email' in request.session:
        mail = request.session['email']
        current_user = get_object_or_404(users_register, email_id=mail)
        bills = Bill.objects.filter(user=current_user)
        return render(request, 'view_bill.html', {'bills': bills})
    
    return redirect('add_bill')



#User searching for bill
def search_bills(request):
    query = request.GET.get('query', '')
    if query:
   
        bills = Bill.objects.filter(category__icontains=query)
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
razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))

def payment(request, bill_id):
    # Get the bill for the user based on the provided bill_id
    bill = get_object_or_404(Bill, id=bill_id, user__email_id=request.session['email'])
    
    # Calculate the amount to be paid (convert to smallest currency unit, e.g., paise)
    amount = int(bill.amount * 100)  # Amount in paise
    currency = 'INR'
    
    # Create an order with Razorpay
    razorpay_order = razorpay_client.order.create({
        'amount': amount,
        'currency': currency,
        'payment_capture': '0'  # Set to '0' for manual capture
    })
    
    # Get the order ID
    razorpay_order_id = razorpay_order['id']

    # Prepare context for rendering the payment template
    context = {
        'razorpay_order_id': razorpay_order_id,
        'razorpay_merchant_key': settings.RAZOR_KEY_ID,
        'razorpay_amount': amount,
        'currency': currency,
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
            result = razorpay_client.utility.verify_payment_signature(params_dict)

            if result is not None:
                # Fetch the bill associated with the razorpay_order_id
                bill = get_object_or_404(Bill, razorpay_order_id=razorpay_order_id)

                # Amount should match the bill amount
                amount = int(bill.amount * 100)  # Convert to paise

                # Capture the payment
                try:
                    razorpay_client.payment.capture(payment_id, amount)

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





