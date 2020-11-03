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

users = []
users_entry_fees = []

state = None                                                                                            # 1=entry, 2=bakeoff, 3=cooldown, 4=idle

initialisation_time = None                                                                              # the first point in time when the next bakeoff can start
entry_time = None                                                                                       # how long users can join the next bakeoff
start_time = None                                                                                       # the time when the next bakeoff starts
cook_time = None                                                                                        # the amount of time a user has to complete a bakeoff
end_time = None                                                                                         # the time that the current bakeoff ends
cooldown_time = None                                                                                    # how long after the previous bakeoff before the next bakeoff can start

steal_amount = None                                                                                     # how many donuts a contestant can steal at any point in time
steal_chance = None                                                                                     # the chance of one contestant successfully stealing donuts
steal_count = None
steal_max_count = None
sabotage_amount = None                                                                                  # how many donuts a contestant can sabotage an any point in time
sabotage_chance = None                                                                                  # the chance of one contestant successfully sabotaging another contestant
sabotage_count = None
sabotage_max_count = None

anomoly_chance = None                                                                                   # the chance of an anomoly occuring during the bakeoff
anomoly_chance_breakdown = None                                                                         # the chance of a contestant having a breakdown, given anomoly occurence
anomoly_chance_flop = None                                                                              # the chance of a contestant's product flopping, give anomoly occurence
anomoly_chance_flop_lower_bound = None                                                                  # the lower bound for the payout reduction due to a flop
anomoly_chance_flop_upper_bound = None                                                                  # the upper bound for the payout reduction due to a flop
anomoly_chance_oven_fail = None                                                                         # the chance of an oven fail occuring, given anomoly occurence
anomoly_chance_oven_fail_lower_bound = None                                                             # the lower bound for the payout reduction due to an oven fail
anomoly_chance_oven_fail_upper_bound = None                                                             # the upper bound for the payout reduction due to an overn fail

first_place_multiplier = None                                                                           # 
second_place_multiplier = None
third_place_multiplier = None
general_multiplier = None

