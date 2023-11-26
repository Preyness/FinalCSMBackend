from django.shortcuts import render
from django.contrib.auth.views import LoginView

class LabTechLoginView(LoginView):
    template_name = 'labtech/login.html'  # Create a template for the login form


