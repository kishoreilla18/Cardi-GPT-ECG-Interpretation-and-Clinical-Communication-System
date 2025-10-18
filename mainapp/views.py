from django.shortcuts import render,redirect
from django.contrib import messages
from mainapp.models import *
from django.core.mail import send_mail
from django.conf import settings 
from django.utils import timezone
import ssl 
import urllib.parse 
import urllib.request


def chatbot(req):
    return render(req, "user/chatbot.html")

def home(req):
    return render(req, "main/index.html")

def about(req):
    return render(req, "main/about.html")

def contact(req):
    return render(req, "main/contact.html")

import random as rnd
def signup(req): 

    if req.method == "POST": 
        fullname = req.POST.get("username") 
        email = req.POST.get("useremail") 
        password = req.POST.get("userpassword")  
        address = req.POST.get("address") 
        phone = req.POST.get("phno")
        age = req.POST.get("age")
        userimage = req.FILES.get("userimage", None)

        number = rnd.randint(1000, 9999)

        print(type(userimage))
        if not fullname or not email or not password or not address or not phone or not userimage: 
            messages.warning(req, "Enter all the fields to continue") 
            return render(req, 'main/signup.html')
        try: 
            data = UserModel.objects.get(user_email=email) 
            messages.warning( 
                req, "Email was already registered, choose another email..!" 
            ) 
            return redirect("signup") 
        except:
            
            UserModel.objects.create( 
                user_name=fullname, 
                user_email=email, 
                user_contact=phone,
                age=age,
                user_address=address,
                user_password=password,
                user_image=userimage, 
                Otp_Num=number,
            ) 
            mail_message = ( 
                f"Registration Successfully\n Your 4 digit Pin is below\n {number}" 
            )  
            
            sendSMS(fullname,number,phone) 
            send_mail("Verify your OTP", mail_message , settings.EMAIL_HOST_USER, [email]) 
            user = UserModel.objects.get(user_email=email)
            req.session["user_email"] = email 
            messages.success(req, "Your account was created..") 
            return redirect("otp")
    print(req.method)  
    return render(req, "main/signup.html")   

def sendSMS(user, otp, mobile): 
    data = urllib.parse.urlencode( 
        { 
            "username": "Codebook", 
            "apikey": "6876b58478ee6ece5fad", 
            "mobile": mobile, 
            "message": f"Hello {user}, your OTP for account activation is {otp}. This message is generated from https://www.codebook.in server. Thank you", 
            "senderid": "CODEBK", 
        } 
    ) 
    data = data.encode("utf-8") 
    # Disable SSL certificate verification 
    context = ssl._create_unverified_context() 
    request = urllib.request.Request("https://smslogin.co/v3/api.php?") 
    f = urllib.request.urlopen(request, data, context=context) 
    return f.read()

def otp(req):
    user_email = req.session.get("user_email")
    if user_email:
        try:
            user_o = UserModel.objects.get(user_email=user_email)
        except UserModel.DoesNotExist:
            messages.error(req, "User not found.")
            return redirect("login")

        if req.method == "POST":
            otp1 = req.POST.get("otp1", "")
            otp2 = req.POST.get("otp2", "")
            otp3 = req.POST.get("otp3", "")
            otp4 = req.POST.get("otp4", "")

            if otp1 and otp2 and otp3 and otp4:
                user_otp = otp1 + otp2 + otp3 + otp4
                if user_otp.isdigit():
                    u_otp = int(user_otp)
                    if u_otp == user_o.Otp_Num:
                        user_o.Otp_Status = "verified"
                        user_o.save()
                        messages.success(
                            req, "OTP verification was successful. You can now login."
                        )
                        return redirect("login")
                    else:
                        messages.error(
                            req, "Invalid OTP. Please enter the correct OTP."
                        )
                else:
                    messages.error(
                        req, "Invalid OTP format. Please enter numbers only."
                    )
            else:
                messages.error(req, "Please enter all OTP digits.")

    else:
        messages.error(req, "Session expired. Please retry the OTP verification.")

    return render(req, "main/otp.html")



def login(req):
    if req.method == "POST":
        user_email = req.POST.get("email")
        user_password = req.POST.get("password")

        # Check empty fields
        if not user_email or not user_password:
            messages.warning(req, "Enter all the fields to continue")
            return render(req, "main/login.html")

        try:
            users_data = UserModel.objects.filter(user_email=user_email)
            if not users_data.exists():
                messages.error(req, "User does not exist")
                return redirect("login")

            for user_data in users_data:
                if user_data.user_password == user_password:
                    # Case 1: Verified OTP + Accepted User
                    if user_data.Otp_Status == "verified":
                        req.session["user_email"] = user_email 
                        messages.success(req, "You are logged in..")
                        user_data.last_login = timezone.now()
                        user_data.save()
                        return redirect("user_dashboard")

                    # Case 4: OTP not verified
                    else:
                        messages.warning(req, "Please verify your OTP first...!")
                        req.session["user_email"] = user_data.user_email
                        return redirect("otp")
                else:
                    messages.error(req, "Incorrect credentials...!")
                    return redirect("login")

            # Fallback if no match found
            messages.error(req, "Incorrect credentials...!")
            return redirect("login")

        except Exception as e:
            print("Login error:", e)
            messages.error(req, "An error occurred. Please try again later.")
            return redirect("login")

    # GET request
    return render(req, "main/login.html")