#---------------------------------------
#   [Required] Intialize Data 
#---------------------------------------
def Init():
    #   globals
    global tick_refresh_rate
    global last_tick

    global settings_path
    global settings

    global state
    global cooldown_time
    global initialisation_time
    global entry_time
    global start_time
    global cook_time
    global end_time

    global steal_amount
    global steal_chance
    global steal_count
    global steal_max_count
    global sabotage_amount
    global sabotage_chance
    global sabotage_count
    global sabotage_max_count

    global anomoly_chance
    global anomoly_chance_breakdown
    global anomoly_chance_flop
    global anomoly_chance_flop_lower_bound
    global anomoly_chance_flop_upper_bound
    global anomoly_chance_oven_fail
    global anomoly_chance_oven_fail_lower_bound
    global anomoly_chance_oven_fail_upper_bound

    global first_place_multiplier
    global second_place_multiplier
    global third_place_multiplier
    global general_multiplier

    #   init
    with codecs.open(settings_path, encoding="utf-8-sig", mode="r") as settings_file:
        settings = json.load(settings_file, encoding="utf-8")

    if (settings != None):
        entry_time = int(settings['entry_time'])
        cook_time = int(settings['cook_time'])
        cooldown_time = int(settings['cooldown_time'])

        steal_amount = int(settings['steal_amount'])
        steal_chance = int(settings['steal_chance'])
        steal_max_count = int(settings['steal_max_count'])
        sabotage_amount = int(settings['sabotage_amount'])
        sabotage_chance = int(settings['sabotage_chance'])
        sabotage_max_count = int(settings['sabotage_max_count'])
        
        anomoly_chance = int(settings['anomoly_chance'])
        anomoly_chance_breakdown = int(settings['anomoly_chance_breakdown'])
        anomoly_chance_flop = int(settings['anomoly_chance_flop'])
        anomoly_chance_flop_lower_bound = int(settings['anomoly_chance_flop_lower_bound'])
        anomoly_chance_flop_upper_bound = int(settings['anomoly_chance_flop_upper_bound'])
        anomoly_chance_oven_fail = int(settings['anomoly_chance_oven_fail'])
        anomoly_chance_oven_fail_lower_bound = int(settings['anomoly_chance_oven_fail_lower_bound'])
        anomoly_chance_oven_fail_upper_bound = int(settings['anomoly_chance_oven_fail_upper_bound'])

        first_place_multiplier = float(settings['first_place_multiplier'])
        second_place_multiplier = float(settings['second_place_multiplier'])
        third_place_multiplier = float(settings['third_place_multiplier'])
        general_multiplier = float(settings['general_multiplier'])

        tick_refresh_rate = int(settings['tick_refresh_rate'])
    
    else:
        entry_time = 10
        cook_time = 10
        cooldown_time = 15

        steal_amount = 20
        steal_chance = 35
        sabotage_amount = 10
        sabotage_chance = 70

        anomoly_chance = 5
        anomoly_chance_breakdown = 10
        anomoly_chance_flop = 60
        anomoly_chance_flop_lower_bound = 40
        anomoly_chance_flop_upper_bound = 60
        anomoly_chance_oven_fail = 30
        anomoly_chance_oven_fail_lower_bound = 20
        anomoly_chance_oven_fail_upper_bound = 40

        first_place_multiplier = 4.0
        second_place_multiplier = 3.0
        third_place_multiplier = 2.0
        general_multiplier = 1.25

        tick_refresh_rate = 5

    ##  Non-settable variables

    last_tick = t.time()
    state = 4
    initialisation_time = t.time()
    rand.seed(t.time())

    steal_count = 0
    sabotage_count = 0

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
    global users
    global users_entry_fees

    global state
    global initialisation_time

    global steal_amount
    global steal_chance
    global steal_count
    global steal_max_count
    global sabotage_amount
    global sabotage_chance
    global sabotage_count
    global sabotage_max_count

    #   functionality
    if ((message.find("!bakeoff") == 0) and (user not in users)):
        if ((t.time() >= initialisation_time) and (state == 1 or state == 4)):
            user_entry_amount = extract_donuts(message)
            if (pay_donuts(user, user_entry_amount)):
                users.append(user)
                users_entry_fees.append(user_entry_amount)
                start_bakeoff(user, user_entry_amount)
        
        else:
            Parent.SendTwitchMessage("@" + user + " , you will be able to enter a new bakeoff in ") # ToDo

    elif (( message.find("!steal") == 0 ) and ( user in users ) and ( state == 2 ) and ( steal_count < steal_max_count )):
        steal_count += 1
        other_user = extract_user(message)
        if (other_user in users):
            if ( rand.randint(0, 100) <= steal_chance ):
                user_index = users.index(user)
                other_user_index = users.index(other_user)
                other_user_donuts = users_entry_fees[other_user_index]

                if ( other_user_donuts > steal_amount ):
                    users_entry_fees[user_index] += steal_amount
                    users_entry_fees[other_user_index] -= steal_amount

                else:
                    users_entry_fees[user_index] += users_entry_fees[other_user_index]
                    users_entry_fees[other_user_index] = 0

                Parent.SendTwitchMessage("Only thinking about themself, @" + user + " has stolen some of @" + other_user + " 's flour, eggs, butter, and icing sugar.") # ToDo
            
            else:
                Parent.SendTwitchMessage("@" + user + " no PunOko")

    elif (( message.find("!sabotage") == 0 ) and ( user in users ) and ( state == 2 ) and ( sabotage_count < sabotage_max_count)):
        sabotage_count += 1
        other_user = extract_user(message)
        if (other_user in users):
            if( rand.randint(0, 100) <= sabotage_chance ):
                other_user_index = users.index(other_user)
                other_user_donuts = users_entry_fees[other_user_index]

                if ( other_user_donuts > sabotage_amount ):
                    users_entry_fees[other_user_index] -= sabotage_amount

                else:
                    users_entry_fees[other_user_index] = 0
                
                Parent.SendTwitchmessage("Attempting to get ahead, @" + user + " has replaced the water in @" + other_user + " 's jug with white vinegar!") # ToDo
            
            else:
                Parent.SendTwitchMessage("@" + user + " no PunOko")

