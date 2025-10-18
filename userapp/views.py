from django.shortcuts import render,redirect
from django.contrib import messages
from userapp.models import *
from mainapp.models import *
from django.core.mail import send_mail
from django.conf import settings 
from django.utils import timezone
import ssl 
import urllib.parse 
import urllib.request
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from django.db import IntegrityError, DatabaseError



def user_dashboard(req):
    # Ensure MobileNetModel record exists
    try:
        if not MobileNetModel.objects.exists():
            MobileNetModel.objects.create(
                model_accuracy=98.80,
                model_name="MobileNet",
                model_executed="yes"
            )
    except (IntegrityError, DatabaseError) as e:
        print(f"Error inserting into MobileNetModel: {e}")

    # Ensure DenseNetModel record exists
    try:
        if not DenseNetModel.objects.exists():
            DenseNetModel.objects.create(
                model_accuracy=98.18,
                model_name="DenseNet",
                model_executed="yes"
            )
    except (IntegrityError, DatabaseError) as e:
        print(f"Error inserting into DenseNetModel: {e}")

    # Ensure InceptionModel record exists
    try:
        if not InceptionModel.objects.exists():
            InceptionModel.objects.create(
                model_accuracy=97.99,
                model_name="Inception",
                model_executed="yes"
            )
    except (IntegrityError, DatabaseError) as e:
        print(f"Error inserting into InceptionModel: {e}")

    # Render user dashboard page
    return render(req, "user/userdashboard.html")

def user_profile(req): 
    email = req.session.get("user_email") 
    if not email: 
        messages.error(req, "User not logged in.") 
        return redirect("login") 
 
    user = UserModel.objects.get(user_email=email)
    print(user.user_image)
 
    if req.method == "POST":
        user.user_name = req.POST.get("user_name")  
        user.user_contact = req.POST.get("user_contact") 
        user.user_email = req.POST.get("user_email") 
        user.user_password = req.POST.get("user_password")
        user.user_address = req.POST.get("address")
        user.age = req.POST.get("age")

        if req.FILES.get('userimage'):
            user.user_image = req.FILES['userimage']

        user.save()
        messages.success(req, "Profile updated successfully.") 
        return render(req, "user/profile.html", {"user": user})

    return render(req, "user/profile.html", {"user": user})



def userfeedback(req): 
    email = req.session["user_email"]  
    user = UserModel.objects.get(user_email=email) 
    if req.method == "POST": 
        stars = req.POST.get("stars") 
        review = req.POST.get("review") 
        
        if not stars or not review.strip(): 
            messages.warning(req, "Enter all the fields to continue!") 
            return render (req, "user/feedback.html") 
        rating = int(stars)
        sid = SentimentIntensityAnalyzer() 
        score = sid.polarity_scores(review) 
        sentiment = None 
        if score["compound"] > 0 and score["compound"] <= 0.5: 
            sentiment = "positive" 
        elif score["compound"] >= 0.5: 
            sentiment = "very positive" 
        elif score["compound"] < -0.5: 
            sentiment = "negative" 
        elif score["compound"] < 0 and score["compound"] >= -0.5: 
            sentiment = " very negative" 
        else: 
            sentiment = "neutral" 
        Feedback.objects.create( 
            Rating=rating, Review=review, Sentiment=sentiment, Reviewer=email 
        ) 
        # # models
        # MobileNetModel.objects.create( 

        #         model_accuracy = 98.80,
        #         model_name = "Mobilnet",
        #         model_executed = "yes"
                
        #     )
        # DenseNetModel.objects.create( 
        #         model_accuracy = 98.18,
        #         model_name = "densenet",
        #         model_executed = "yes"
                
        #     )
        # InceptionModel.objects.create( 
        #         model_accuracy = 97.99,
        #         model_name = "Inception",
        #         model_executed = "yes"
                
        #     ) 

        messages.success(req, "Feedback recorded") 
        return redirect("userfeedback") 
    return render(req, "user/feedback.html", {"user": user})


import os 
import base64 
from django.core.files.storage import default_storage 
import numpy as np 
import cv2 
from django.conf import settings 
from tensorflow.keras.models import load_model 
from tensorflow.keras.preprocessing import image 
import numpy as np 
 
