# homework_bot
This telegram bot was made to make it easier to get information about status of homework.
Each time the status changes, the bot sends a notification to your telegram account.

# Technologies:
Python, TelegramBot, Yandex.Practicum API

### How to launch the project:

Clone the repository and open it through terminal.
In some cases you need to use "python" instead of "python3".

Create and activate virtual environment:
* If you have Linux/macOS
    ```
    python3 -m venv env 
    source env/bin/activate
    ```

* If you have windows
    ```
    python3 -m venv venv
    source venv/scripts/activate
    ```
Then upgrade pip
```
python3 -m pip install --upgrade pip
```
Install all requirements from requirements.txt file:
```
pip install -r requirements.txt
```
Change the directory:
```
cd ./homework_bot/
```
Create .env file and add next variables:
PRACTICUM_TOKEN - profile token at Yandex.Practicum
TELEGRAM_TOKEN - token of telegram bot, which will send a message
CHAT_ID - your ID in telegram

Launch the project:
```
python3 homework.py
```

# Author
Ivanova Lina
