from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
import bs4
import time
import pandas as pd
import lxml
import numpy as np
from datetime import datetime
import math
from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive
from datetime import date
import os

gauth = GoogleAuth()           
drive = GoogleDrive(gauth) 





# loads existing data
month = date.today().month

# TEST VALUES - DELETE AFTER FINISHED
month = 5
month = str(month)



try:
    main_df = pd.read_csv('timingdata/' + month + '/monthly.csv',index_col=0, usecols=[0,1,2,3,4,5,6,7,8,9,10])
    # main_df = main_df.sort_values(by=['Best'], ignore_index=True, usecols=[0,1,2,3,4,5,6,7,8,9,10])
    fastlapdata = pd.read_csv('timingdata/alltime/fastlapdata.csv')
except:
    directory = str(month)
    path = 'timingdata/' + directory
    os.makedirs(path)
    main_df = pd.read_csv('blank.csv', index_col=0, usecols=[0,1,2,3,4,5,6,7,8,9,10])
    main_df.to_csv('timingdata/' + month + '/monthly.csv', index=True, header=True, columns=['Kart','Driver','Best','S1 Driver','Sector 1','S2 Driver','Sector 2','S3 Driver','Sector 3','Fantasy Lap'])



# filters out any non second values for best, s1,s2 and s3. 

colClean = ['Best', 'Sector 1', 'Sector 2', 'Sector 3']
for i in range(0,len(main_df)):
    for k in range(0,(len(colClean))):
        if(main_df.at[i, colClean[k]]=='-' ):
            main_df.at[i, colClean[k]]=float(999.999)
        else:
            badtimes = ['1:', '2:', '3:', '4:', '5:']
            test = str(main_df.at[i, colClean[k]])
            if (test.startswith(tuple(badtimes))):
                main_df.at[i, colClean[k]]=float(999.999)
            else:
                main_df.at[i, colClean[k]]=float(main_df.at[i, colClean[k]])



# initialised error count
errors = 0
uploadError = 0
uploadErrorHTML = 0

# initialised upload counter
uploadCount = 0
uploadCountHTML = 0

# initialised program running variables
run = 0
cycles = 2

