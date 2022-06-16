# Как развернуть

    1. Создать в [Google Developers Console](https://console.cloud.google.com/apis/dashboard) создать проект и подключить к нему Google Sheets и Google Drive.
    2. В ранее созданном проекте создать Service Accounts и скачать его токен в виде josn файла.
    3. Клонировать репозиторий `git clone https://github.com/Rai0/tt.git`.
    4. Ранее скаченный токен Google Service Account переименовать в token.json и с копировать в папку клонированного репозитория.
    5. Создать виртуальное окруженме python `python -m venv env`
    6. Активировать виртуальное окружение и установить все библиотеки из файла requirements.txt `pip install -r requirements.txt`.
    7. Создать .env файл и ввести в него все переменные окружения, а именно необходимые для работы с postgreSQL хост, имя пользователя, пароль и имя базы данных, а также id Google Sheets таблицы. 
    ```
        HOST=""
        USER=""
        PASSWORD=""
        DBNAME=""
        SHEET_ID=""
    ```
    8. Запустить скрипт `python main.py`.