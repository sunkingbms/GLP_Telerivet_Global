"""
  Author: Singa Maurice Shanga
  Date: 11 March 2025
  Version: 1.0
  Description:
      This script interacts with Google APIs using OAuth 2.0 authentication.
      It writes errors log details from the Telerivet API to a sheets designed
      to save the daily report.

  Dependencies:
      The following Python packages must be installed for this script to work:
      - google-auth
      - google-auth-oauthlib
      - google-auth-httplib2
      - google-api-python-client

  Installation:
      To install the required dependencies, run:
      pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client
"""

import datetime
import os
import time
import telerivet

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "11hPihYyR1gFZ1UnJgy1yG2lUvToHegj8P4aKT_MMzwU"
# Defining the scope as all actions available to Spreadsheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
RANGE="Failed_Logs_Summary_All_Markets!A2"


# Getting file path
def get_file_path(file_name):
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, file_name)
    if os.path.exists(file_path):
        return file_path
    else:
        raise FileNotFoundError("File not found!")

def get_failed_messages(API_KEY: str, NG_PROJECT_ID: str, delay: int = 6) -> list:
    """
    Retrieve logs with a fail status and return an array of all the errors from the current day
    """
    messages = []
    today = datetime.date.today()

    start_of_day = int(datetime.datetime.combine(today, datetime.time.min).timestamp())
    end_of_day = int(datetime.datetime.combine(today, datetime.time.max).timestamp())

    tr = telerivet.API(API_KEY)
    project = tr.initProjectById(NG_PROJECT_ID)

    try:
        cursor = project.queryMessages(
            direction="outgoing",
            message_type="sms",
            status="failed",
            time_created={"min": start_of_day, "max": end_of_day}
        )

        for message in cursor.all():
            messages.append({
                "status": message.status,
                "error log": message.error_message,
                "from number": message.from_number,
                "to number": message.to_number,
                "time_sent": datetime.datetime.utcfromtimestamp(message.time_sent).strftime('%Y-%m-%d %H:%M:%S')
            })

    except telerivet.APIException as e:
        print(f"Error occurred: {e}")
        time.sleep(delay)

    return messages

def error_log_occurrence(data: list) -> dict:
    """
    Analyze error logs and return occurrence count of each error type.
    """
    try:
        if not data:
            print("Empty array passed")
            return {}
        error_log: dict = {}
        for error in data:
            error_message = error["error log"]
            error_log[error_message] = error_log.get(error_message, 0) + 1
        return error_log
    except Exception as e:
        print(f"Error occurred: {e}")
        return{}

API_KEY = "Kldps_2TelsJ2O7PKrePmB7tWDk8ZxAUawxs"
TZ_PROJECT_ID = "PJ951527fbf8258b5e"

failed_messages = get_failed_messages(API_KEY, TZ_PROJECT_ID)
error_counts = error_log_occurrence(failed_messages)
print(failed_messages)


from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
from datetime import datetime

SERVICE_ACCOUNT_FILE = get_file_path('Telerivet_Report_Ke.json')
creds = None
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)

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
    # Converting the dictionary from telerivet to a list and prepare to be send
    # through Google Sheets API
    data_to_append = [[ date_log, key, value, 'Uganda' ] for key, value in data.items()]

    # Body to be passed to the Gogle API
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

# Colling all the functions written above
save_to_sheets = save_to_sheets(error_counts) 