# Define the class mapping  
class_dict = {
    'Left Bundle Branch Block': 0,
    'Normal': 1,
    'Premature Atrial Contraction': 2,
    'Premature Ventricular Contractions': 3,
    'Right Bundle Branch Block': 4,
    'Ventricular Fibrillation': 5,
}
# Reverse the dictionary to map index to label 
class_dict_reversed = {v: k for k, v in class_dict.items()} 
 
from tensorflow.keras.preprocessing import image 
from tensorflow.keras.applications import mobilenet, densenet, inception_v3 
import numpy as np 
 
def predict_image_category(model, image_path, model_type): 
    try: 
        img = image.load_img(image_path, target_size=(224, 224)) 
        img_array = image.img_to_array(img) 
        img_array = np.expand_dims(img_array, axis=0) 
 
        # Choose correct preprocessing 
        if model_type.lower() == "mobilenet": 
            img_array = img_array / 255.0 
        elif model_type.lower() == "densenet": 
            img_array = densenet.preprocess_input(img_array) 
        elif model_type.lower() == "inception": 
            img_array = inception_v3.preprocess_input(img_array) 
        else: 
            raise ValueError("Unsupported model type") 
 
        prediction = model.predict(img_array) 
        predicted_class_index = np.argmax(prediction[0]) 
        return class_dict_reversed.get(predicted_class_index, "Unknown") 
 
    except Exception as e: 
        print(f"Error during prediction: {e}") 
        return "Prediction Failed"

 
 
def detection(req): 
    email = req.session.get("user_email")
    print(f"Request method received: {req.method}") 
    if req.method == "POST": 
        print("Inside POST block...") 
        try: 
            model_type = req.POST.get("model_type") 
            uploaded_file = req.FILES.get("image") 
            print(f"Model Type: {model_type}, Uploaded File: {uploaded_file}") 

            if not model_type or not uploaded_file: 
                messages.warning(req, "Enter all the fields to continue.....!") 
                return render(req, "user/detection.html") 
 
            temp_image_path = default_storage.save(uploaded_file.name, uploaded_file) 
            image_path = default_storage.path(temp_image_path) 
 
            if model_type == "Inception": 
                print("Inception")
                model_path = 'ECG_signal_classification/xception_model.h5' 
                model = load_model(model_path) 
                predicted_result = predict_image_category(model, image_path, model_type)
                print(predicted_result) 
                model_info = InceptionModel.objects.latest('S_No') 
                print(model_info)
 
            elif model_type == "Mobilenet":
                print("Mobilenet") 
                model_path = 'ECG_signal_classification/mobilnet_model.h5' 
                model = load_model(model_path) 
                predicted_result = predict_image_category(model, image_path, model_type) 
                model_info = MobileNetModel.objects.latest('S_No') 
 
            elif model_type == "Densenet": 
                print("Densenet")
                model_path = 'ECG_signal_classification/densnet_model.h5' 
                model = load_model(model_path) 
                predicted_result = predict_image_category(model, image_path, model_type) 
                model_info = DenseNetModel.objects.latest('S_No') 
 
            else: 
                raise ValueError("Select a valid Model") 
            
            PredictionRecord.objects.create(
                predicted_result=predicted_result,
                model_accuracy=model_info.model_accuracy,
                model_name=model_info.model_name,
                user_email=email,
            )
 
            uploaded_image_base64, segmented_image_base64, grayscale_image_base64 = generate_segmented_image(image_path) 
 
            req.session["image_path"] = default_storage.url(temp_image_path) 
            req.session["predicted_result"] = predicted_result 
            req.session["uploaded_image_base64"] = uploaded_image_base64 
            req.session["segmented_image_base64"] = segmented_image_base64 
            req.session["grayscale_image_base64"] = grayscale_image_base64 
            req.session["model_name"] = model_info.model_name 
            req.session["model_accuracy"] = model_info.model_accuracy 
 
            print("Resutl:-----------",predicted_result) 
 
            messages.success(req, "Detection Process Completed") 
            return redirect("detection_result") 
 
        except Exception as e: 
            print(e)
            print(f"Exception occurred: {e}") 
            messages.error(req, f"An error occurred: {str(e)}") 
            return render(req, "user/detection.html", {"error": str(e)}) 
 
    print("Inside ELSE block") 
    return render(req, "user/detection.html") 
 
 
