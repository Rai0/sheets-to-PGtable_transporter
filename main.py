import httplib2
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials as SAC

import psycopg2
import os
from dotenv import load_dotenv

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)



SHEET_ID = "1uAqCeIWbx_Ag0CBK6ni-zAKTbmWfp1JjFQbcWZ6rTWk"
API_TOKEN_FILE = "token.json"
TABLE_RANGE = "A1:D51"

class SheetsExemplar:
    def __init__(self, SHEET_ID=SHEET_ID, API_TOKEN_FILE=API_TOKEN_FILE, TABLE_RANGE=TABLE_RANGE) -> None:
        self.SHEET_ID = SHEET_ID
        self.API_TOKEN_FILE = API_TOKEN_FILE
        self.TABLE_RANGE = TABLE_RANGE
    
    SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets", 
    "https://www.googleapis.com/auth/drive"
    ]
    
    CREDENTIALS = SAC.from_json_keyfile_name(
    API_TOKEN_FILE,
    SCOPES
    )

    httpAuth = CREDENTIALS.authorize(httplib2.Http())
    service = apiclient.discovery.build("sheets", "v4", http = httpAuth)

    value = service.spreadsheets().values().get(
        spreadsheetId=SHEET_ID,
        range=TABLE_RANGE,
        majorDimension="ROWS"
    ).execute()



def get_data_from_google_api (self):
    return "Ты крутой"

if __name__ == "__main__":
    print (get_data_from_google_api(''))