import requests
import json
import pandas as pd
import time
from datetime import datetime
from datetime import date
import numpy as np
import math
import os
import string


# URL for the live data
url = "https://live.racefacer.com/ajax/live-data?slug=hyperkarting"

# Establish session timing dataframe
session_timing = pd.DataFrame(columns =['Kart', 'Driver', 'Best Lap', 'S1', 'S1 Driver', 'S2', 'S2 Driver', 'S3', 'S3 Driver', 'Laps', 'Theoretical Best', 'Time'])

# Establish tuple for laps over a minute
slow_laps = ['1:', '2:', '3:', '4:', '5:', '6:', '7:', '8:', '9:', '10:', "11:", "12:", '13:', '14:', '15:']

# Establish values for data table.
values = ['Driver', 'S1 Driver', 'S2 Driver', 'S3 Driver', 'Laps', 'Best Lap', 'S1', 'S2', 'S3']

# Establish JSON equivalent names for above values
jsonvalues = ['name', 'name', 'name', 'name', 'total_laps', 'best_time', 's1', 's2', 's3']

# Establish months
months = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']

# Initialise program, determine cycle count and whether data is test data or live data
cycles = int(input('how many cycles? '))

test_mode = input('Test mode? y/n ')
if (test_mode =='n'):
    test_mode = 0
if (test_mode == 'y'):
    test_mode = 1

# Function to remove bad time values
def timecheck(a):
    if (a == '-'):
        a = float(99.999)
    if str(a).startswith(tuple(slow_laps)):
        a = float(99.999)
    if (math.isnan(float(a))):
        a = float(99.999)

    return float(a)

def compare(a, b):
    a = timecheck(a)
    b = timecheck(b)
    if(a > float(b)):
        a = b
    return a

def compare_str(a,b):
    if (b == a):
        return a
    else:
        return b

def checkkart(kart, tim_data):
    for i in range(len(tim_data)):
        if kart in tim_data:
            return tim_data[0]

def fastest_theoretical(a,b,c):
    a = timecheck(a)
    b = timecheck(b)
    c = timecheck(c)
    if (a < b):
        if (a < c):
            return a
        else:
            return c
    if (b < c):
        return b
    else:
        return c
    
def add_time(a):
    time_of_session = datetime.now().strftime('%H:%M:%S')
    for i in range(len(a)):
         print(a['Time'][i])
         a['Time'][i] = time_of_session
    return a

def session_finished(a,b):
    today = date.today()
    month = today.month
    b = str(b).replace('#', '').replace(' ', '-')
    print('this should be fucking saving!!!!')
    print(a)
    if (1 == 1):
        try:
            pd.DataFrame(a).to_csv('timingdata/' + str(month) + '/' + str(today) + b + '.csv', index=True, header=True, columns=['Kart', 'Driver', 'Best Lap', 'S1', 'S1 Driver', 'S2', 'S2 Driver', 'S3', 'S3 Driver', 'Laps', 'Theoretical Best', 'Time'])
        except:
            directory = str(month)
            path = 'timingdata/' + directory
            os.makedirs(path)
            pd.DataFrame(a).to_csv('timingdata/' + str(month) + '/' + str(today) + b + '.csv', index=True, header=True, columns=['Kart', 'Driver', 'Best Lap', 'S1', 'S1 Driver', 'S2', 'S2 Driver', 'S3', 'S3 Driver', 'Laps', 'Theoretical Best', 'Time'])
    c = pd.DataFrame(columns =['Kart', 'Driver', 'Best Lap', 'S1', 'S1 Driver', 'S2', 'S2 Driver', 'S3', 'S3 Driver', 'Laps', 'Theoretical Best', 'Time'])
    return c

def refreshjson():
    response = requests.get(url)
    data = json.loads(response.text) 
    return data
    # if it is a new session, start the process that compares data to the main data
    # THIS IS ALL TODO :)
    # could probably shrink down the theoretical time section too if you really think about it.
    #  when you write the function to update the monthly timing, make sure you write it to update the driver name.

def reset_time(a,b):
    if (b == 0):
        a = datetime.now().strftime('%H.%M')
    if (b == 1):
        a = datetime.now().strftime('%H:%M:%S')
    return a




