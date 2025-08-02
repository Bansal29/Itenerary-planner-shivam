from flask import render_template, Blueprint, request, redirect, url_for, jsonify
import google.generativeai as genai
import os
from dotenv import load_dotenv


# Load environment variables from .env
load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

views = Blueprint('views', __name__)

# Homepage
@views.route('/')
def home():
    return render_template('index.html')

# New plan creation page
@views.route('/plans/newplan', methods=['GET', 'POST'])
def new_plan():
    if request.method == 'POST':
        return redirect(url_for('views.plan_preferences'))
    return render_template('new_plan.html')

# Preferences selection page
@views.route('/plans/preferences', methods=['GET', 'POST'])
def plan_preferences():
    if request.method == 'POST':
        return redirect(url_for('views.plan_details'))
    return render_template('preferences.html')

# Plan details page and AI itinerary generator
@views.route('/plans/details', methods=['GET', 'POST'])
def plan_details():
    if request.method == 'POST':
        print("Line no 36 inside if")
        destination = request.form.get('destination')
        days = request.form.get('days')
        interests = request.form.get('interests')

        # Validate input
        if not destination or not days or not interests:
            return render_template('plan_details.html', error="All fields are required.")

        # Generate AI-based itinerary
        itinerary = get_ai_itinerary(destination, days, interests)

        # If OpenAI response is empty
        if not itinerary or "Sorry" in itinerary:
            print("Line no 50")
            return render_template('plan_details.html', error=itinerary)
        print("Line no 52")
        
        return render_template('ai_plan.html', 
                               itinerary=itinerary, 
                               destination=destination, 
                               days=days, 
                               interests=interests)
    print("Line 57")
    return render_template('plan_details.html')


# AI itinerary generator using OpenAI API
def get_ai_itinerary(destination, days, interests):
    print("Line no 63")
    try:
        days = int(days)
    except ValueError:
        return "Invalid number of days."

    prompt = (
        f"You are a professional travel planner. Create a detailed {days}-day travel itinerary "
        f"to {destination} for someone interested in {interests}. "
        "Format it day by day:\n"
        "Day 1:\nDay 2:\n... and so on."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful travel planner."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        return f"Sorry, something went wrong while generating your itinerary: {str(e)}"


# Optional API endpoint for frontend JavaScript
# @views.route('/generate-plan', methods=['POST'])
# def generate_plan():
#     print("line no 97")
#     user_data = request.json
#     destination = user_data.get("destination")
#     days = user_data.get("days")
#     interests = user_data.get("interests")

#     itinerary = get_ai_itinerary(destination, days, interests)
#     return jsonify({"success": True, "itinerary": itinerary})




@views.route('/generate-plan', methods=['POST'])
def generate_plan():
    user_data = request.json
    destination = user_data.get("destination")
    days = user_data.get("days")
    interests = user_data.get("interests")

    prompt = f"""
    I want you to act as a travel planner.

    Generate a detailed {days}-day itinerary for a trip to {destination}.
    The traveler is interested in: {interests}.
    Include famous attractions, local food suggestions, and cultural experiences.
    Provide the plan day by day.
    """

    try:
        # Old method for version 0.1.0rc1
        response = genai.generate_text(
            model="models/gemini-2.5-flash",  # older text model
            prompt=prompt,
            temperature=0.7,
            max_output_tokens=1024
        )
        itinerary = response.result.strip()
    except Exception as e:
        print("Error generating plan:", e)
        return jsonify({"success": False, "error": str(e)}), 500

    return jsonify({"success": True, "itinerary": itinerary})