def bakeoff_tick():
    #   globals
    global users
    global users_entry_fees

    global cooldown_time
    global initialisation_time
    global state
    global start_time
    global cook_time
    global end_time

    global steal_count
    global sabotage_count

    global anomoly_chance
    global anomoly_chance_breakdown
    global anomoly_chance_flop
    global anomoly_chance_flop_lower_bound
    global anomoly_chance_flop_upper_bound
    global anomoly_chance_oven_fail
    global anomoly_chance_oven_fail_lower_bound
    global anomoly_chance_oven_fail_upper_bound

    global first_place_multiplier
    global second_place_multiplier
    global third_place_multiplier
    global general_multiplier

    #   variables
    current_time = t.time()

    #   functionality
    if (( state == 1 ) and ( start_time <= current_time )):
        end_time = current_time + cook_time
        state = 2

        Parent.SendTwitchMessage("Ready. Set. Bake! Our bakers have 5 minutes to complete their creations for the judges!")

    elif (( state == 2) and ( end_time <= current_time )):
        initialisation_time = current_time + cooldown_time
        state = 3

        steal_count = 0
        sabotage_count = 0
        
        users_placings = []
        users_payout = []
        number_of_contestants = len(users)

        for _ in range(0, number_of_contestants):
            random_user_index = rand.randint(0, len(users))

            if (users_entry_fees[random_user_index] > 0):
                users_placings.append(users[random_user_index])
                users_payout.append(users_entry_fees[random_user_index])

            del users[random_user_index]
            del users_entry_fees[random_user_index]

        number_of_contestants = len(users_placings)
        payout_podium_message = "The bakeoff has finished with the following podium placings: "
        payout_general_message = "The following users finished the bakeoff without placing: "

        for i in range(0, number_of_contestants):
            if (i == 0):
                users_payout[i] *= first_place_multiplier
                payout_podium_message = payout_podium_message + "1st. " + users_placings[i] + " (" + str(users_payout[i]) + "), "

            elif (i == 1):
                users_payout[i] *= second_place_multiplier
                payout_podium_message = payout_podium_message + "2st. " + users_placings[i] + " (" + str(users_payout[i]) + "), "

            elif (i == 2): 
                users_payout[i] *= third_place_multiplier
                payout_podium_message = payout_podium_message + "3rd. " + users_placings[i] + " (" + str(users_payout[i]) + ")"

            else:
                users_payout[i] *= general_multiplier
                payout_general_message = payout_general_message + users_placings[i] + " (" + str(users_payout[i]) + ")"

                if (i != number_of_contestants -1):
                    payout_general_message = payout_general_message + ", "

            Parent.AddPoints(users_placings[i], users_payout[i])


    elif (( state == 3) and (initialisation_time <= current_time)):
        state = 4
        
        Parent.SendTwitchMessage("You can now start a new bakeoff!")

    elif ( state == 2 ):
        if ( rand.randint(0, 100) <= anomoly_chance ):
            anomoly_index = rand.randint(0, 100)
            user_index = rand.randint(0, len(users))
            user = users[user_index]

            if ( anomoly_index <= anomoly_chance_breakdown ):
                users_entry_fees[user_index] = 0
                Parent.SendTwitchMessage("@" + user + " couldn't take the pressure anymore and quit the competition! They were last heard shouting: 'Not the gumdrop buttons'")

            elif ( anomoly_index <= ( anomoly_chance_breakdown + anomoly_chance_flop ) ):
                flop_percentage_amount = rand.randint(anomoly_chance_flop_lower_bound, anomoly_chance_flop_upper_bound)
                flop_actual_amount = int( users_entry_fees[user_index] * float(100) / flop_percentage_amount )
                users_entry_fees[user_index] -= flop_actual_amount
                Parent.SendTwitchMessage("Despite their best efforts, sweat, blood, tears, and many sacrifices to the sugar Gods, @" + user + " pulled out a tray of slimey, eggy cookies with still frozen choc chips. Is there time to steal some of the other competitors' cookies before the judges are called?")

            else:
                flop_percentage_amount = rand.randint(anomoly_chance_oven_fail_lower_bound, anomoly_chance_oven_fail_upper_bound)
                flop_actual_amount = int( users_entry_fees[user_index] * float(100) / flop_percentage_amount )
                users_entry_fees[user_index] -= flop_actual_amount
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
        Parent.SendTwitchMessage("@" + user + " , you do not currently have enough donuts to pay the entry fee for the bakeoff.")
        return False

def start_bakeoff(user, amount):
    global start_time
    global entry_time
    global state

    if (state == 4):
        start_time = t.time() + entry_time
        state = 1
        Parent.SendTwitchMessage("Get ready to bake! @" + user + " has started a bake off competition. To enter type !bakeoff and the number of donuts you are using as your entry fee. Good luck bakers!")

    else:
        Parent.SendTwitchMessage("After piling their entry fee of " + str(amount) + " donuts on the table, " + user + " has entered the bake off competition!")