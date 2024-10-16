import google.generativeai as genai
import os
import json
import datetime
import os.path
from pypdf import PdfReader
from dotenv import load_dotenv
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

load_dotenv() 

genai.configure(api_key=os.getenv("Gemini_Api"))
model = genai.GenerativeModel('gemini-1.5-flash')
SCOPES = ["https://www.googleapis.com/auth/calendar", "https://www.googleapis.com/auth/calendar.events"]

#creds = None
  # The file token.json stores the user's access and refresh tokens, and is
  # created automatically when the authorization flow completes for the first
  # time.
#if os.path.exists("token.json"):
  #creds = Credentials.from_authorized_user_file("token.json", SCOPES)
  # If there are no (valid) credentials available, let the user log in.
#if not creds or not creds.valid:
#  if creds and creds.expired and creds.refresh_token:
#    creds.refresh(Request())
#  else:
#    flow = InstalledAppFlow.from_client_secrets_file(
#        "credentials.json", SCOPES
#    )
#    creds = flow.run_local_server(port=3000)
    # Save the credentials for the next run
#   with open("token.json", "w") as token:
#      token.write(creds.to_json())


reader = PdfReader("Syllabus_3339_13728.pdf")
number_of_pages = len(reader.pages)
page = ''
text = ''
text_list = []
for i in range(number_of_pages):
  page = reader.pages[i]
  text = page.extract_text()
  text_list.append(text)
text = ''.join(text_list)
#End_of_doc = text.index('Mental Health and Wellness Resources')
#text = text[:End_of_doc]

def Important_date(prompt):
  response = model.generate_content(prompt + text)
  return response.text
  
def generate_ordinal_list():
  ordinals = []
  suffixes = {1: "st", 2: "nd", 3: "rd"}

  for i in range(1, 1001):
      if 10 <= i % 100 <= 20:  # Special case for teens (e.g., 11th, 12th, 13th)
          suffix = "th"
      else:
          suffix = suffixes.get(i % 10, "th")

      # Append the ordinal string to the list
      ordinals.append(f"{i}{suffix}")

  return ordinals

def Addevent(event):
  try:
    service = build("calendar", "v3", creds)

    # Call the Calendar API
    now = datetime.datetime.utcnow().isoformat() + "Z"  # 'Z' indicates UTC time
    event = service.events().insert(calendarId='onyekachukwumuoghalu@gmail.com', body=event).execute()
  except HttpError as error:
    print(f"An error occurred: {error}")

# Example usage
ordinal_list = generate_ordinal_list()
#print(ordinal_list)

prompt_2 = """Given the attached syllabus document, 
count the number of due dates. Return the result in this exact format:

The document you provided mentions (number of due dates) due dates with specific DUE dates.

Do not include any additional text or information."""
event_string_2 = Important_date(prompt_2)
print(event_string_2)
num_of_events = event_string_2[35]

i = 36
event_list = []
while(event_string_2[i] != ' '):
    num_of_events = num_of_events + event_string_2[i]
    i = i + 1
num_of_events = int(num_of_events)
print(num_of_events)
prompt = """Given the attached syllabus document,  
return all events that contain a date.  
An event is either an exam, homework, deadline, or any other relevant activity with a date.  
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

event_string = Important_date(prompt)
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
print(len(event_list))
#for i in range(num_of_events):()
#   Addevent(event_list[i])
    
