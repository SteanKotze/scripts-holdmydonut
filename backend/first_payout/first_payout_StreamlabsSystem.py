#---------------------------------------
#   Import Libraries
#---------------------------------------
import os
import codecs
import json
import random as rand
import time as t

#---------------------------------------
#   [Required]  Script Information
#---------------------------------------
ScriptName = "!first script"
Website = "https://github.com/SteanKotze/scripts-holdmydonut.git"
Creator = "I_am_steak"
Version = "0.1"
Description = "This script rewards users when they use the !first command"

#---------------------------------------
#   Set Variables
#---------------------------------------
settings_path = "Services\\Scripts\\scripts-holdmydonut\\backend\\first_payout\\first_payout_json"
settings = None

#   Script related
first_user_payout = None
second_user_payout = None
third_user_payout = None

user_payout_flag = [False, False, False]
successful_user_payouts = []

#---------------------------------------
#   [Required] Intialize Data 
#---------------------------------------
def Init():
    #   Globals
    global settings_path
    global settings

    global first_user_payout
    global second_user_payout
    global third_user_payout

    with codecs.open(settings_path, encoding="utf-8-sig", mode="r") as settings_file:
        settings = json.load(settings_file, encoding="utf-8")

    if (settings != None):
        first_user_payout = int(settings['first_user_payout'])
        second_user_payout = int(settings['second_user_payout'])
        third_user_payout = int(settings['third_user_payout'])

    else:
        first_user_payout = 200
        second_user_payout = 100
        third_user_payout = 50

    return
    
#---------------------------------------
#   [Required] Execute Data / Process Messages
#---------------------------------------
def Execute(data):
    if (data.IsChatMessage() and data.IsFromTwitch()):
        first_payout(data.User, data.Message)

    return

def first_payout(user, message):
    global first_user_payout
    global second_user_payout
    global third_user_payout

    global user_payout_flag
    global successful_user_payouts

    try:
        if (message == "I am steak"):
            Parent.SendTwitchMessage("VoHiYo")
        
        elif (message in ['!first', '!second', 'third']):
            if (user not in successful_user_payouts):
                if (user_payout_flag[0] == False):
                    Parent.AddPoints(user, first_user_payout)
                    user_payout_flag[0] = True
                    successful_user_payouts.append(user)

                elif (user_payout_flag[1] == False):
                    Parent.AddPoints(user, second_user_payout)
                    user_payout_flag[1] = True
                    successful_user_payouts.append(user)

                elif (user_payout_flag[2] == False):
                    Parent.AddPoints(user, third_user_payout)
                    user_payout_flag[2] = True
                    successful_user_payouts.append(user)

                else:
                    print('yeet')
            else:
                print('yeet')

    except Exception as e:
        Parent.SendTwitchWhisper("i_am_steak", e.message)
        Parent.SendTwitchWhisper("i_am_not_steak", e.message)


#---------------------------------------
#   [Required] Tick Function
#---------------------------------------
def Tick(): #DONE
    return

