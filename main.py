import httplib2
import requests 
import apiclient.discovery
from oauth2client.service_account import ServiceAccountCredentials as SAC
import xmltodict
import psycopg2
import os
from dotenv import load_dotenv
import datetime
import time as t

dotenv_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)



SHEET_ID = os.environ.get("SHEET_ID")
API_TOKEN_FILE = "token.json"
TABLE_RANGE = "A2:D51"

HOST = os.environ.get("HOST")
USER = os.environ.get("USER")
PASSWORD = os.environ.get("PASSWORD")
DBNAME = os.environ.get("DBNAME")

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

    value = ''

    httpAuth = CREDENTIALS.authorize(httplib2.Http())
    service = apiclient.discovery.build("sheets", "v4", http = httpAuth)
    try:
        value = service.spreadsheets().values().get(
            spreadsheetId = SHEET_ID,
            range = TABLE_RANGE,
            majorDimension = "ROWS"
        ).execute()["values"]
    except Exception as ex:
        print ("[ERROR] failed to retrieve data from google api", ex)

class USDValue:

    currency_value=''
    currency_kod="USD"
    endpoint="https://www.cbr.ru/scripts/XML_daily.asp"

    try:
        response = requests.get(endpoint, stream=True)
    except Exception as ex:
        print ("[ERROR] failed to retrieve data from server cbr", ex)
    
    dict_data = xmltodict.parse(response.content)
    
    for i in dict_data["ValCurs"]["Valute"]:
        if i["CharCode"] == currency_kod:
            currency_value = i["Value"]

    currency_value = round(float(currency_value.replace(",", ".")), 2)

class DB(SheetsExemplar):
    def __init__ (self, RUB, host=HOST, user=USER, password=PASSWORD, db_name=DBNAME):
        self.host = host
        self.user = user
        self.password = password
        self.db_name = db_name
        self.RUB = RUB
    
    def db_connect_decorator (func):
        def decorator_wrapper (self):
            connect = psycopg2.connect (
                host = self.host,
                user = self.user,
                password = self.password,
                database = self.db_name
            )
            connect.autocommit=True
            func(self, connect)
            connect.close ()
        return decorator_wrapper

    @db_connect_decorator
    def _clear_db (self, connect) -> None:
        with connect.cursor () as cursor:
            cursor.execute (
                """CREATE TABLE IF NOT EXISTS estimate(
                    id serial PRIMARY KEY,
                    order_number integer NOT NULL,
                    cost_USD integer NOT NULL,
                    cost_RUB integer NOT NULL, 
                    delivery_date date NOT NULL
                );
                TRUNCATE TABLE estimate;"""
            )

    @db_connect_decorator
    def enter_data (self, connect) -> None:
        if super().value:
            self._clear_db()
            with connect.cursor () as cursor:
                for i in super().value:
                    id = int(i[0])
                    order = int(i[1])
                    usd = int(i[2])
                    rub = int(i[2]) * self.RUB
                    delivery_date = datetime.datetime.strptime(i[3], ("%d.%m.%Y"))
                    try:
                        cursor.execute("INSERT INTO estimate (id, order_number, cost_USD, cost_RUB, delivery_date) VALUES (%s, %s, %s, %s, %s)", (str(id), str(order), usd, rub, str(delivery_date)))
                    except Exception as ex:
                        print ("[ERROR] failed to add data to the database", ex)
                print ("[INFO] data was successfully added to the database")

def loop_decorator(func):
    def wrapper ():
        print ("[INFO] loop start")
        last_update_date = None
        USD_to_RUB = ""
        while True: 
            if last_update_date == None or last_update_date.date() != datetime.datetime.now().date ():
                last_update_date = datetime.datetime.now()
                USD_to_RUB = USDValue().currency_value
                print (f"[INFO] Update currency value, USD exchange rate = {USD_to_RUB}")
            func (USD_to_RUB)
            t.sleep (600)
    return wrapper 

@loop_decorator
def get_data_from_google_api (currency_value):
    return (DB(currency_value).enter_data())

if __name__ == "__main__":
    print (get_data_from_google_api())