from flask_cors import CORS
from dotenv import load_dotenv
from flask import Flask, request, render_template, redirect, url_for, jsonify, session
from authlib.integrations.flask_client import OAuth
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from pypdf import PdfReader
import os
import json
import google.generativeai as genai
import datetime

# Load environment variables from .env file
Message = {"Sucess": "Processing Complete Please check your calendar", "Failure": "This is not a syallbus an error occured"}
load_dotenv()

app = Flask(__name__)

UPLOAD_FOLDER = 'PDF_Syallabus'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

app.secret_key = '2468'  # Change to a secure key for production
genai.configure(api_key=os.getenv("Gemini_Api"))
model = genai.GenerativeModel('gemini-1.5-flash')
oauth = OAuth(app)

# Register Google OAuth provider
oauth.register(
    name='google',
    client_id=os.getenv("Google_ID"),
    client_secret=os.getenv("Google_Secret"),
    access_token_url='https://oauth2.googleapis.com/token',
    authorize_url='https://accounts.google.com/o/oauth2/v2/auth',
    userinfo_endpoint='https://openidconnect.googleapis.com/v1/userinfo',
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile https://www.googleapis.com/auth/calendar https://www.googleapis.com/auth/calendar.events' ,
        'prompt': 'consent',  # Optional: Forces consent screen to be shown every time
    }
)

# Routes
@app.route('/submit', methods=['GET', 'POST'])
def submit():
    if request.method == 'POST':
        return "Form submitted!"
    else:
        return "Submit form"
    
@app.route('/')
def home():
    return render_template('sign_in_page.html')

@app.route('/login')
def login():
    redirect_uri = url_for('authorize', _external=True)
    return oauth.google.authorize_redirect(redirect_uri)

@app.route('/mainpage', methods=['GET', 'POST'])
def mainpage():
    return render_template('index.html')

@app.route('/authorize')
def authorize():
    token = oauth.google.authorize_access_token()
    if token is None:
        return "Authorization failed", 400
    user_info = oauth.google.userinfo()
    session['user'] = user_info
    session['token'] = token
    return redirect(url_for('mainpage'))

@app.route('/profile')
def profile():
    user = session.get('user')
    token = session.get('token')
    print(user)
    print(token)
    return redirect(url_for('home'))

@app.route('/upload', methods=['GET','POST'])
def upload_file():
    if 'file-input' not in request.files:
        return 'No file part'
    file = request.files['file-input']
    
    if file.filename == '':
        return 'No selected file'
    
    if file and file.filename.endswith('.pdf'):
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
        file.save(filepath)
        # Now process the file
        return process_pdf(filepath)
    
def process_pdf(filepath):
    reader = PdfReader(filepath)
    number_of_pages = len(reader.pages)
    page = ''
    text = ''
    text_list = []
    for i in range(number_of_pages):
        page = reader.pages[i]
        text = page.extract_text()
        text_list.append(text)
    text = ''.join(text_list)
    prompt_2 = """Given the attached syllabus document, 
    count the number of due dates. Return the result in this exact format:

    The document you provided mentions (number of due dates) due dates with specific DUE dates.

    Do not include any additional text or information."""
    event_string_2 = Important_date(prompt_2, text)
    print(event_string_2)
    num_of_events = event_string_2[35]

    i = 36
    event_list = []
    while(event_string_2[i] != ' '):
        num_of_events = num_of_events + event_string_2[i]
        i = i + 1
    try: 
        num_of_events = int(num_of_events)
    except ValueError:
        if os.path.exists(filepath):
            os.remove(filepath)
            print(f"{filepath} has been deleted")
        data = {"message": Message.get("Failure")}
        return jsonify(data)
    print(num_of_events)
    prompt = """Given the attached syllabus document,  
    return all events that contain a date.  
    An event is either an exam, homework, deadline, or any other relevant activity with a date. 
    if the event does not have a start time make the start time be 2 days before the end time
    The events should be formatted as a Python dictionary in plain text, without any code 
    block symbols or formatting indicators, using the following structure:
    (
    {
    "summary": "Event Title",
    "location": "Event Location",
    "description": "Event Description",
    "start": {
    "dateTime": "YYYY-MM-DDTHH:MM:SS-00:00",
    "timeZone": "Time Zone"
    },
    "end": {
    "dateTime": "YYYY-MM-DDTHH:MM:SS-00:00",
    "timeZone": "Time Zone"
    },
    "reminders": {
    "useDefault": false,
    "overrides": [
    {"method": "email", "minutes": 2880},
    {"method": "popup", "minutes": 2880}
    ]
    }
    }
    )
    Make sure to include all events with dates and provide the output as plain text, 
    without any formatting indicators like backticks."""

    event_string = Important_date(prompt, text)
    print(event_string)
    while(len(event_string) != 0):
        for i in event_string:
            if i == ')':
                end_index = event_string.index(i)
                event_details = event_string[0:end_index+1:1]
                event_string = event_string[end_index+1::1]
                event_details = event_details.replace('(', '')
                event_details = event_details.replace(')', '')
            
                event_details = json.loads(event_details)
                event_list.append(event_details)
        print((len(event_string)))
        if(len(event_string) == 1):
            break
    
    print(event_list)
    for i in range(len(event_list)):
        Addevent(event_list[i])
    if os.path.exists(filepath):
        os.remove(filepath)
        print(f"{filepath} has been deleted")
    data = {"message": Message.get("Sucess")}
    return jsonify(data)

def Addevent(event):
    token = session.get('token')
    credentials = Credentials(
        token['access_token'],
        refresh_token=token.get('refresh_token'),
        token_uri='https://oauth2.googleapis.com/token',
        client_id=os.getenv('Calendar_ID'),
        client_secret=os.getenv('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')
    )
    user_info = session.get('user')  
    user_email = user_info.get('email')
    try:
        service = build('calendar', 'v3', credentials=credentials)
        now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
        event = service.events().insert(calendarId=user_email, body=event).execute()
        # Call the Calendar API
    except HttpError as error:
        print(f"An error occurred: {error}")
    
def Important_date(prompt, text):
  response = model.generate_content(prompt + text)
  return response.text
# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)  # You can run HTTPS locally with ssl_context if needed
