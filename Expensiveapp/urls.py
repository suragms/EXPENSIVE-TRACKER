from django.urls import path
from .import views

urlpatterns = [
    path('',views.index,name='index'),
    path('user_register/',views.user_register,name='user_register'),
    path('login/',views.login,name='login'),
    path('logout/',views.logout,name='logout'),
    path('userprofile/',views.userprofile,name='userprofile'),
    path('overview/<int:aid>/',views.overview, name='overview'),
    path('userprofile_edit/<int:eid>/',views.userprofile_edit,name='userprofile_edit'),
    path('admin_dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('users/',views.user_list, name='user_list'),
    path('delete_user/<int:did>/',views.delete_user, name='delete_user'),
    path('adminlogin/', views.adminlogin, name='adminlogin'),
    path('feedback_rate/', views.feedback, name='feedback_rate'),
    path('usershome/', views.usershome, name='usershome'),
    path('feedbacklist/', views.feedback_list_view, name='feedbacklist'),
    path('delete_feedbacks/<int:did>/', views.delete_feedbacks, name='delete_feedbacks'),
    path('add_income/<int:aid>/', views.add_income, name='add_income'),
    path('add_expense/<int:aid>/',views.add_expense,name='add_expense'),
    path('add/',views.add,name='add'),
    path('view/',views.view,name='view'),
    path('view_income/',views.viewincome,name='view_income'),
    path('view_expense/',views.viewexpense,name='view_expense'),
    path('pie/<int:aid>/',views.pie_chart, name='pie'),
    path('delete_income/<int:did>/',views.delete_income, name='delete_income'),
    path('delete_expense/<int:did>/',views.delete_expense, name='delete_expense'),
    path('all_transactions/<int:aid>/',views.all_transactions, name='all_transactions'),
    path('bar_chart/<int:aid>/',views.bar_chart,name='bar_chart'), 
    path('add_bill/<int:aid>/',views.add_bill,name='add_bill'), 
    path('bill/', views.view_bill, name='view_bill'),
    path('search_bills/',views.search_bills, name='search_bills'),
    path('delete_bill/<int:bid>/',views.delete_bill, name='delete_bill'),
    path('payment/<int:bill_id>/',views.payment, name='payment'), 
    path('paymenthandler/',views.paymenthandler, name='paymenthandler'),
    path('userfeedback_list/', views.userfeedback_list_view, name='userfeedback_list'),
    


]
