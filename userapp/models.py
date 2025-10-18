from django.db import models
from djongo import models   # ✅ correct for MongoDB


class BaseModelWithAutoIncrement(models.Model):
    S_No = models.AutoField(primary_key=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.S_No:
            last_model = self.__class__.objects.all().order_by('-S_No').first()
            self.S_No = (last_model.S_No + 1) if last_model and last_model.S_No else 1
        super().save(*args, **kwargs)

class QuestionIdWithAutoIncrement(models.Model):
    question_id = models.AutoField(primary_key=True)

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        if not self.question_id:
            last_model = self.__class__.objects.all().order_by('-question_id').first()
            self.question_id = (last_model.question_id + 1) if last_model and last_model.question_id else 1
        super().save(*args, **kwargs)

class MobileNetModel(BaseModelWithAutoIncrement):
    model_accuracy = models.CharField(max_length=10)
    model_name = models.CharField(max_length=10)
    model_executed = models.CharField(max_length=10, null=True)

    class Meta:
        db_table = "MobileNet_model"



class DenseNetModel(BaseModelWithAutoIncrement):
    model_accuracy = models.CharField(max_length=10)
    model_name = models.CharField(max_length=10)
    model_executed = models.CharField(max_length=10, null=True)

    class Meta:
        db_table = "DenseNet_model"
    
    


class InceptionModel(BaseModelWithAutoIncrement):
    model_accuracy = models.CharField(max_length=10)
    model_name = models.CharField(max_length=20)
    model_executed = models.CharField(max_length=10, null=True)

    class Meta:
        db_table = "Inception_model"
    


# your_app_name/models.py

from django.utils import timezone

class PredictionRecord(BaseModelWithAutoIncrement):
    predicted_result = models.CharField(max_length=100, default="Unknown") 
    model_accuracy = models.FloatField(null=True, blank=True)
    model_name = models.CharField(max_length=100, null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    user_email = models.EmailField(help_text="user_email", unique=True)

    class Meta:
        db_table = "Prediction_Record"

    def __str__(self):
        return f"{self.predicted_result} ({self.model_name})"
    

from datetime import datetime



class Question(models.Model):
    category = models.CharField(max_length=100)
    question = models.TextField()
    posted_by = models.EmailField()
    answers = models.JSONField(default=list)
    timestamp = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = "Comm_Questions"

    def __str__(self):
        return f"{self.category}: {self.question[:40]}"
    

class Answer(models.Model):
    answer_id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE)
    answered_by = models.EmailField()
    text = models.TextField()
    sentiment = models.CharField(max_length=100, null=True) 
    time = models.DateTimeField(default=datetime.now)

    class Meta:
        db_table = "Comm_Answers"

    def __str__(self):
        return f"Answer to Q{self.question.question_id}"
