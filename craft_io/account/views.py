from django.shortcuts import render,redirect
from django.views import View
from .forms import *
from django.contrib import messages
from django.contrib.auth import authenticate,login
from django.http import HttpResponse
from django.views.generic import TemplateView,FormView,CreateView
from django.urls import reverse_lazy


class LoginView(FormView):
    template_name='login.html'
    form_class=LoginForm
    def post(self,request):
        form=LoginForm(data=request.POST)
        if form.is_valid():
            uname=form.cleaned_data.get('username')
            pswd=form.cleaned_data.get('password')
            user=authenticate(request,username=uname,password=pswd)
            if user:
                login(request,user)
                return redirect('customerhome')
            else:
                messages.error(request,'Login Failed!!')
                return redirect('login')
        return render(request,'login.html',{'form':form})

class RegistrationView(CreateView):
    template_name='registration.html'
    form_class=RegistrationForm
    success_url=reverse_lazy('login')