def generate_segmented_image(image_path): 
    image = cv2.imread(image_path) 
    gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) 
    _, binary_image = cv2.threshold(gray_image, 127, 255, cv2.THRESH_BINARY) 
    
    segmented_image_path = os.path.join(settings.MEDIA_ROOT, 'segmented_image.jpg') 
    cv2.imwrite(segmented_image_path, binary_image) 
    
    grayscale_image_path = os.path.join(settings.MEDIA_ROOT, 'grayscale_image.jpg') 
    cv2.imwrite(grayscale_image_path, gray_image) 
    
    with open(image_path, "rb") as img_file: 
        original_image_base64 = base64.b64encode(img_file.read()).decode('utf-8') 
    
    with open(segmented_image_path, "rb") as img_file: 
        segmented_image_base64 = base64.b64encode(img_file.read()).decode('utf-8') 
    
    with open(grayscale_image_path, "rb") as img_file: 
        grayscale_image_base64 = base64.b64encode(img_file.read()).decode('utf-8') 
    
    return original_image_base64, segmented_image_base64, grayscale_image_base64 
 
 
def detection_result(req): 
    image_path = req.session.get("image_path", None) 
    predicted_result = req.session.get("predicted_result", "Unknown") 
    model_accuracy = req.session.get("model_accuracy", None) 
    model_name = req.session.get("model_name", None) 
    uploaded_image_base64 = req.session.get("uploaded_image_base64", None) 
    segmented_image_base64 = req.session.get("segmented_image_base64", "") 
    grayscale_image_base64 = req.session.get("grayscale_image_base64", "") 
    graph_accuracy = "" 
    graph_loss = "" 
 
    

    brief_note = {
        'Left Bundle Branch Block': {
            'title': "Left Bundle Branch Block (LBBB)",
            'description': "A condition where the electrical conduction through the left bundle branch of the heart is delayed or blocked. It can indicate underlying heart disease and affects how the left ventricle contracts. Diagnosis is made via ECG, showing a widened QRS complex and specific waveform patterns."
        },
        'Normal': {
            'title': "Normal ECG",
            'description': "Represents a healthy heart rhythm with normal conduction patterns. The P wave, QRS complex, and T wave appear within standard durations and amplitudes, indicating proper atrial and ventricular activity."
        },
        'Premature Atrial Contraction': {
            'title': "Premature Atrial Contraction (PAC)",
            'description': "An early heartbeat originating from the atria. On ECG, it appears as an early P wave with a normal QRS complex. PACs are common and usually benign but may indicate underlying heart conditions if frequent."
        },
        'Premature Ventricular Contractions': {
            'title': "Premature Ventricular Contractions (PVC)",
            'description': "An early heartbeat originating from the ventricles. ECG shows a wide, abnormal QRS complex without a preceding P wave. Occasional PVCs can be benign, but frequent PVCs may require medical evaluation."
        },
        'Right Bundle Branch Block': {
            'title': "Right Bundle Branch Block (RBBB)",
            'description': "A condition where electrical conduction through the right bundle branch is delayed or blocked. On ECG, it shows a widened QRS and characteristic RSR’ pattern in the right precordial leads. It may be benign or indicate heart disease."
        },
        'Ventricular Fibrillation': {
            'title': "Ventricular Fibrillation (VF)",
            'description': "A life-threatening arrhythmia where the ventricles quiver instead of contracting effectively. ECG shows chaotic, irregular waves with no discernible QRS complexes. Immediate defibrillation is required to prevent cardiac arrest."
        }
    }

    
    
   
    if model_name == "Inception": 
        graph_accuracy = 'admin/inception-acc.png' 
        graph_loss = 'admin/inception-loss.png' 
    elif model_name == "Mobilenet": 
        graph_accuracy = 'admin/mobilenet-acc.png' 
        graph_loss = 'admin/mobilenet-loss.png' 
    elif model_name == "densenet": 
        graph_accuracy = 'admin/densenet-acc.png' 
        graph_loss = 'admin/densenet-loss.png' 
    
    

    print(image_path)
    print(segmented_image_base64)
    print("model accuracy",model_accuracy)
    print(model_name)
    print(grayscale_image_base64)
    print(graph_accuracy)
    print(graph_loss)
    print(brief_note)
    return render(req, "user/result.html", { 
        "image_path": image_path, 
        "predicted_result": predicted_result, 
        "model_accuracy": model_accuracy, 
        "model_name": model_name, 
        "uploaded_image_base64": uploaded_image_base64, 
        "segmented_image_base64": segmented_image_base64, 
        "grayscale_image_base64": grayscale_image_base64, 
        "graph_accuracy": graph_accuracy, 
        "graph_loss": graph_loss, 
        "brief_note": brief_note.get(predicted_result, {}), 
    }) 




