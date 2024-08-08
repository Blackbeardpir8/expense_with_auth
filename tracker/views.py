from django.shortcuts import render,redirect
from django.contrib import messages
from tracker.models import *
from django.db.models import Sum
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import authenticate,login,logout
# Create your views here.


def register_person(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        user_obj = User.objects.filter(
            Q(email=email) | Q(username=username)
            )

        if not username or not password:
            messages.error(request, "Error: Username and Password cannot be Empty.")
            return redirect('/register_person/')

        if user_obj.exists():
            messages.error(request, "Error: Username or Email already Exists.")
            return redirect('/register_person/')
        
        user_obj = User.objects.create(
            first_name = first_name,
            last_name = last_name,
            username = username,
            email = email,
        )
        user_obj.set_password(password)
        user_obj.save()
        messages.success(request, "Success: Account Created.")
        return redirect('/register_person/')

    return render(request,'register.html')

def login_person(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user_obj = User.objects.filter(username=username)

        if not user_obj.exists():
            messages.error(request, "Error : Username does not Exists ")
            return redirect('/login_person/')
        
        user_obj = authenticate(username = username, password = password)

        if not user_obj:
            messages.error(request, "Error : Invalid Credentials ")
            return redirect('/login_person/')
        
        login(request,user_obj)
        return redirect('/')
    
    return render(request,'login.html')


def logout_person(request):
    logout(request)
    messages.success(request, "Success : User Logout")
    return redirect('/login_person/')
    

def index(request):
    if request.method =="POST":
        description = request.POST.get('description')
        amount = request.POST.get('amount')


        if not description:
            messages.info(request, "Description cannot be empty")
            return redirect('/')
        
        try:
            amount = float(amount)
        except ValueError:
            messages.info(request, "Amount should be a valid number")
            return redirect('/')


        Transactions.objects.create(
            description = description,
            amount = amount,
        )

        messages.success(request, "Transaction added successfully!")
        return redirect('/')
        

    
    context = {'transactions' : Transactions.objects.all(),
               'balance' : Transactions.objects.all().aggregate(total_balance = Sum('amount'))['total_balance'] or 0,
               'income' : Transactions.objects.filter(amount__gte = 0).aggregate(income = Sum('amount'))['income'] or 0,
               'expense' : Transactions.objects.filter(amount__lte = 0).aggregate(expense = Sum('amount'))['expense'] or 0,
               }

    return render(request,'index.html',context)


def deleteTransaction(request,uuid):

    Transactions.objects.get(uuid = uuid).delete()
    return redirect('/')

