from json import load
from telebot import *
from telebot.types import *
from mariadb import *
from database.database import *
from time import time
from sys import exit
import mariadb
from datetime import datetime
import pytz

moscow_tz = pytz.timezone('Europe/Moscow')

try: 
    print("Reading configures.json...")
    configures = load(open("globals/configures.json", encoding="utf-8"))
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


API = open("API.txt", 'r').read().split(sep="\n")[0]
messages = configures['messages']
stations = configures['stations']

bot = TeleBot(API)

@bot.message_handler(commands=['start'])
def start(message):
    print(users.get_info(message.chat.username))
    if users.get_info(message.chat.username) == -1:
        bot.send_message(message.chat.id, messages['start'])
        
        # даём выбор в команде человек или нет
        keyboard = InlineKeyboardMarkup()
        solo = InlineKeyboardButton(text="Я играю один", callback_data="start:solo")
        team = InlineKeyboardButton(text="Я играю с командой", callback_data="start:team")

        keyboard.add(solo)
        keyboard.add(team)

        bot.send_message(message.chat.id, messages['solo/team'], reply_markup=keyboard)
    else:

        bot.send_message(message.chat.id, messages['already'])

# funcs
## solo registration
def solo_registration(message):
    bot.send_message(message.chat.id, messages["solo-start"])
    bot.register_next_step_handler(message, solo_registration_2)

def solo_registration_2(message):
    users.insert(message.chat.username, message.text, message.text)
    users.team_size(message.chat.username, 1)
    bot.send_message(message.chat.id, text=messages["success"])


## team registration
def team_registration(message):
    bot.send_message(message.chat.id, messages["team-start"])
    bot.register_next_step_handler(message, team_registration_2)

def team_registration_2(message):
    bot.send_message(message.chat.id, messages["team-members"])
    bot.register_next_step_handler(message, team_registration_3)

def team_registration_3(message):
    users.insert(message.chat.username, message.text, message.text)
    bot.send_message(message.chat.id, text=messages["people"])
    bot.register_next_step_handler(message, team_registration_4)

def team_registration_4(message):
    users.team_size(message.chat.username, message.text)
    bot.send_message(message.chat.id, text=messages["success"])

@bot.message_handler(commands=['choose'])
def choose(message):
    print(users.get_info(message.chat.username))
    if users.get_info(message.chat.username) != -1:
        if users.get_info(message.chat.username)[0][4] == "0":
            markup = InlineKeyboardMarkup()

            for station in stations:
                if not(station in users.get_info(message.chat.username)[0][3].split(sep=" ")) and users.get_all_users_on_station(stations[station]["id"]) < stations[station]["max-people"]:
                    button = InlineKeyboardButton(text=stations[station]["name"], callback_data=f"station:{stations[station]['id']}")
                    markup.add(button)

            bot.send_message(message.chat.id, messages["choose"], reply_markup=markup)
        else:
            current_station = users.get_info(message.chat.username)[0][4]
            keyboard = InlineKeyboardMarkup()
            tip = InlineKeyboardButton("get tip", callback_data=f"tip:{current_station}")
        
            keyboard.add(tip)
            bot.send_message(message.chat.id, messages['unfinished'], reply_markup=keyboard)

    elif users.get_info(message.chat.username) != []:
        bot.send_message(message.chat.id, messages["not-registrated"])

    elif current_station != "0":
        bot.send_message(message.chat.id, messages["enter-finishcode"] + current_station, reply_markup=keyboard)
        bot.register_next_step_handler(message, finish, station=current_station)
            
    else:
        bot.send_message(message.chat.id, messages["not-registrated"])

@bot.message_handler()
def text(message):
    if users.get_info(message.chat.username) != -1:
    
        current_station = users.get_info(message.chat.username)[0][4]
        keyboard = InlineKeyboardMarkup()
        tip = InlineKeyboardButton("get tip", callback_data=f"tip:{current_station}")
        keyboard.add(tip)

        if current_station != "0":
            bot.send_message(message.chat.id, messages["enter-finishcode"] + current_station, reply_markup=keyboard)
            bot.register_next_step_handler(message, finish, station=current_station)
    else:
        bot.send_message(message.chat.id, messages["not-registrated"])

