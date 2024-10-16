from dotenv import load_dotenv
import google.generativeai as genai
import os

load_dotenv() 

genai.configure(api_key=os.getenv("Gemini_Api"))
model = genai.GenerativeModel('gemini-1.5-flash')

prompt = """ Give me a one page summary for this syallbi please make sure to include all the important dates and details"""
def Important_date(prompt):
  response = model.generate_content(prompt)
  return response.text