"""
Author: Singa Maurice Shanga
Date: 11 March 2025
Version: 1.0
Description: 
    This script interacts with Google APIs using OAuth 2.0 authentication.
    It writes errors log details from the Telerivet API to a sheets designed
    to save the daily report.

License: Greenlight Planet

Dependencies:
    The following Python packages must be installed for this script to work:
    - google-auth
    - google-auth-oauthlib
    - google-auth-httplib2
    - google-api-python-client

Installation:
    To install the required dependencies, run:
    pip3 install telerivet
    pip3 install --upgrade google-api-python-client google-auth-httplib2 google-auth-oauthlib
"""

from datetime import datetime, date, time as dt_time
import time
import os
import telerivet
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from datetime import datetime

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "11hPihYyR1gFZ1UnJgy1yG2lUvToHegj8P4aKT_MMzwU"
# Defining the scope as all actions available to Spreadsheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
RANGE="Sms_Summary_count!A2"

# Getting file path
def get_file_path(file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)
    if os.path.exists(file_path):
        return file_path
    else:
        raise FileNotFoundError("File not found!")
    


SERVICE_ACCOUNT_FILE = get_file_path('Telerivet_Report_Ke.json')
creds = None
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

def get_failed_messages_count(API_KEY: str, tz_project_id: str, delay: int = 6) -> list:
    """
    Retrieve logs with a fail status and return an array of all the errors from the current day
    """
    messages = []
    current_date = date.today()

    # Create datetime objects for start/end of day
    start_of_day = datetime.combine(current_date, dt_time.min)
    end_of_day = datetime.combine(current_date, dt_time.max)
    
    # Convert to UTC timestamps
    start_timestamp = int(start_of_day.timestamp())
    end_timestamp = int(end_of_day.timestamp())

    tr = telerivet.API(API_KEY)
    project = tr.initProjectById(tz_project_id)

    try:
        cursor = project.queryMessages(
            direction="outgoing",
            message_type="sms",
            status="sent",
            time_created={"min": start_timestamp, "max": end_timestamp}
        )

        for message in cursor.all():
            # Convert timestamp to UTC datetime
            utc_time = datetime.utcfromtimestamp(message.time_sent)
            
            messages.append({
                "status": message.status,
                "error log": message.error_message,
                "from number": message.from_number,
                "to number": message.to_number,
                "time_sent": utc_time.strftime('%Y-%m-%d %H:%M:%S UTC')
            })

    except telerivet.APIException as e:
        print(f"API Error: {e}")
        time.sleep(delay)
    
    return len(messages)


def save_to_sheets(data):
  """
    Save error logs to spreadsheet.
  """

  try:
    service = build("sheets", "v4", credentials=creds)
    date_log = datetime.today().strftime("%Y-%m-%d")

    # Call the Sheets API
    sheet = service.spreadsheets()

    if not data:
      print("Error getting data!!")
      exit()
    # Converting the dictionary from telerivet to a list and prepare data to be send
    # through Google Sheets API
    data_to_append = [[ date_log, "Total Sent SMS", data, 'Tanzania' ]]

    # Body to be passed to the Google API
    body = {
        "values": data_to_append
    }

    # Call the Google Sheets API to append the data from Telerivet function
    response = sheet.values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=RANGE,
            valueInputOption="RAW",
            insertDataOption="INSERT_ROWS",
            body=body,
        ).execute()

  except HttpError as err:
    print(err)

# Important keys to be deleted on Github
API_KEY = "Kldps_2TelsJ2O7PKrePmB7tWDk8ZxAUawxs"
KEN_PROJECT_ID = "PJfa48114ec238c778684060c88b822385"

# Calling all the functions written above
failed_messages = get_failed_messages_count(API_KEY, KEN_PROJECT_ID)
save_to_sheets = save_to_sheets(failed_messages)
print(failed_messages)
print(save_to_sheets)