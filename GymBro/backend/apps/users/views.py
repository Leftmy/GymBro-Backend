from django.shortcuts import render
from django.contrib.auth import authenticate, login, logout
from django.views import View
from .services import UserService
# Create your views here.

class UserLoginView(View):
    def get(self, request):
        return render(request, 'users/login.html')

    def post(self, request):
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'users/login_success.html')
        else:
            return render(request, 'users/login.html', {'error': 'Invalid credentials'})
        

class UserRegisterView(View):
    def get(self, request):
        return render(request, 'users/register.html')

    def post(self, request):
        # Registration logic here
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        try:
            user = UserService.create_user(username=username, email=email, password=password)
            return render(request, 'users/register_success.html')
        except ValueError as e:
            return render(request, 'users/register.html', {'error': str(e)})
        return render(request, 'users/register_success.html')