x = 1
while (x < cycles):
    try:
        if (run == 0):
            # Headless chrome browser set up options
            options = Options()
            options.add_argument("start-maximized")
            options.add_experimental_option("detach", True)
            options.add_argument("--headless")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")

            # Headless chrome browser initialisation
            webdriver_service = Service('/Users/anthonyhartley/Downloads/chromedriver_mac_arm64/chromedriver')
            driver = webdriver.Chrome(options=options, service=webdriver_service)
            website = 'https://live.racefacer.com/hyperkarting'
            page=driver.get(website)
            html=driver.page_source
            run = 1

        print(str(x) + ' out of ' + str(cycles - 1))
        driver.refresh()
        time.sleep(5)
        html=driver.page_source
        df=pd.read_html(html)
        df = df[1]
        df.head()

            # Splits sectors into 3 columns
        if (len(df['S1 S2 S3']) > 0):
            df[['Sector 1', 'Sector 2', 'Sector 3']] = df['S1 S2 S3'].str.split(' ', expand = True) 

        # Removes unnecessary columns from table
        badCols = ['P', 'Unnamed: 8', 'Laps', 'Gap', 'Lap Time', 'Int', 'Unnamed: 9', 'S1 S2 S3']
        for i in range(0, len(badCols)):
            if (badCols[i] in df.columns):
                del df[badCols[i]]

        # Name newly created sector columns
        sectors = ['S1 Driver', 'S2 Driver', 'S3 Driver']
        for i in range(0, len(sectors)):
            df[sectors[i]] = df['Driver']

        # Create fantasy lap column for comparison purposes. Sort by best time 
        df['Fantasty Lap'] = df['Best']



        # Get session ID
        soup = bs4.BeautifulSoup(html, 'lxml')
        session_id = soup.find(class_='-skew-x-[40deg] truncate').get_text()
        print(session_id)
        session_check = session_id


        while (session_check == session_id):
            driver.refresh()
            session_df = pd.read_html(html)
            session_df = session_df[1]
            session_df.head()

            # Splits sectors into 3 columns
            if (len(session_df['S1 S2 S3']) > 0):
                session_df[['Sector 1', 'Sector 2', 'Sector 3']] = session_df['S1 S2 S3'].str.split(' ', expand = True) 

            for i in range(0, len(badCols)):
                if (badCols[i] in session_df.columns):
                    del session_df[badCols[i]]

            for i in range(0, len(sectors)):
                session_df[sectors[i]] = session_df['Driver']

            session_df['Fantasty Lap'] = session_df['Best']

            print('\n'); print('SESSION DATAFRAME'); print(session_df); print('\n')
            # edit this to check session id. move sleep time to this loop. after this loop exits, commit data to dataframe "df" then commit to kart files
            # as well as any other data, log a time for the fastlapdata file
            # make this loop update as the session goes on, overwriting slower values. i guess just keep best sectors of each even though it wont add up
            # to the best lap necessarily. 
            # i dont see the need to commit every lap but if you were it would check all 3 sectors have values before taking them all down together and doing the math?
            # or are you better off including last and just using that....perhaps, or atleast use it to determine what to keep. you could also use the lap count
            # to keep the lap count and assign growing values for each driver. to even out the playing field for those who dont race much......
            # full of good ideas but do your fucking math homework first :) and go to the gym now because you need to be on time!
            session_check = '10'

    
        


        print('\n')
        print('\n')
        print('df START')
        print(df)
        print('df FINISH')
        print('\n')
        print('\n')
    except:
        driver.quit()
        run = 0
        print('An error occured')
        errors = (errors + 1)
    

    try:
        for i in range(0,len(df)):
            if(df.at[i, 'Best']=='-' ):
                df.at[i, 'Best']=float(999.999)
            else:
                badtimes = ['1:', '2:', '3:', '4:', '5:']
                test = str(df.at[i, 'Best'])
                if (test.startswith(tuple(badtimes))):
                    df.at[i, 'Best']=float(999.999)
                else:
                    df.at[i, 'Best']=float(df.at[i, 'Best'])
                if float(df.at[i, 'Best'] < 35.8):
                    df.at[i, 'Best']=float(888.888)
        #sector 1 bad times fixer
        for i in range(0,len(df)):
            if(df.at[i, 'Sector 1']=='-' ):
                df.at[i, 'Sector 1']=float(99.999)
            else:
                badtimes = ['1:', '2:', '3:', '4:', '5:']
                test = str(df.at[i, 'Sector 1'])
                if (test.startswith(tuple(badtimes))):
                    df.at[i, 'Sector 1']=float(99.999)
                else:
                    df.at[i, 'Sector 1']=float(df.at[i, 'Sector 1'])        
        #sector 2 bad times fixer
        for i in range(0,len(df)):
            if(df.at[i, 'Sector 2']=='-' ):
                df.at[i, 'Sector 2']=float(99.999)
            else:
                badtimes = ['1:', '2:', '3:', '4:', '5:']
                test = str(df.at[i, 'Sector 2'])
                if (test.startswith(tuple(badtimes))):
                    df.at[i, 'Sector 2']=float(99.999)
                else:
                    df.at[i, 'Sector 2']=float(df.at[i, 'Sector 2'])     
        #sector 3 bad times fixer
        for i in range(0,len(df)):
            if(df.at[i, 'Sector 3']=='-' ):
                df.at[i, 'Sector 3']=float(99.999)
            else:
                badtimes = ['1:', '2:', '3:', '4:', '5:']
                test = str(df.at[i, 'Sector 3'])
                if (test.startswith(tuple(badtimes))):
                    df.at[i, 'Sector 3']=float(99.999)
                else:
                    df.at[i, 'Sector 3']=float(df.at[i, 'Sector 3'])      
    except:
        pass
  
    print(df)
    try:
        # Best times add in
        for i in range(0, (len(df['Kart']))):
                if df.at[i, 'Kart'] in main_df['Kart'].values:
                    for k in range(0,(len(main_df['Kart']))):
                        if (df.at[i, 'Kart'] == main_df.at[k, 'Kart']):
                            if (df.at[i, 'Best'] == main_df.at[k, 'Best']):
                                main_df.at[k, 'Best'] = main_df.at[k, 'Best']
                                break
                            elif df.at[i, 'Best'] < main_df.at[k, 'Best']:
                                main_df.at[k, 'Best'] = df.at[i, 'Best']
                                main_df.at[k, 'Driver'] = df.at[i, 'Driver']
                                break
                else:
                    main_df.loc[len(main_df)] = df.loc[i]
                    print('Kart ' + str(df.at[i, 'Kart']) + ' added successfully')
                    
        # sector 1 add in
        for i in range(0, (len(df['Kart']))):
                if df.at[i, 'Kart'] in main_df['Kart'].values:
                    for k in range(0,(len(main_df['Kart']))):
                        if (df.at[i, 'Kart'] == main_df.at[k, 'Kart']):
                            if (df.at[i, 'Sector 1'] == main_df.at[k, 'Sector 1']):
                                main_df.at[k, 'Sector 1'] = main_df.at[k, 'Sector 1']
                                break
                            elif df.at[i, 'Sector 1'] < main_df.at[k, 'Sector 1']:
                                main_df.at[k, 'Sector 1'] = df.at[i, 'Sector 1']
                                main_df.at[k, 'S1 Driver'] = df.at[i, 'S1 Driver']

        # sector 2 add in
        for i in range(0, (len(df['Kart']))):
                if df.at[i, 'Kart'] in main_df['Kart'].values:
                    for k in range(0,(len(main_df['Kart']))):
                        if (df.at[i, 'Kart'] == main_df.at[k, 'Kart']):
                            if (df.at[i, 'Sector 2'] == main_df.at[k, 'Sector 2']):
                                main_df.at[k, 'Sector 2'] = main_df.at[k, 'Sector 2']
                                break
                            elif df.at[i, 'Sector 2'] < main_df.at[k, 'Sector 2']:
                                main_df.at[k, 'Sector 2'] = df.at[i, 'Sector 2']
                                main_df.at[k, 'S2 Driver'] = df.at[i, 'S2 Driver']

        # sector 3 add in
        for i in range(0, (len(df['Kart']))):
                if df.at[i, 'Kart'] in main_df['Kart'].values:
                    for k in range(0,(len(main_df['Kart']))):
                        if (df.at[i, 'Kart'] == main_df.at[k, 'Kart']):
                            if (df.at[i, 'Sector 3'] == main_df.at[k, 'Sector 3']):
                                main_df.at[k, 'Sector 3'] = main_df.at[k, 'Sector 3']
                                break
                            elif df.at[i, 'Sector 3'] < main_df.at[k, 'Sector 3']:
                                main_df.at[k, 'Sector 3'] = df.at[i, 'Sector 3']
                                main_df.at[k, 'S3 Driver'] = df.at[i, 'S3 Driver']
    except:
        pass

    print('\n')
    print('\n')

    try:
        for i in range(0, len(main_df['Kart'])):
            y = round(float(main_df.at[i, 'Sector 1'] + main_df.at[i, 'Sector 2'] + main_df.at[i, 'Sector 3']), 3)
            if (y > 999.999):
                main_df.at[i, 'Fantasy Lap'] = 999.999
            if y < main_df.at[i, 'Best']:
                main_df.at[i, 'Fantasy Lap'] = y
            else: 
                main_df.at[i, 'Fantasy Lap'] = main_df.at[i, 'Best']
            
        for i in range(0, len(main_df['S1 Driver'])):
            if (len(main_df['S1 Driver'][i]) > 30):
                main_df['S1 Driver'][i] = ('%.30s' % main_df['Driver'][i])

        for i in range(0, len(main_df['S2 Driver'])):
            if (len(main_df['S2 Driver'][i]) > 30):
                main_df['S2 Driver'][i] = ('%.30s' % main_df['Driver'][i])

        for i in range(0, len(main_df['S3 Driver'])):
            if (len(main_df['S3 Driver'][i]) > 30):
                main_df['S3 Driver'][i] = ('%.30s' % main_df['Driver'][i])
    except: errors += 1
    
    main_df = main_df.sort_values(by=['Best'], ignore_index=True)

    pd.DataFrame(main_df).to_csv('kart2.txt', index=True, header=True, columns=['Kart','Driver','Best','S1 Driver','Sector 1','S2 Driver','Sector 2','S3 Driver','Sector 3','Fantasy Lap'])
    

                                
    print('\n')
    print(main_df)
    print('\n')
    print(x)
    x+=1
    print('errors: ' + str(errors))

    # if (x%12 == 0):
    #     try:
    #         main_df.to_html('karts.html',header=True, index=False, justify="left", border=0, table_id='timingdata')

    #         with open('index.html') as ind:
    #             txt = ind.read()
    #             soup = bs4.BeautifulSoup(txt, "lxml")
    #             table = soup.find(id ="timingdata")
    #             with open('karts.html') as tabl:
    #                 txt_tabl = tabl.read()
    #                 soup_tabl = bs4.BeautifulSoup(txt_tabl, 'lxml')
    #                 table.replace_with(soup_tabl)
    #         with open('index.html', 'w') as outf:
    #             outf.write(str(soup))
    #     except:
    #         pass

    # try:
    #     if (x%12 == 0):
    #         gfile = drive.CreateFile({'title': 'index.html', 'id': '1tzjTSmVT2N2vl1rx3e6FrhuE54LFiPSE', 'Parents': '15KMUtO4gWeRqT0d2OrwabT6ReoP45XzU'})
    #         gfile.SetContentFile('index.html')
    #         gfile.Upload() # Upload the file.
    #         uploadCountHTML += 1
    #         print('HTML Upload Success, Upload number: ' + str(uploadCountHTML))
    # except:
    #     uploadErrorHTML += 1
    #     print('HTML Upload Error: ' + str(uploadErrorHTML))
    # try:
    #     if (x%12 == 0):
    #         gfile = drive.CreateFile({'title': 'kart2.txt', 'id': '1kbL7rIrKBo-PGWY_uqY2flIu4dU0j-G7', 'Parents': '15KMUtO4gWeRqT0d2OrwabT6ReoP45XzU'})
    #         gfile.SetContentFile('kart2.txt')
    #         gfile.Upload() # Upload the file.
    #         uploadCount += 1
    #         print('Upload Success, Upload number: ' + str(uploadCount))
    # except:
    #     uploadError += 1
    #     print('Upload Error: ' + str(uploadError))
    
 


    today = date.today()
    print(today)
    today = str(today)
    pd.DataFrame(main_df).to_csv('timingdata/' + today + '.csv', index=True, header=True, columns=['Kart','Driver','Best','S1 Driver','Sector 1','S2 Driver','Sector 2','S3 Driver','Sector 3','Fantasy Lap'])



    try:
        best = main_df['Driver'].value_counts()
        s1 = main_df['S1 Driver'].value_counts()
        s2 = main_df['S2 Driver'].value_counts()
        s3 = main_df['S3 Driver'].value_counts()
        leaderboard = pd.concat([best, s1, s2, s3], axis=1).fillna(0)
        leaderboard.rename(columns= {'Driver' : 'Best'}, inplace=True)
        columns = ['Best','S1 Driver', 'S2 Driver', 'S3 Driver']
        for i in range(0, 4):
            (leaderboard[columns[i]]) = (leaderboard[columns[i]].astype(int))
        leaderboard['Total'] = 0
        for i in range(0, len(leaderboard['Total'])):
            leaderboard['Total'][i] = leaderboard['Best'][i] + leaderboard['S1 Driver'][i] + leaderboard['S2 Driver'][i] + leaderboard['S3 Driver'][i]
        leaderboard.drop(labels='Unused Kart', axis=0, inplace=True)
        leaderboard = leaderboard.sort_values(by=['Total'], ascending=False)
    except:
        pass

    print(leaderboard)
    print('\n')
    print('\n')
        

    time.sleep(15)
    


print(main_df)
driver.quit()
