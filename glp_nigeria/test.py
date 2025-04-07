
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

error_counts = error_log_occurrence(failed_messages)
print(error_counts)

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google.oauth2 import service_account
import datetime

# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = "11hPihYyR1gFZ1UnJgy1yG2lUvToHegj8P4aKT_MMzwU"
# Defining the scope as all actions available to Spreadsheets
SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
# Path to the key created from the console cloud.
# In my case I have it in the same folder with the Python files
SERVICE_ACCOUNT_FILE = 'Telerivet_Report_Ke.json'
RANGE="Failed_Logs_Summary_All_Markets!A2"


creds = None
creds = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)


def save_to_sheets(data):
  """
    Save error logs to spreadsheet.
  """

  try:
    service = build("sheets", "v4", credentials=creds)
    date_log = datetime.date.today().strftime("%Y-%m-%d")

    # Call the Sheets API
    sheet = service.spreadsheets()

    if not data:
      print("Error getting data!!")
      exit()
    # Converting the dictionary from telerivet to a list and prepare to be send
    # through Google Sheets API
    data_to_append = [[ date_log, key, value, 'Kenya' ] for key, value in data.items()]

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

# Important keys to be deleted on Github
API_KEY = "9ryvf_7TrRWrzcaGC4BhmYijolLeLBTUUWkK" # Ngr 9ryvf_7TrRWrzcaGC4BhmYijolLeLBTUUWkK
KEN_PROJECT_ID = "PJc52ea35f23f0d960"

# Colling all the functions written above
failed_messages = get_failed_messages(API_KEY, KEN_PROJECT_ID)
error_counts = error_log_occurrence(failed_messages)
save_to_sheets = save_to_sheets(error_counts)
print(error_counts)
print(save_to_sheets)