# Get the initial data
if (test_mode == 0):
    response = requests.get(url)
    data = json.loads(response.text)
if (test_mode == 1):
    with open('jsontestdata.json', 'r') as j:
        data = json.loads(j.read())  

# Establish time of session
session_start_time = datetime.now().strftime('%H:%M:%S')
time_of_session = datetime.now().strftime('%H.%M')


x = 0

while x < cycles:

 

    try:
        print('Time left: ' + data['data']['time_left'])
        session_id = data['data']['event_name']
        print(session_id)
        # print(session_timing)
        session = data['data']['runs']
        spare_session_id = session_id
    except:
        pass
    
    



    try:
        if session_id == data['data']['event_name']:
            for i in range(0, len(data["data"]['runs'])):
                if (data['data']['time_left_in_seconds'] > 780 and session[i]['laps'] > 3):
                    break
                if session[i]['kart'] in session_timing['Kart'].values:
                    for j in range(len(session_timing['Kart'])):
                        if session[i]['kart'] == session_timing.at[j, 'Kart']:
                            for k in range(len(jsonvalues)):
                                if (k < 5):
                                    session_timing.at[j, values[k]] = compare_str(session_timing.at[j, values[k]],session[i][jsonvalues[k]])
                                else:
                                    session_timing.at[j, values[k]] = compare(session_timing.at[j, values[k]], session[i][jsonvalues[k]])
                                    # Combines sector a, compare to existing a and replace
                            combined_sectors = timecheck(session_timing['S1'][j]) + timecheck(session_timing['S2'][j]) + timecheck(session_timing['S3'][j])
                            session_timing.at[j, 'Theoretical Best'] = fastest_theoretical(session_timing.at[j, 'Theoretical Best'], combined_sectors, session_timing.at[j, 'Best Lap'])               
                else:
                    new_kart = pd.DataFrame(columns =['Kart', 'Driver', 'Best Lap', 'S1', 'S1 Driver', 'S2', 'S2 Driver', 'S3', 'S3 Driver', 'Laps', 'Theoretical Best', 'Time'])
                    new_kart.at[0, 'Kart'] = session[i]['kart']
                    for k in range(len(jsonvalues)):
                        if (k < 5):
                            new_kart.at[0, values[k]] = session[i][jsonvalues[k]]
                        else:
                            new_kart.at[0, values[k]] = timecheck(session[i][jsonvalues[k]])
                                # Combines sector a, compare to existing a and replace
                    combined_sectors = new_kart['S1'][0] + new_kart['S2'][0] + new_kart['S3'][0]
                    new_kart.at[0, 'Theoretical Best'] = fastest_theoretical(new_kart.at[0, 'Theoretical Best'], combined_sectors, new_kart.at[0, 'Best Lap'])
                    new_kart.at[0, 'Time'] = session_start_time
                    session_timing = pd.concat([session_timing, new_kart], ignore_index=True)
    except:
        pass

    session_timing.sort_values(by=['Best Lap'], ignore_index=True, inplace=True)
    print(session_timing),print('')
    time.sleep(10)
    if (test_mode == 0):
        data = refreshjson()
    if (test_mode == 1):
        with open('jsontestdata.json', 'r') as j:
            data = json.loads(j.read())   


    time_elapsed = float(time_of_session) - float(datetime.now().strftime('%H.%M'))
    print('Time Elapsed: ', str(time_elapsed))
    



    try:
        if (data['data']['event_name'] != session_id or time_elapsed < -0.6):
            while (len(session_timing != 0)):
                session_timing = add_time(session_timing)
                session_timing = session_finished(session_timing, session_id)
                print(session_timing)
                print('this is the length of the dataframe: ', len(session_timing))
    except KeyError:
        while (len(session_timing != 0)):
            session_timing = add_time(session_timing)
            session_timing = session_finished(session_timing, session_id)
            time_of_session = reset_time(time_of_session,0)
            session_start_time = reset_time(time_of_session, 1)
            print(session_timing)
            print('this is the length of the dataframe: ', len(session_timing))
        

    x += 1
    print(''),print(x,' out of ', str(cycles))
    

    

