from json import load
from telebot import *
from telebot.types import *
from mariadb import *
from database.database import *
from time import time
from time import sleep
from sys import exit
import mariadb
from datetime import datetime
import pytz

moscow_tz = pytz.timezone('Europe/Moscow')
RESIDENTS = 3


try: 
    print("Reading configures.json...")
    configures = load(open("globals/configures.json", encoding="utf-8"))
    resident = load(open("globals/resident.json", encoding="utf-8"))
    print("Task completed.")
except:
    print("Wrong configures.json location!")
    exit(0)

try:
    print("Connecting to mariadb...")
    mariaconnection = MariaConnection(configures["database"])
    print("Task completed.")
    
    print("Connecting to users...")
    users = Users(mariaconnection)
    print("Task completed.")

except mariadb.ProgrammingError as e:
    print(e)
    print("Wrong mariaconnection params!")
    exit(0)

API = open("API_2.txt", "r").read().split(sep='\n')[0]

bot = TeleBot(API)

subscribed_users = users.get_all_resident_users()
print(subscribed_users)

# Функция для проверки времени и отправки сообщения
def check_time_and_send():
    while True:

        now_moscow = datetime.now(moscow_tz)
        for iterator in range(len(resident["time"]["time-start"])):
            print(int(resident["time"]["time-start"][iterator].split(sep=":")[0]) * 60 + \
                int(resident["time"]["time-start"][iterator].split(sep=":")[1]))
            
            print(now_moscow.hour * 60 + now_moscow.minute)

            if now_moscow.hour * 60 + now_moscow.minute + 10 == int(resident["time"]["time-start"][iterator].split(sep=":")[0]) * 60 + \
                int(resident["time"]["time-start"][iterator].split(sep=":")[1]):
                sent_users = []
                for x in range(RESIDENTS):
                    try:
                        random_user = random.choice(subscribed_users)[0]
                    except IndexError:
                        print("All users are busy now!")
                        break
                    sent_users.append(random_user)
                    
                    print(random_user)

                    keyboard = InlineKeyboardMarkup()
                    yes = InlineKeyboardButton("yes", callback_data="resident")
                    no = InlineKeyboardButton("no", callback_data="none")

                    keyboard.add(yes)
                    keyboard.add(no)

                    bot.send_message(random_user, resident["messages"]["reg"], reply_markup=keyboard)
                    users.set_current_by_id(random_user, -1)
                sleep( \
                int(resident["time"]["time-stop"][iterator].split(sep=":")[0]) * 60 + \
                int(resident["time"]["time-stop"][iterator].split(sep=":")[1]) - 
                int(resident["time"]["time-start"][iterator].split(sep=":")[0]) * 60 + \
                int(resident["time"]["time-start"][iterator].split(sep=":")[1]))
                
        sleep(60)

@bot.callback_query_handler(func = lambda call: True)
def callback(call):
    if call.data == "yes":
        users.set_current(call.from_user.username, 0)
        users.add(call.message.chat.username, -1)
    else:
        print(int(users.get_info(call.from_user.username)[0][4]))
        if int(users.get_info(call.from_user.username)[0][4]) != -1:
            users.set_current(call.from_user.username, 0)

thread = threading.Thread(target=check_time_and_send)
thread.start()

bot.polling(none_stop=True)