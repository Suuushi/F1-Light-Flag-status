
import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import time
import sys
import logging
from datetime import datetime
from time import sleep
from threading import Thread
from threading import Event


# Scraper
chrome_driver_path = 'H:\\Chromedriver'
chrome_options = Options()
chrome_options.add_argument('--headless')

webdriver = webdriver.Chrome(
    executable_path=chrome_driver_path, options=chrome_options
)

url = "https://f1.tfeed.net/live"

webdriver.get(url)
time.sleep(8)                  # Delay to connect to Website

finished = Event()

# Logging
fname = datetime.now().strftime("%Y_%m_%d-%I_%M_%S_%p")

logging.basicConfig(filename=fname, format='%(message)s ',
                    level=logging.INFO, filemode='w')
# %(asctime)s

# variables request / print
sessionstarted = webdriver.execute_script('return sessionStarted')
sessionfinished = webdriver.execute_script('return sessionFinished')
sessiontype = webdriver.execute_script('return sessionType')
sessionleftlaps = webdriver.execute_script('return sessionLeftLaps')
sessionremaining = webdriver.execute_script('return sessioninfo.remaining')
year_calendar = webdriver.execute_script('return calendar')
next_finished = webdriver.execute_script('return calendarNextEvent')
next_finished_timestamp = (webdriver.execute_script('return calendarNextEventTimestamp'))/1000


# var
global request_rate  # REQUEST RATE
request_rate = 8
global timeoffset   # TIME OFFSET of LEDs with Livestream
timeoffset = 10
endtime = 5         # TIME AFTER CHECKERED FLAG
global flag_status
flag_status = 0     # White Flag (standby)
current_timestamp = round(time.time())
request_beginn_delay = 300  # in s


# main functions

def flag_check():       # Flag
    while not finished.is_set():
        Flag = webdriver.execute_script('return sessionFlag')
        print('Flag: ' + str(Flag))
        logging.info(Flag)
        # logging.info('Flag: ' + str(Flag))
        time.sleep(request_rate)
    sys.exit()


def file_reader():      # Set flag_status delayed by timeoffset
    while not finished.is_set():
        count = 0
        time.sleep(timeoffset)
        log_file = open(fname, 'r')
        Lines = log_file.readlines()
        while not finished.is_set():
            time.sleep(request_rate)
            if count == 0:
                print('Count is 0')
                count += 1
            else:
                for line in Lines:
                    # print("Line{}: {}".format(count, line.strip()))
                    # print(str(line), end = '')
                    print('Reading:' + line.rstrip())
                    flag_status = line.rstrip()
                    count += 1


def flag_led():         # Control LEDs
    while not finished.is_set():
        print('LEDS')
        time.sleep(15)
        # LED STANDBY
        # flag_status

        # if FLG == 1:
        # LED GREEN - constant
        # elif FLG == 2:
        # LED Yellow - const
        # elif FLG == 3 or Flag == 4:
        # LED Yellow - Flashing
        # elif FLG == 5:
        # LED RED - const
        # elif FLG ==7:
        # LED Yellow - Fade - blinking
        # elif flag_status == -1 or flag_status == 0:
        # LED WHITE
                # OSWIN SAGT ARRAY PROBIEREN

    # else:
        # time.sleep(endtime)
        # finished.set()
        # webdriver.close()
        # sys.exit()


def standby():          # Standby
    while not finished.is_set():
        current_timestamp = round(time.time())
        next_finished_timestamp = (webdriver.execute_script(
            'return calendarNextEventTimestamp'))/1000
        #Flag = webdriver.execute_script('return sessionFlag')
        
                
        if (next_finished_timestamp-request_beginn_delay) <= current_timestamp: # Checking if Time = next finished - 5 min
                                                                                
            Thread(target=flag_check).start()
            Thread(target=file_reader).start()
            print('Main Threads started')

            while not finished.is_set():                     # Get Sessiondata
                sessiontype = webdriver.execute_script('return sessionType')
                sessionleftlaps = webdriver.execute_script(
                    'return sessionLeftLaps')
                sessionremaining = webdriver.execute_script(
                    'return sessioninfo.remaining')

                # END Clauses

                if sessiontype == 1:                         # Sessiontype == RACE
                    if sessionleftlaps == 0:                 # Race Finished
                        print('Race finished')
                        logging.info('Race finished ')
                        # LED FLG CHECKERED
                        time.sleep(endtime)
                        finished.set()
                        webdriver.close()
                        sys.exit()
                        # back to white RGB
                # else:

                elif sessiontype == 2 or sessiontype == 3 or sessiontype == 4:  # Practice/Quali/Sprint
                    if sessionremaining == 0:                   
                        print('Practice/Quali/Sprint finished')
                        logging.info('Practice/Quali/Sprint finished')
                        # LED CHECKERED - flashing
                        time.sleep(endtime)
                        finished.set()
                        webdriver.close()
                        sys.exit()
                        # back to white RGB

                        # AUS DIESEM LOOP RAUS
                        # NOT back to chekcing if sessionstarted
                    else:
                        sys.exit()
                sys.exit()
                # else:

        else:
            print('THIS IS NOT THE WAY')     
            flag_status == 0                    # standby white Light
            finished.clear()                    # finished back to standart
            time.sleep(120)


# Threads:
Thread(target=standby).start()
Thread(target=flag_led).start()


# IDEAS:
    # Button press to start timer and synch website with video feed = timeoffset
        # offset: 88 sec ( Race 1)
        # delay = input('Input Delay: ')
        # WENN ENTSCHEIDUNG OB ARDUINO ODER RASPBERRY
        
    # RACE NUMBER IN FILE TITLE!
    
    # UPLOAD GITHUB
    # after ENDTIME -> change LED back to White (standart) TEST RUN !!!!!!!
    # Automatic start of python script when booted

    # Arduino connection 
        #ttyUSB0
        
# DONE:
    # maybe kill / start threats according to session started
    # start looking bei Uhrzeit wenn renen anfängt - 5 min
    # read array
    # 2023_calendar.js
    # calendar_utc=-3;
    # calendar=new Array(

# Scraps:
    # start Threads
    # if __name__ == '__main__':
    # Thread(target=flag_check).start()
    # Thread(target=file_reader).start()
    # Thread(target=led_change).start()
