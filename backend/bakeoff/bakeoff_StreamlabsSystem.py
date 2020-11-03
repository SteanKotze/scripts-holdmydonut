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
ScriptName = "!bakeoff script"
Website = "https://github.com/SteanKotze/scripts-holdmydonut.git"
Creator = "I_am_steak"
Version = "0.1"
Description = "This script allows users to start a bake off"

#---------------------------------------
#   Set Variables
#---------------------------------------
settings_path = "Services\\Scripts\\scripts-donut\\backend\\bakeoff\\bakeoff_settings.json"
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

bakeoff_steal_amount = None                                                                                     # how many donuts a contestant can steal at any point in time
bakeoff_steal_chance = None                                                                                     # the chance of one contestant successfully stealing donuts
bakeoff_steal_count = None
bakeoff_steal_max_count = None
bakeoff_sabotage_amount = None                                                                                  # how many donuts a contestant can sabotage an any point in time
bakeoff_sabotage_chance = None                                                                                  # the chance of one contestant successfully sabotaging another contestant
bakeoff_sabotage_count = None
bakeoff_sabotage_max_count = None

bakeoff_anomoly_chance = None                                                                                   # the chance of an anomoly occuring during the bakeoff
bakeoff_anomoly_chance_breakdown = None                                                                         # the chance of a contestant having a breakdown, given anomoly occurence
bakeoff_anomoly_chance_flop = None                                                                              # the chance of a contestant's product flopping, give anomoly occurence
bakeoff_anomoly_chance_flop_lower_bound = None                                                                  # the lower bound for the payout reduction due to a flop
bakeoff_anomoly_chance_flop_upper_bound = None                                                                  # the upper bound for the payout reduction due to a flop
bakeoff_anomoly_chance_oven_fail = None                                                                         # the chance of an oven fail occuring, given anomoly occurence
bakeoff_anomoly_chance_oven_fail_lower_bound = None                                                             # the lower bound for the payout reduction due to an oven fail
bakeoff_anomoly_chance_oven_fail_upper_bound = None                                                             # the upper bound for the payout reduction due to an overn fail

