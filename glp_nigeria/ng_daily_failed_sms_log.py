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
import time
import telerivet

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


API_KEY = "Kldps_2TelsJ2O7PKrePmB7tWDk8ZxAUawxs"
# API_KEY = "9ryvf_7TrRWrzcaGC4BhmYijolLeLBTUUWkK" #w_n6I_mg7AINI7n2i3ejMHShsCPYVfevEvqo Kn # Ngr w_n6I_HxzMBeFAfMTwaoTabbQ9FWsJR5nEHb
NG_PROJECT_ID = "PJc52ea35f23f0d960"
failed_messages = get_failed_messages(API_KEY, NG_PROJECT_ID)
print(failed_messages)