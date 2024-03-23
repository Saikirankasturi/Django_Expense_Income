from django.shortcuts import redirect, render
from django.views import View
import json
from django.http import JsonResponse
from django.contrib.auth.models import User
from validate_email import validate_email
from django.contrib import messages
from django.core.mail import send_mail
from expense.settings import EMAIL_HOST_USER
from django.urls import reverse
from django.contrib import auth

from django.utils.encoding import force_bytes,force_str
from django.utils.http import urlsafe_base64_encode,urlsafe_base64_decode
from .utils import token_generator
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.auth.tokens import PasswordResetTokenGenerator
import threading



# Create your views here.
class EmailThread(threading.Thread):
    def __init__(self, email):
        self.email = email
        threading.Thread.__init__(self)

    def run(self):
        self.send_mail(fail_silently=True)    



class UsernameValidationView(View):
    def post(self,request):
        data=json.loads(request.body)
        username = data['username']

        #The isalnum() method returns True if all the characters are alphanumeric, 
        #meaning alphabet letter (a-z) and numbers (0-9).
        if not str(username).isalnum():
            return JsonResponse({'username_error':'Username should only contain alphanumeric characters'},status=400)
        if User.objects.filter(username=username).exists():
            return JsonResponse({'username_error':'Username is already exists,choose another one'},status=409)
        
        return JsonResponse({'username_valid':True})
    
class EmailValidationView(View):
    def post(self,request):
        data=json.loads(request.body)
        email = data['email']

        #The isalnum() method returns True if all the characters are alphanumeric, 
        #meaning alphabet letter (a-z) and numbers (0-9).
        if not validate_email(email):
            return JsonResponse({'email_error':'Email is invalid'},status=400)
        if User.objects.filter(email=email).exists():
            return JsonResponse({'email_error':'Email is already exists,choose another one'},status=409)
        return JsonResponse({'email_valid':True})
    
class RegistrationView(View):
    def get(self,request):
        return render(request,'authentication/register.html')
    
    def post(self,request):

        # messages.success(request,'Success whatsapp')
        # messages.warning(request,'Success warning')
        # messages.info(request,'Success info')
        # messages.error(request, 'An error occurred!')
        
        #GET USER DATA
        #VALIDATE
        #create user  account

        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']

        context={
            'fieldValues':request.POST
        }

        if not User.objects.filter(username=username).exists():
            if not User.objects.filter(email=email).exists():


                if len(password) <6:
                    messages.error(request,"Password is too short")
                    return render(request,'authentication/register.html',context)
                
                user = User.objects.create_user(username=username,email=email)
                user.set_password(password)
                user.is_active=False
                user.save()

                #path_to_view

                #relative url verification
                #encode uid
                #token
                
                current_site=get_current_site(request)

                email_body={
                    'user':user,
                    'domain':current_site.domain,
                    'uid':urlsafe_base64_encode(force_bytes(user.pk)),
                    'token':token_generator.make_token(user),

                }

                #uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

                link= reverse('activate',kwargs={'uidb64':email_body['uid'],'token':email_body['token']})
                
                #link=reverse('activate',kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})

                activate_url='http://' + current_site.domain + link

                subject = "Your account has been successfully activated with username - {}".format(username)
                
                message= 'Hi  '+ user.username  + '\n Please use this link to verify your account \n'+ activate_url +'\n Dear {},\n\nWelcome to our website! We are thrilled to have you join us.\n\nBest regards,\nThe Team'.format(username)

                send_mail(
                    subject,
                    message,
                    'noreply@gmail.com',
                    [email],
                    fail_silently=True
                )

                EmailThread(email).start()

                messages.success(request,'Account Successfully created')
                return render(request,'authentication/register.html')
            

        return render(request,'authentication/register.html')


    
class VerificationView(View):
    def get(self,request,uidb64,token):
        try:
            id=force_str(urlsafe_base64_encode(uidb64))
            user=User.objects.get(pk=id)
            
            if not token_generator.check_token(user,token):
                return redirect('login'+'?message='+'User is already activated!')
            
            if user.is_active:
                return redirect('login')
            user.is_active=True
            user.save()

            messages.success(request,'Account activated successfully!')
            return redirect('login')
        except Exception as ex:
            pass   
        return redirect('login')

class LoginView(View):
    def get(self,request):
        return render(request,'authentication/login.html')
    
    def post(self,request):
        username=request.POST['username']
        password=request.POST['password']

        if username and password:
            user=auth.authenticate(username= username,password=password)

            if user:
                if user.is_active:
                    auth.login(request,user)
                    messages.success(request,'Welcome back, '+ user.username +' You are now logged in!!')
                    return redirect('expense')
                messages.error(request,'Account is not active please check your email')
                return render(request,'authentication/login.html')
            
            messages.error(request,'Invalid Credentails,Please try again')
            return render(request,'authentication/login.html')
        
        messages.error(request,'Please fill in all the required fields.')
        return render(request,'authentication/login.html')
    
class LogoutView(View):
    def post(self,request):
        auth.logout(request)
        messages.success(request,'You have been logged out')
        return redirect('login')
    
class RequestPasswordResetEmail(View):
    def get(self,request):
        return render(request,'authentication/reset-password.html')
    
    def post(self,request):
        email = request.POST.get('email', None)

        context={
            'values':request.POST
        }

        if not email:
            messages.error(request, "Please provide an email address")
            return render(request, 'authentication/reset-password.html',context)

        current_site=get_current_site(request)

        user = User.objects.filter(email=email).first()
        if user:
            email_contents = {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': PasswordResetTokenGenerator().make_token(user),
            }


            # uidb64 = urlsafe_base64_encode(force_bytes(user.pk))

            link= reverse('reset-user-password',kwargs={'uidb64':email_contents['uid'],'token':email_contents['token']})
                
            # link=reverse('activate',kwargs={'uidb64':uidb64,'token':token_generator.make_token(user)})

            reset_url = 'http://' + current_site.domain + link


            subject = "Password reset"
                
            message= 'Hi ' + '\n Please the click this link to reset your password \n'+ reset_url +'\n\nBest regards,\nThe Team'

            send_mail(
            subject,
            message,
            'noreply@gmail.com',
            [email],
            fail_silently=True
            )       
            EmailThread(email).start()

        messages.success(request,"We have send you email to reset your password")
        return render(request, 'authentication/reset-password.html')
    

class CompletePasswordReset(View):
    def get(self,request,uidb64,token):

        context={
            'uidb64':uidb64,
            'token':token
        }

        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=user_id)

            if not PasswordResetTokenGenerator().check_token(user,token):
                messages.info(request,"Password is invalid, please request a new one")
                return render(request, 'authentication/reset-password.html')
        
        except Exception as identifier:
            pass






        return render(request,'authentication/set-newpassword.html',context)
    
    def post(self,request,uidb64,token):
        context={
            'uidb64':uidb64,
            'token':token
        }
        password=request.POST['password']
        password2=request.POST['password2']

        if password != password2:
            messages.error(request,'Password do not match')
            return render(request,'authentication/set-newpassword.html',context)

        if len(password) < 6 :
            messages.error(request,'Password too short')
            return render(request,'authentication/set-newpassword.html',context)
        
        try:
            user_id = force_str(urlsafe_base64_decode(uidb64))

            user = User.objects.get(pk=user_id)

            user.set_password(password)
            user.save()

            messages.success(request,"Password reset successfull,You can login now with new password")
            return redirect('login')
        
        except Exception as identifier:
            messages.info(request,"Something went wrong!!!,try again")
            return render(request,'authentication/set-newpassword.html',context)
        #return render(request,'authentication/set-newpassword.html',context)