# callback
@bot.callback_query_handler(func = lambda call: True)
def callback(call):
    if call.data.split(sep=":")[0] == "start":
        if call.data.split(sep=":")[1] == "solo":
            solo_registration(call.message)
        elif call.data.split(sep=":")[1] == "team":
            team_registration(call.message)
    elif call.data.split(sep=":")[0] == "station":
        station_id = call.data.split(sep=":")[1]
        now_moscow = datetime.now(moscow_tz)
        for iterator in range(len(stations[station_id]["time-start"])):
            print(f"start time {iterator}: {int(stations[station_id]["time-start"][iterator].split(":")[0]) * 60 +\
            int(stations[station_id]["time-start"][iterator].split(":")[1])}")

            print(f"finish time {iterator}: {int(stations[station_id]["time-finish"][iterator].split(":")[0]) * 60 +\
            int(stations[station_id]["time-finish"][iterator].split(":")[1])}")

            print(f"current time: {now_moscow.hour * 60 + now_moscow.minute}")


            if (int(stations[station_id]["time-start"][iterator].split(":")[0]) * 60 +\
            int(stations[station_id]["time-start"][iterator].split(":")[1])) \
                  <=  now_moscow.hour * 60 + now_moscow.minute and \
                      now_moscow.hour * 60 + now_moscow.minute <= \
            int(stations[station_id]["time-finish"][iterator].split(":")[0]) * 60 +\
            int(stations[station_id]["time-finish"][iterator].split(":")[1]):
                if users.get_all_users_on_station(station_id) + users.get_info(call.message.chat.username)[0][5] <= stations[station_id]["max-people"]:
                    bot.send_message(call.message.chat.id, stations[station_id]["description"])
                    bot.send_message(call.message.chat.id, stations[station_id]["quote"])
                    if stations[station_id]["filepath"] != "none":
                        try:
                            file = open(stations[station_id]["filepath"], "rb")
                            bot.send_document(call.message.chat.id, file)
                        except:
                            bot.send_message(call.message.chat.id, "File not found :/")
                    keyboard = InlineKeyboardMarkup()
                    yes = InlineKeyboardButton("yes", callback_data=f"finish:{station_id}")
                    no = InlineKeyboardButton("no", callback_data=f"dont_want")

                    keyboard.add(yes)
                    keyboard.add(no)

                    bot.send_message(call.message.chat.id, messages["sure"], reply_markup=keyboard)
                    break
                else:
                    bot.send_message(call.message.chat.id, messages["full"])
                    break
        else:
            bot.send_message(call.message.chat.id, "Не время")
    elif call.data.split(sep=":")[0] == "finish":
        station_id = call.data.split(sep=":")[1]
        users.set_current(call.message.chat.username, station_id)

        keyboard = InlineKeyboardMarkup()
        tip = InlineKeyboardButton("get tip", callback_data=f"tip:{station_id}")

        bot.send_message(call.message.chat.id, messages["enter-finishcode"] + station_id, reply_markup=keyboard)
        bot.register_next_step_handler(call.message, finish, station=call.data.split(sep=":")[1])
    elif call.data.split(sep=":")[0] == "tip":
        station_id = call.data.split(sep=":")[1]
        bot.send_message(call.message.chat.id, stations[station_id]["quote"])
        bot.send_message(call.message.chat.id, messages["enter-finishcode"] + station_id)

        bot.register_next_step_handler(call.message, finish, station=call.data.split(sep=":")[1])
    elif call.data == "dont_want":
        bot.send_message(call.message.chat.id, messages["dont_want"])

def finish(message, station):
    attempt = ""

    for s in message.text.lower():
        if not(s in ",.!-"):
            attempt += s
    print(f"User attempt: {attempt}")
    print(f"Finish code: {stations[station]["finish-code"].lower()}")
    if attempt == stations[station]["finish-code"].lower():
        users.set_current(message.chat.username, "0")
        users.add(message.chat.username, station)
        bot.send_message(message.chat.id, messages["finished"])
    else:
        keyboard = InlineKeyboardMarkup()
        tip = InlineKeyboardButton("get tip", callback_data=f"tip:{station}")
        
        keyboard.add(tip)

        bot.send_message(message.chat.id, "Incorrect")
        bot.send_message(message.chat.id, messages["enter-finishcode"], reply_markup=keyboard)
        bot.register_next_step_handler(message, finish, station=station)



if __name__ == "__main__":
    bot.infinity_polling()