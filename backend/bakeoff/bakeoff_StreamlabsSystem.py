#---------------------------------------
#   Import Libraries
#---------------------------------------
import os
import codecs
import json
import random as random
import time as t

#---------------------------------------
#   [Required]  Script Information
#---------------------------------------
ScriptName = "!bakeoff script"
Website = "https://github.com/SteanKotze/scripts-holdmydonut.git"
Creator = "I_am_steak"
Version = "0.1"
Description = "This script allows users to start a bake off"

#---------------------------------------
#   Set Variables
#---------------------------------------
settings_path = "Services\\Scripts\\scripts-donut\\backend\\first_payout\\first_payout_settings.json"
settings = None

#   Script related
tick_refresh_rate = None
last_tick = None

bakeoff_users = []
bakeoff_users_entry_fees = []

bakeoff_state = None                                                                                            # 1=entry, 2=bakeoff, 3=cooldown, 4=idle
bakeoff_initialisation_time = None                                                                              # the first point in time when the next bakeoff can start
bakeoff_entry_time = None                                                                                       # how long users can join the next bakeoff
bakeoff_start_time = None                                                                                       # the time when the next bakeoff starts
bakeoff_cook_time = None                                                                                        # the amount of time a user has to complete a bakeoff
bakeoff_end_time = None                                                                                         # the time that the current bakeoff ends
bakeoff_cooldown_time = None                                                                                    # how long after the previous bakeoff before the next bakeoff can start

#---------------------------------------
#   [Required] Intialize Data 
#---------------------------------------
def Init():
    #   globals
    global tick_refresh_rate
    global last_tick

    global settings_path
    global settings

    global bakeoff_state
    global bakeoff_cooldown_time
    global bakeoff_initialisation_time
    global bakeoff_entry_time
    global bakeoff_start_time
    global bakeoff_cook_time
    global bakeoff_end_time

    #   init
    with codecs.open(settings_path, encoding="utf-8-sig", mode="r") as settings_file:
        settings = json.load(settings_file, encoding="utf-8")

    #if (settings != None):
    #    tick_refresh_rate = int(settings['tick_refresh_rate'])
    #    bakeoff_entry_time = int(settings['entry_time'])
    #    bakeoff_cooldown_time = int(settings['cooldown_time'])
    #
    #else:
    tick_refresh_rate = 5
    bakeoff_entry_time = 10
    bakeoff_cook_time = 10
    bakeoff_cooldown_time = 15

    last_tick = t.time()
    bakeoff_state = 4
    bakeoff_initialisation_time = t.time()

#---------------------------------------
#   [Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
    if (data.IsChatMessage() and data.IsFromTwitch()):
        bakeoff(data.User, data.Message)

    return

#---------------------------------------
#   [Required] Execute Data / Process Messages
#---------------------------------------
def Tick():
    #   globals
    global tick_refresh_rate
    global last_tick

    #   functionality
    current_time = t.time()
    if (last_tick + tick_refresh_rate <= current_time):
        last_tick = current_time
        bakeoff_tick()

    return

#---------------------------------------
#   !bakeoff
#---------------------------------------
def bakeoff(user, message):
    #   globals
    global bakeoff_users
    global bakeoff_users_entry_fees

    global bakeoff_state
    global bakeoff_initialisation_time

    #   functionality
    try:
        if ((message.find("!bakeoff") == 0) and (user not in bakeoff_users)):
            if ((t.time() >= bakeoff_initialisation_time) and (bakeoff_state == 1 or bakeoff_state == 4)):
                bakeoff_user_entry_amount = extract_donuts(message)
                if (pay_donuts(user, bakeoff_user_entry_amount)):
                    bakeoff_users.append(user)
                    bakeoff_users_entry_fees.append(bakeoff_user_entry_amount)
                    start_bakeoff(user, bakeoff_user_entry_amount)
            
            else:
                Parent.SendTwitchMessage("@" + user + " , you will be able to enter a new bakeoff in ") # ToDo

    except Exception as e:
        Parent.SendTwitchWhisper("i_am_steak", e.message)
        Parent.SendTwitchWhisper("i_am_not_steak", e.message)

def bakeoff_tick():
    #   globals
    global bakeoff_users
    global bakeoff_users_entry_fees

    global bakeoff_cooldown_time
    global bakeoff_initialisation_time
    global bakeoff_state
    global bakeoff_start_time
    global bakeoff_cook_time
    global bakeoff_end_time

    #   variables
    current_time = t.time()

    #   functionality
    if (( bakeoff_state == 1 ) and ( bakeoff_start_time <= current_time )):
        bakeoff_end_time = current_time + bakeoff_cook_time
        bakeoff_state = 2

        Parent.SendTwitchMessage("Ready. Set. Bake! Our bakers have 5 minutes to complete their creations for the judges!")

    elif (( bakeoff_state == 2) and ( bakeoff_end_time <= current_time )):
        bakeoff_initialisation_time = current_time + bakeoff_cooldown_time
        bakeoff_state = 3

        for i in range(0, len(bakeoff_users)):
            Parent.AddPoints(bakeoff_users[i], int(float(bakeoff_users_entry_fees[i]) * 1.25))

        bakeoff_users = []
        bakeoff_users_entry_fees = []

        Parent.SendTwitchMessage("Bakeoff completed!")

    elif (( bakeoff_state == 3) and (bakeoff_initialisation_time <= current_time)):
        bakeoff_state = 4
        
        Parent.SendTwitchMessage("You can now start a new bakeoff!")

#---------------------------------------
#   backend
#---------------------------------------
def extract_donuts(message):
    split_message = message.split(' ')
    if (split_message[0] == "!bakeoff"):
        return int(split_message[1])
    
def pay_donuts(user, amount):
    if (Parent.GetPoints(user) >= long(amount)):
        Parent.RemovePoints(user, long(amount))
        return True

    else:
        Parent.SendTwitchmessage("@" + user + " , you do not currently have enough donuts to pay the entry fee for the bakeoff.")
        return False

def start_bakeoff(user, amount):
    global bakeoff_start_time
    global bakeoff_entry_time
    global bakeoff_state

    if (bakeoff_state == 4):
        bakeoff_start_time = t.time() + bakeoff_entry_time
        bakeoff_state = 1
        Parent.SendTwitchMessage("Yeet! Steak is not a donut KEKW ! @" + user + " started a bakeoff by entering with " + str(amount) + " donuts.")

    else:
        Parent.SendTwitchMessage("After piling their entry fee of " + str(bakeoff_user_entry_amount) + " donuts on the table, " + user + " has entered the bake off competition!")