import os
import json
import requests
from dotenv import load_dotenv
from django.shortcuts import render

load_dotenv()
API_KEY = os.getenv("PERPLEXITY_API_KEY")


#Through API

import os
import json
import requests
from dotenv import load_dotenv
from django.shortcuts import render
from django.http import JsonResponse

load_dotenv()

API_KEY = os.getenv("PERPLEXITY_API_KEY")

def ecg_interpretation(request):
    age = request.GET.get("age", "")
    chestpain = request.GET.get("chestpain", "")
    shortbreath = request.GET.get("shortbreath", "")
    beatingfast = request.GET.get("beatingfast", "")
    swelling = request.GET.get("swelling", "")
    familyhistory = request.GET.get("familyhistory", "")
    sweating = request.GET.get("sweating", "")

    # Prepare structured prompt for Perplexity
    user_prompt = f"""
    You are a professional cardiology assistant AI.
    Based on the following patient symptoms, provide a structured and concise ECG interpretation summary.

    Patient Details:
    - Age: {age}
    - Chest Pain: {chestpain}
    - Shortness of Breath: {shortbreath}
    - Fast/Irregular Heartbeat: {beatingfast}
    - Swelling in Legs/Feet: {swelling}
    - Family History: {familyhistory}
    - Sweating: {sweating}

    Tasks:
    1. Interpret the symptoms briefly and suggest possible ECG patterns or abnormalities (like Normal, Left Bundle Branch Block, Right Bundle Branch Block, PVC, etc.) give only single possible ECG pattern results and stick to only one result when i refreshed the page or reenter the same values.
    2. Provide a concise recommendation — for example: "Immediate medical attention advised" or "Monitor and review in 24 hours".
    3. Suggest 3-4 short preventive or health tips (like hydration, lifestyle habits, etc.)
    4. Return the response strictly in JSON format with this structure:
    {{
      "patient_summary": {{
        "age": "{age}",
        "chest_pain": "{chestpain}",
        "shortness_of_breath": "{shortbreath}",
        "heart_beating_fast": "{beatingfast}",
        "swelling": "{swelling}",
        "family_history": "{familyhistory}",
        "sweating": "{sweating}"
      }},
      "ecg_interpretation": {{
        "result": "...",
        "explanation": "..."
      }},
      "recommendation": "...",
      "health_tips": ["...", "..."]
    }}
    """

    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    data = {
        "model": "sonar",
        "messages": [
            {"role": "system", "content": "You are a medical AI that always returns structured JSON only."},
            {"role": "user", "content": user_prompt}
        ]
    }

    try:
        response = requests.post("https://api.perplexity.ai/chat/completions", headers=headers, json=data)
        response.raise_for_status()
        response_json = response.json()

        ai_text = response_json["choices"][0]["message"]["content"]

        # Try parsing JSON safely
        try:
            structured_data = json.loads(ai_text)
        except json.JSONDecodeError:
            # If not pure JSON, extract JSON substring
            start = ai_text.find("{")
            end = ai_text.rfind("}") + 1
            if start != -1 and end != -1:
                structured_data = json.loads(ai_text[start:end])
            else:
                structured_data = {"error": "Invalid response format"}

    except Exception as e:
        structured_data = {"error": str(e)}
    messages.success(request, "Report Generated successfully!")
    # ✅ Pass parsed JSON to template
    return render(request, "user/ecg_result.html", {"result": structured_data})



from datetime import datetime