bakeoff_first_place_multiplier = None                                                                           # 
bakeoff_second_place_multiplier = None
bakeoff_third_place_multiplier = None
bakeoff_general_multiplier = None

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

    global bakeoff_steal_amount
    global bakeoff_steal_chance
    global bakeoff_steal_max_count
    global bakeoff_sabotage_amount
    global bakeoff_sabotage_chance
    global bakeoff_sabotage_max_count

    global bakeoff_anomoly_chance
    global bakeoff_anomoly_chance_breakdown
    global bakeoff_anomoly_chance_flop
    global bakeoff_anomoly_chance_flop_lower_bound
    global bakeoff_anomoly_chance_flop_upper_bound
    global bakeoff_anomoly_chance_oven_fail
    global bakeoff_anomoly_chance_oven_fail_lower_bound
    global bakeoff_anomoly_chance_oven_fail_upper_bound

    global bakeoff_first_place_multiplier
    global bakeoff_second_place_multiplier
    global bakeoff_third_place_multiplier
    global bakeoff_general_multiplier

    #   init
    with codecs.open(settings_path, encoding="utf-8-sig", mode="r") as settings_file:
        settings = json.load(settings_file, encoding="utf-8")

    if (settings != None):
        bakeoff_entry_time = int(settings['bakeoff_entry_time'])
        bakeoff_cook_time = int(settings['bakeoff_cook_time'])
        bakeoff_cooldown_time = int(settings['bakeoff_cooldown_time'])

        bakeoff_steal_amount = int(settings['bakeoff_steal_amount'])
        bakeoff_steal_chance = int(settings['bakeoff_steal_chance'])
        bakeoff_steal_max_count = int(setting['bakeoff_steal_max_count'])
        bakeoff_sabotage_amount = int(settings['bakeoff_sabotage_amount'])
        bakeoff_sabotage_chance = int(settings['bakeoff_sabotage_chance'])
        bakeoff_sabotage_max_count = int(settings['bakeoff_sabotage_max_count'])
        
        bakeoff_anomoly_chance = int(settings['bakeoff_anomoly_chance'])
        bakeoff_anomoly_chance_breakdown = int(settings['bakeoff_anomoly_chance_breakdown'])
        bakeoff_anomoly_chance_flop = int(settings['bakeoff_anomoly_chance_flop'])
        bakeoff_anomoly_chance_flop_lower_bound = int(settings['bakeoff_anomoly_chance_flop_lower_bound'])
        bakeoff_anomoly_chance_flop_upper_bound = int(settings['bakeoff_anomoly_chance_flop_upper_bound'])
        bakeoff_anomoly_chance_oven_fail = int(settings['bakeoff_anomoly_chance_oven_fail'])
        bakeoff_anomoly_chance_oven_fail_lower_bound = int(settings['bakeoff_anomoly_chance_oven_fail_lower_bound'])
        bakeoff_anomoly_chance_oven_fail_upper_bound = int(settings['bakeoff_anomoly_chance_oven_fail_upper_bound'])

        bakeoff_first_place_multiplier = float(settings['bakeoff_first_place_multiplier'])
        bakeoff_second_place_multiplier = float(settings['bakeoff_second_place_multiplier'])
        bakeoff_third_place_multiplier = float(settings['bakeoff_third_place_multiplier'])
        bakeoff_general_multiplier = float(settings['bakeoff_general_multiplier'])

        tick_refresh_rate = int(settings['tick_refresh_rate'])
    
    else:
        bakeoff_entry_time = 10
        bakeoff_cook_time = 10
        bakeoff_cooldown_time = 15

        bakeoff_steal_amount = 20
        bakeoff_steal_chance = 35
        bakeoff_sabotage_amount = 10
        bakeoff_sabotage_chance = 70

        bakeoff_anomoly_chance = 5
        bakeoff_anomoly_chance_breakdown = 10
        bakeoff_anomoly_chance_flop = 60
        bakeoff_anomoly_chance_flop_lower_bound = 40
        bakeoff_anomoly_chance_flop_upper_bound = 60
        bakeoff_anomoly_chance_oven_fail = 30
        bakeoff_anomoly_chance_oven_fail_lower_bound = 20
        bakeoff_anomoly_chance_oven_fail_upper_bound = 40

        bakeoff_first_place_multiplier = 4.0
        bakeoff_second_place_multiplier = 3.0
        bakeoff_third_place_multiplier = 2.0
        bakeoff_general_multiplier = 1.25

        tick_refresh_rate = 5

    ##  Non-settable variables

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

    global bakeoff_steal_amount
    global bakeoff_steal_chance

    global bakeoff_sabotage_amount
    global bakeoff_sabotage_chance

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

        elif (( message.find("!steal") == 0 ) and ( user in bakeoff_users ) and ( bakeoff_state == 2 )):
            other_user = extract_user(message)
            if (other_user in bakeoff_users):
                if ( rand.randint(0, 100) <= bakeoff_steal_chance ):
                    user_index = bakeoff_users.index(user)
                    other_user_index = bakeoff_users.index(other_user)
                    other_user_donuts = bakeoff_users_entry_fees[other_user_index]

                    if ( other_user_donuts > bakeoff_steal_amount ):
                        bakeoff_users_entry_fees[user_index] += bakeoff_steal_amount
                        bakeoff_users_entry_fees[other_user_index] -= bakeoff_steal_amount

                    else:
                        bakeoff_users_entry_fees[user_index] += bakeoff_users_entry_fees[other_user_index]
                        bakeoff_users_entry_fees[other_user_index] = 0

                    Parent.SendTwitchmessage("Only thinking about themself, @" + user + " has stolen some of @" + other_user + " 's flour, eggs, butter, and icing sugar.") # ToDo

        elif (( message.find("!sabotage") == 0 ) and ( user in bakeoff_users ) and ( bakeoff_state == 2 )):
            other_user = extract_user(message)
            if (other_user in bakeoff_users):
                if( rand.randint(0, 100) <= bakeoff_sabotage_amount ):
                    other_user_index = bakeoff_users.index(other_user)
                    other_user_donuts = bakeoff_users_entry_fees[other_user_index]

                    if ( other_user_donuts > bakeoff_sabotage_amount ):
                        bakeoff_users_entry_fees[other_user_index] -= bakeoff_sabotage_amount

                    else:
                        bakeoff_users_entry_fees[other_user_index] = 0
                   
                    Parent.SendTwitchmessage("Attempting to get ahead, @" + user + " has replaced the water in @" + other_user + " 's jug with white vinegar!") # ToDo

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

    global bakeoff_anomoly_chance
    global bakeoff_anomoly_chance_breakdown
    global bakeoff_anomoly_chance_flop
    global bakeoff_anomoly_chance_flop_lower_bound
    global bakeoff_anomoly_chance_flop_upper_bound
    global bakeoff_anomoly_chance_oven_fail
    global bakeoff_anomoly_chance_oven_fail_lower_bound
    global bakeoff_anomoly_chance_oven_fail_upper_bound

    global bakeoff_first_place_multiplier
    global bakeoff_second_place_multiplier
    global bakeoff_third_place_multiplier
    global bakeoff_general_multiplier

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
        
        bakeoff_users_placings = []
        bakeoff_users_payout = []
        number_of_contestants = len(bakeoff_users)

        for _ in range(0, number_of_contestants):
            random_user_index = rand.randint(0, len(bakeoff_users) - 1)

            if (bakeoff_users_entry_fees[random_user_index] > 0):
                bakeoff_users_placings.append(bakeoff_users[random_user_index])
                bakeoff_users_payout.append(bakeoff_users_entry_fees[random_user_index])

            del bakeoff_users[random_user_index]
            del bakeoff_users_entry_fees[random_user_index]

        number_of_contestants = len(bakeoff_users_placings)
        payout_podium_message = "The bakeoff has finished with the following podium placings: "
        payout_general_message = "The following users finished the bakeoff without placing: "

        for i in range(0, number_of_contestants):
            if (i == 0):
                bakeoff_users_payout[i] *= bakeoff_first_place_multiplier
                payout_podium_message = payout_podium_message + "1st. " + bakeoff_users_placings[i] + " (" + str(bakeoff_users_payout[i]) + "), "

            elif (i == 1):
                bakeoff_users_payout[i] *= bakeoff_second_place_multiplier
                payout_podium_message = payout_podium_message + "2st. " + bakeoff_users_placings[i] + " (" + str(bakeoff_users_payout[i]) + "), "

            elif (i == 2): 
                bakeoff_users_payout[i] *= bakeoff_third_place_multiplier
                payout_podium_message = payout_podium_message + "3rd. " + bakeoff_users_placings[i] + " (" + str(bakeoff_users_payout[i]) + ")"

            else:
                bakeoff_users_payout[i] *= bakeoff_general_multiplier
                payout_general_message = payout_general_message + bakeoff_users_placings[i] + " (" + str(bakeoff_users_payout[i]) + ")"

                if (i != number_of_contestants -1):
                    payout_general_message = payout_general_message + ", "

            Parent.AddPoints(bakeoff_users_placings[i], bakeoff_users_payout[i])


    elif (( bakeoff_state == 3) and (bakeoff_initialisation_time <= current_time)):
        bakeoff_state = 4
        
        Parent.SendTwitchMessage("You can now start a new bakeoff!")

    elif ( bakeoff_state == 2 ):
        if ( rand.randint(0, 100) <= bakeoff_anomoly_chance ):
            anomoly_index = rand.randint(0, 100)
            user_index = rand.randint(0, len(bakeoff_users) - 1)
            user = bakeoff_users[user_index]

            if ( anomoly_index <= bakeoff_anomoly_chance_breakdown ):
                bakeoff_users_entry_fees[user_index] = 0
                Parent.SendTwitchMessage("@" + user + " couldn't take the pressure anymore and quit the competition! They were last heard shouting: 'Not the gumdrop buttons'")

            elif ( anomoly_index <= ( bakeoff_anomoly_chance_breakdown + bakeoff_anomoly_chance_flop ) ):
                flop_percentage_amount = rand.randint(bakeoff_anomoly_chance_flop_lower_bound, bakeoff_anomoly_chance_flop_upper_bound)
                flop_actual_amount = int( bakeoff_users_entry_fees[user_index] * float(100) / flop_percentage_amount )
                bakeoff_users_entry_fees[user_index] -= flop_actual_amount
                Parent.SendTwitchMessage("Despite their best efforts, sweat, blood, tears, and many sacrifices to the sugar Gods, @" + user + " pulled out a tray of slimey, eggy cookies with still frozen choc chips. Is there time to steal some of $users cookies before the judges are called?")

            else:
                flop_percentage_amount = rand.randint(bakeoff_anomoly_chance_oven_fail_lower_bound, bakeoff_anomoly_chance_oven_fail_upper_bound)
                flop_actual_amount = int( bakeoff_users_entry_fees[user_index] * float(100) / flop_percentage_amount )
                bakeoff_users_entry_fees[user_index] -= flop_actual_amount
                Parent.SendTwitchmessage("In a particularly extravagant show of flair and pizazz, @" + user + " expertly put their cake in the oven and spun round in a twirl to throw off the other bakers, but did they remember to turn the oven on?")

#---------------------------------------
#   backend
#---------------------------------------
def extract_donuts(message):
    split_message = message.split(' ')
    if (split_message[0] == "!bakeoff"):
        return int(split_message[1])

def extract_user(message):
    split_message = message.split(' ')
    if (len(split_message) > 1):
        return split_message[1]
    
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
        Parent.SendTwitchMessage("Get ready to bake! @" + user + " has started a bake off competition. To enter type !bakeoff and the number of donuts you are using as your entry fee. Good luck bakers!")

    else:
        Parent.SendTwitchMessage("After piling their entry fee of " + str(amount) + " donuts on the table, " + user + " has entered the bake off competition!")