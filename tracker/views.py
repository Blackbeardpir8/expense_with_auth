from django.shortcuts import render, redirect
from django.contrib import messages
from tracker.models import Transactions
from django.db.models import Sum
from django.contrib.auth.models import User
from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import logging

logger = logging.getLogger(__name__)

# Create your views here.

def register_person(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')

        logger.info(f"Attempt to register with username: {username} and email: {email}")

        user_obj = User.objects.filter(
            Q(email=email) | Q(username=username)
        )

        if not username or not password:
            messages.error(request, "Error: Username and Password cannot be empty.")
            logger.warning("Registration failed: Username or Password empty")
            return redirect('/register_person/')

        if user_obj.exists():
            messages.error(request, "Error: Username or Email already exists.")
            logger.warning(f"Registration failed: Username or Email already exists for {username} or {email}")
            return redirect('/register_person/')

        try:
            user_obj = User.objects.create(
                first_name=first_name,
                last_name=last_name,
                username=username,
                email=email,
            )
            user_obj.set_password(password)
            user_obj.save()
            messages.success(request, "Success: Account created.")
            logger.info(f"Registration successful for username: {username}")
            return redirect('/register_person/')
        except Exception as e:
            logger.error(f"Error during registration: {str(e)}")
            messages.error(request, "Error: Could not create account. Please try again.")
            return redirect('/register_person/')

    return render(request, 'register.html')


def login_person(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        logger.info(f"Attempt to login with username: {username}")

        user_obj = User.objects.filter(username=username)

        if not user_obj.exists():
            messages.error(request, "Error: Username does not exist.")
            logger.warning(f"Login failed: Username {username} does not exist")
            return redirect('/login_person/')

        user_obj = authenticate(username=username, password=password)

        if not user_obj:
            messages.error(request, "Error: Invalid credentials.")
            logger.warning(f"Login failed: Invalid credentials for username {username}")
            return redirect('/login_person/')

        login(request, user_obj)
        messages.success(request, "Success: Logged in successfully.")
        logger.info(f"Login successful for username: {username}")
        return redirect('/')

    return render(request, 'login.html')


def logout_person(request):
    if request.user.is_authenticated:
        logger.info(f"User {request.user.username} logged out")
        logout(request)
        messages.success(request, "Success: Logged out successfully.")
    else:
        logger.warning("Logout attempt failed: User was not authenticated")
        messages.error(request, "Error: You are not logged in.")

    return redirect('/login_person/')


@login_required(login_url='/login_person/')
def index(request):
    if request.method == "POST":
        description = request.POST.get('description')
        amount = request.POST.get('amount')

        if not description:
            messages.info(request, "Error: Description cannot be empty.")
            logger.warning(f"Transaction failed: Description was empty for user {request.user.username}")
            return redirect('/')

        try:
            amount = float(amount)
        except ValueError:
            messages.info(request, "Error: Amount should be a valid number.")
            logger.warning(f"Transaction failed: Invalid amount entered by user {request.user.username}")
            return redirect('/')

        try:
            Transactions.objects.create(
                description=description,
                amount=amount,
                created_by=request.user
            )
            messages.success(request, "Transaction added successfully!")
            logger.info(f"Transaction successful for user {request.user.username}")
        except Exception as e:
            logger.error(f"Error during transaction creation: {str(e)}")
            messages.error(request, "Error: Could not add transaction. Please try again.")
        return redirect('/')

    context = {
        'transactions': Transactions.objects.filter(created_by=request.user),
        'balance': Transactions.objects.filter(created_by=request.user).aggregate(total_balance=Sum('amount'))['total_balance'] or 0,
        'income': Transactions.objects.filter(created_by=request.user, amount__gte=0).aggregate(income=Sum('amount'))['income'] or 0,
        'expense': Transactions.objects.filter(created_by=request.user, amount__lte=0).aggregate(expense=Sum('amount'))['expense'] or 0,
    }

    return render(request, 'index.html', context)


@login_required(login_url='/login_person/')
def deleteTransaction(request, uuid):
    try:
        transaction = Transactions.objects.get(uuid=uuid, created_by=request.user)
        transaction.delete()
        messages.success(request, "Transaction deleted successfully.")
        logger.info(f"Transaction {uuid} deleted successfully by user {request.user.username}")
    except Transactions.DoesNotExist:
        messages.error(request, "Error: Transaction not found.")
        logger.warning(f"Transaction deletion failed: Transaction {uuid} not found for user {request.user.username}")
    except Exception as e:
        logger.error(f"Error during transaction deletion: {str(e)}")
        messages.error(request, "Error: Could not delete transaction. Please try again.")

    return redirect('/')
