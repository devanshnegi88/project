# from .import ai_bp
from flask import Blueprint, render_template, request, jsonify
import os,json

import google.generativeai as genai

chatbot_bp=Blueprint("ai_chatbot",__name__, url_prefix='/chatbot')
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

@chatbot_bp.route("/")
def home():
    return render_template("chatbot.html")

@chatbot_bp.route("/chat", methods=["POST"])
def chat():
    message=request,json.get("message","")
    if not message:
        return jsonify({"message is required"})
    
    prompt = f"""
 
    If a question is not related to study, reply with: "Sorry, I can only answer study-related questions."

     Question: {message}
      """
    model=genai.GenrativeModel("gemini-1.5-flash")
    response=model.generate_content(prompt)
    answer=response.text

    return jsonify({"response":answer})
                         