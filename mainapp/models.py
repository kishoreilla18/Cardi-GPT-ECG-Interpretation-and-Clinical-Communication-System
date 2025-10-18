from django.db import models

class UserModel(models.Model):
    user_id = models.AutoField(primary_key=True) 
    user_name = models.CharField(help_text="user_name", max_length=50)  
    user_email = models.EmailField(help_text="user_email", unique=True) 
    user_password = models.EmailField(help_text="user_password", max_length=50) 
    user_address = models.TextField(help_text="user_address", max_length=100)  
    user_contact = models.CharField(help_text="user_contact", max_length=15, null=True)
    age = models.CharField(help_text="age", max_length=3, null=True) 
    user_image = models.ImageField(upload_to="profile_images/", blank=True, null=True)
    datetime = models.DateTimeField(auto_now=True)  
    last_login = models.DateTimeField(null=True, blank=True) 
    # STATUS_CHOISES = [
    #     ('pending', 'Pending'),
    #     ('accepted', 'Accepted'),
    #     ('rejected', 'Rejected'),
    # ]
    # status = models.CharField(max_length=10, choices=STATUS_CHOISES, default='pending')
    Otp_Num = models.IntegerField(null=True) 
    Otp_Status = models.TextField(default="pending", max_length=60, null=True)
    class Meta: 
        db_table = "user_details" 


class Feedback(models.Model): 
    Feed_id = models.AutoField(primary_key=True) 
    Rating = models.CharField(max_length=100, null=True) 
    Review = models.CharField(max_length=225, null=True) 
    Sentiment = models.CharField(max_length=100, null=True) 
    Reviewer = models.EmailField(help_text="user_email") 
    datetime = models.DateTimeField(auto_now=True) 
 
    class Meta: 
        db_table = "feedback_details" 