CATEGORIES = [
    "Chest Pain",
    "Heart Attack",
    "Irregular Heartbeat",
    "High Blood Pressure",
    "ECG Abnormalities",
    "Heart Surgery Recovery"
]

def community_home(request):
    selected_category = request.GET.get("category")


    questions = Question.objects.filter(category=selected_category)
    print(questions)
    return render(request, "user/community.html", {
        "categories": CATEGORIES,
        "selected_category": selected_category,
        "questions": questions
    })


def post_question(request):
    email = request.session.get("user_email")
    if request.method == "POST":
        category = request.POST.get("category")
        question_text = request.POST.get("question")

        
        request.session["question"]=question_text
        Question.objects.create(
            category=category,
            question=question_text,
            posted_by=email,
            timestamp=datetime.now()
        )
        messages.success(request, "Question posted successfully!")
        print("question added!")
        return redirect(f"/community/?category={category}")
    return redirect("/community/")


from bson.objectid import ObjectId

def post_answer(request, question_id):
    email = request.session.get("user_email")
    if request.method == "POST":
        answer_text = request.POST.get('answer_text')


        #answer sentiment
        sid = SentimentIntensityAnalyzer() 
        score = sid.polarity_scores(answer_text) 
        sentiment = None 
        if score["compound"] > 0 and score["compound"] <= 0.5: 
            sentiment = "positive" 
        elif score["compound"] >= 0.5: 
            sentiment = "very positive" 
        elif score["compound"] < -0.5: 
            sentiment = "negative" 
        elif score["compound"] < 0 and score["compound"] >= -0.5: 
            sentiment = " very negative" 
        else: 
            sentiment = "neutral"  

        qu = request.session.get("question")
        info=Question.objects.get(id=question_id)

        print(info)
        info.answers+=answer_text
        # question_id is the MongoDB _id (string)
        question = Question.objects.get(id=question_id)

        next_id = 1
        if question.answers:
            next_id = len(question.answers) + 1

        new_answer = {
            "answer_id": next_id,
            "answered_by": email,
            "text": answer_text,
            "sentiment": sentiment,
            "time": datetime.now().isoformat()
        }

        question.answers.append(new_answer)
        question.save()

        messages.success(request, "✅ Answer added successfully!")
        return redirect(f'/community/?category={question.category}')



def user_reports(request):
    user_email = request.session.get("user_email")
    if user_email:
    
        reports = PredictionRecord.objects.filter(user_email=user_email).order_by('-created_at')
    else:
        messages.error(request, "Reports not found!, Please check again.")
    return render(request, 'user/reports.html', {'reports': reports})


import sklearn 
import pickle 
import pandas as pd 
 
