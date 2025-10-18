"""Cardi_GPT URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from mainapp import views as mainviews
from userapp import views as userviews
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('admin/', admin.site.urls),
    path('',mainviews.home,name='home'),
    path('home/',mainviews.home,name='home'),
    path('about/',mainviews.about,name='about'),
    path('contact/',mainviews.contact,name='contact'),
    path('signup/',mainviews.signup,name='signup'),
    path('otp/',mainviews.otp,name='otp'),
    path('login/',mainviews.login,name='login'),
    path('user-dashboard/',userviews.user_dashboard,name='user_dashboard'),
    path('user-profile/',userviews.user_profile,name='user_profile'),
    path('user-feedback/',userviews.userfeedback,name='userfeedback'),
    path('detection/',userviews.detection,name='detection'),
    path('detection-result/',userviews.detection_result,name='detection_result'),
    path('chatbot/',mainviews.chatbot,name='chatbot'),
    path("ecg-interpretation/", userviews.ecg_interpretation, name="ecg_interpretation"),
    path("community/", userviews.community_home, name="community_home"),
    path("post_question/", userviews.post_question, name="post_question"),
    path("post_answer/<str:question_id>/", userviews.post_answer, name="post_answer"),
    path('reports/', userviews.user_reports, name='user_reports'),
    path('prediction/', userviews.prediction, name='prediction'),
    path('prediction_result/', userviews.prediction_result, name='prediction_result'),
    path('my_post/', userviews.my_post, name='my_post'),



] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
