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
        # ✅ Capture all form fields
        destination = request.form.get('destination')  # If you add destination input
        days = request.form.get('days')               # If you add days input
        currency = request.form.get('currency')
        budget = request.form.get('budget')
        adults = request.form.get('adults')
        children = request.form.get('children')
        seniors = request.form.get('seniors')
        activities = request.form.get('activities')

        # Validate essential fields
        if not days or not activities:
            return render_template('plan_details.html', error="Please fill all required fields.")

        # Use activities as interests for AI
        itinerary = get_ai_itinerary(destination or "your chosen destination",
                                     days,
                                     activities)

        if not itinerary or itinerary.startswith("Sorry"):
            return render_template('plan_details.html', error=itinerary)

        # Pass all fields to the template
        return render_template(
            'ai_plan.html',
            itinerary=itinerary,
            destination=destination or "Not specified",
            days=days,
            currency=currency,
            budget=budget,
            adults=adults,
            children=children,
            seniors=seniors,
            activities=activities
        )

    return render_template('plan_details.html')


# AI itinerary generator using Gemini
def get_ai_itinerary(destination, days, interests):
    try:
        days = int(days)
    except ValueError:
        return "Invalid number of days."

    prompt = (
        f"You are a professional travel planner. Create a detailed {days}-day travel itinerary "
        f"for a trip to {destination} for someone interested in {interests}. "
        "Include famous attractions, local food, and cultural experiences. "
        "Provide the plan day by day in this format:\nDay 1: ...\nDay 2: ..."
    )

    try:
        model = genai.GenerativeModel("gemini-2.0-flash")  # Correct for v0.8.5
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Sorry, something went wrong while generating your itinerary: {str(e)}"


# API endpoint for Postman or frontend testing
@views.route('/generate-plan', methods=['POST'])
def generate_plan():
    user_data = request.json
    destination = user_data.get("destination", "Not specified")
    days = user_data.get("days", 1)
    interests = user_data.get("interests", "General travel")

    itinerary = get_ai_itinerary(destination, days, interests)

    return jsonify({"success": True, "itinerary": itinerary})
