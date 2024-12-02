from django.shortcuts import render,redirect
from .forms import *
from django.views.generic import FormView,CreateView
from django.urls import reverse_lazy
from django.contrib.auth import authenticate, login

# class LoginView(FormView):
#     template_name = 'login.html'
#     form_class = LoginForm

#     def post(self, request):
#         form = LoginForm(data=request.POST)
#         if form.is_valid():
#             email = form.cleaned_data.get('email')  # Get the email
#             pswd = form.cleaned_data.get('password')  # Get the password
            
#             try:
#                 # Get the user by email
#                 user = User.objects.get(email=email)
                
#                 # Authenticate the user
#                 user = authenticate(request, email=user.email, password=pswd)
                
#                 if user is not None:
#                     login(request, user)
#                     return redirect('shop')  # Redirect to the shop page on successful login
#                 else:
#                     messages.error(request, 'Invalid email or password.')
#                     return redirect('login')
#             except User.DoesNotExist:
#                 messages.error(request, 'User does not exist.')
#                 return redirect('login')

#         return render(request, 'login.html', {'form': form})
    


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
                return redirect('shop')
            else:
                return redirect('login')
        return render(request,'login.html',{'form':form})
        

        


class RegistrationView(CreateView):
    template_name='registration.html'
    form_class=RegistrationForm
    success_url=reverse_lazy('login')

    def form_valid(self, form):
        return super().form_valid(form)
    def form_invalid(self, form):
        return super().form_invalid(form)