def prediction(request):
    try:
        # Get inputs from request
        Gender = request.GET.get('gender', "")
        Age = request.GET.get('age', "")
        Hypertension = request.GET.get('hypertension', "")
        Heart_disease = request.GET.get('heart_disease', "")
        Ever_married = request.GET.get('ever_married', "")
        Work_type = request.GET.get('work_type', "")
        Residence_type = request.GET.get('residence_type', "")
        Avg_glucose_level = request.GET.get('avg_glucose_level', "")
        Bmi = request.GET.get('bmi', "")
        Smoking_status = request.GET.get('smoking_status', "")

        print(Gender,Age,Hypertension,Heart_disease,Ever_married,Work_type,Residence_type,Avg_glucose_level,Bmi,Smoking_status)
        # Convert categorical inputs to numeric
        # Gender
        if Gender == "male" or Gender == "Male":
            Gender = 1
        elif Gender == "female" or Gender == "Female":
            Gender = 0


        # Hypertension
        if Hypertension == "yes" or Hypertension == "Yes":
            Hypertension = 1
        elif Hypertension == "no" or Hypertension == "No":
            Hypertension = 0

        # Heart_disease
        if Heart_disease == "yes" or Heart_disease == "Yes":
            Heart_disease = 1
        elif Heart_disease == "no" or Heart_disease == "No":
            Heart_disease = 0

        # Ever_married
        if Ever_married == "yes" or Ever_married == "Yes":
            Ever_married = 1
        elif Ever_married == "no" or Ever_married == "No":
            Ever_married = 0

        # Work_type
        # Work_type
        if Work_type in ( "children","Children"):
            Work_type = 0
        elif Work_type == "govt_job" or Work_type == "Govt_job" or Work_type == "govt job":
            Work_type = 1
        elif Work_type == "never_worked" or Work_type == "Never_worked" or Work_type == "never worked" or Work_type == "never":
            Work_type = 2
        elif Work_type == "private" or Work_type == "Private":
            Work_type = 3
        elif Work_type == "self-employed" or Work_type == "Self_employed" or Work_type == "self_employed" or Work_type == "self":
            Work_type = 4 


        # Residence_type
        if Residence_type == "urban" or Residence_type == "Urban":
            Residence_type = 1
        elif Residence_type == "rural" or Residence_type == "Rural":
            Residence_type = 0

        # Smoking_status
        # Smoking_status
        if Smoking_status == "formerly smoked" or Smoking_status == "Formerly smoked" or Smoking_status == "formerly":
            Smoking_status = 1
        elif Smoking_status == "never smoked" or Smoking_status == "never" or Smoking_status == "never smokes":
            Smoking_status = 0
        elif Smoking_status == "unknown" or Smoking_status == "Unknown":
            Smoking_status = 2
        elif Smoking_status == "smokes" or Smoking_status == "Smokes" or Smoking_status == "smoked":
            Smoking_status = 3


    except (ValueError, TypeError):
        messages.warning(request, "Please enter valid numbers.")
        print("Please enter valid numbers")
        return render(request, "user/detection.html")

    # Load the trained stroke prediction model
    file_path = r'stroke prediction/rfc_strok1.pkl'
    try:
        with open(file_path, 'rb') as file:
            loaded_model = pickle.load(file)

        if not isinstance(loaded_model, sklearn.base.BaseEstimator):
            messages.error(request, "Loaded model is not compatible.")
            print("Loaded model is not compatible.")
            return redirect("prediction_result")

    except FileNotFoundError:
        messages.error(request, "Model file not found.")
        print("Model file not found.")
        return redirect("prediction_result")
    except Exception as e:
        messages.error(request, f"Error loading model: {str(e)}")
        print(e)
        return redirect("prediction_result")

    # Prepare input features as DataFrame
    feature_names = [
        'gender', 'age', 'hypertension', 'heart_disease', 'ever_married',
        'work_type', 'Residence_type', 'avg_glucose_level', 'bmi', 'smoking_status'
    ]
    features_df = pd.DataFrame(
        [[Gender, Age, Hypertension, Heart_disease, Ever_married, Work_type, Residence_type,
          Avg_glucose_level, Bmi, Smoking_status]],
        columns=feature_names
    )
    print("start")
    print(feature_names)
    print(features_df)

    # Make prediction
    try:
        prediction = loaded_model.predict(features_df)
        prediction_result = int(prediction[0])
        print("RESULT ---------", prediction_result)
        request.session['prediction_result'] = prediction_result
    except Exception as e:
        messages.error(request, f"Prediction error: {str(e)}")
        print("Prediction error:", e)
        return redirect("prediction_result")

    return redirect("prediction_result")
 
def prediction_result(req): 
    prediction_result = req.session.get('prediction_result') 
    context = { 
        "prediction_result": prediction_result 
    } 
 
    return render(req,"user/stroke_prediction_result.html",context) 


def my_post(request):
    email = request.session.get("user_email")
    if not email:
        messages.error(request, "Please log in to view your posts.")
        return redirect("/login/")

    # Fetch all questions posted by this user
    user_questions = Question.objects.filter(posted_by=email)

    # Fetch all answers posted by this user (from all questions)
    user_answers = []
    all_questions = Question.objects.all()
    for q in all_questions:
        for ans in q.answers:
            if ans.get("answered_by") == email:
                user_answers.append({
                    "question_id": str(q.id),
                    "question_text": q.question,
                    "answer_text": ans.get("text"),
                    "answered_by": ans.get("answered_by"),
                    "sentiment": ans.get("sentiment"),
                    "time": ans.get("time"),
                    "category": q.category
                })

    context = {
        "user_questions": user_questions,
        "user_answers": user_answers,
        "categories": CATEGORIES,
        "user_email": email
    }
    return render(request, "user/mypost.html", context)
