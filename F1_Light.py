# import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.ui import Select
import time
import sys
from datetime import datetime
# from time import sleep
from threading import Thread
from threading import Event
import serial

from inputimeout import inputimeout


# pip install webdriver-manager selenium pandas
# sudo apt-get install chromium-chromedriver
# pip install inputimeout
# Raspberry chrome_driver_path = '/usr/lib/chromium-browser/chromedriver'

# serial connection to arduino via USB
# smae serial frequency ? wie arduino


# Scraper

# chrome_driver_path = '/usr/lib/chromium-browser/chromedriver'  # Raspberry
chrome_driver_path = 'H:\\Chromedriver'     # Desktop
# chrome_driver_path = 'C:\\Chromedriver'    # Laptop

# ser_usb = serial.Serial('/dev/ttyUSB0', 57600, timeout=1)   # Raspberry
ser_usb = serial.Serial('COM13', 57600, timeout=1)  # Desktop
# ser_usb = serial.Serial('COM4', 57600, timeout=1)  # Laptop


chrome_options = Options()
chrome_options.add_argument('--headless')

webdriver = webdriver.Chrome(
    executable_path=chrome_driver_path, options=chrome_options
)

# URLs
url_dict = {"l": "https://f1.tfeed.net/live",
            "i": "https://racecontrol.indycar.com/"
            }


standart_F1_url = "https://f1.tfeed.net/live"
archive_F1_url = "https://f1.tfeed.net/year/racetrack"


def get_url():
    try:
        watch_input = (inputimeout(prompt='L(ive) or "Year/location" ', timeout=30)).lower()
        if watch_input[0] == 'l':
            url = url_dict.pop(watch_type)
        else:
            url = str('https://f1.tfeed.net/' + watch_input)
            print('Archive URL')
            print(url)
            return url
                   
    except Exception:
        watch_type = 'F1-Live'
        #print(watch_input)
        url = str(url_dict.pop("l"))
        return url

def get_watch_mode(url):
    print(url)
    time.sleep(2)
    if url == "https://f1.tfeed.net/live":
        watch_mode = 1
    elif "https://f1.tfeed.net/20" in url:
        watch_mode = 2
    else:
        watch_mode = -1
    print("watchmode: " + watch_mode)
    return watch_mode

# return watch_mode
    # try:
    #     watch_input = (inputimeout(prompt='L(ive) or "Year/location" ', timeout=30)).lower()
    #     if watch_input[0] == 'l':
    #         url = url_dict.pop(watch_type)
    #     else:
    #         url = str('https://f1.tfeed.net/' + watch_input)
    #         print('Archive URL')
    #         print(url)
    #         return url

    # except Exception:
    #     watch_type = 'F1-Live'
    #     print(watch_input)
    #     url = str(url_dict.pop("l"))
    #     return url


url = get_url()
print(url)

webdriver.get(url)
time.sleep(7)

# output_delay = int(input('Input Delay: '))

# var
request_beginn_delay = 200        # in s
endtime = 10                        # in s
led_count = 60                      # how many LEDs on LED-Strip
brightness = str(0.3)               # USE INPUT?
stream_delay = 10  # 330

# def f1_archive_skip_to_Lap1():
#     select = Select(webdriver.find_element(By.ID, 'replay_laps_select'))
#     select.select_by_index(1)


def session_info():
    year_calendar = webdriver.execute_script('return calendar')
    next_event = webdriver.execute_script('return calendarNextEvent')
    race_number = str(year_calendar[next_event])
    next_event_timestamp = (webdriver.execute_script(
        'return calendarNextEventTimestamp'))/1000
    filename = "Race %s.txt" % race_number
    # sessiontype
    return filename, next_event_timestamp

def get_flag_and_write():       # Flag
    flag_queue.clear()
    filename = session_info()[0]
    # race_number = session_info()
    # filename = "Race %s.txt" % race_number
    flag_log = open(filename, "w+")
    while not finished.is_set():
        Flag = str(webdriver.execute_script('return sessionFlag'))
        print('Flag: ' + Flag)
        flag_log.write("Flag: " + Flag + '\n')
        flag_log.flush()
        flag_queue.append(Flag)
        time.sleep(5)   # MAYBE TIME SLEEP 10 ??


def read_queue():
    flag_state = str(flag_queue.pop(0))
    lap_state = str(lap_queue.pop(0))
    return flag_state, lap_state


def sessionstart():
    
    while True:  # not finished.is_set()
        current_timestamp = round(time.time())
        # next_event_timestamp = (webdriver.execute_script('return calendarNextEventTimestamp'))/1000
        # print
        filename, next_event_timestamp = session_info()  # ???????????ßßßß

        if (next_event_timestamp - request_beginn_delay) <= current_timestamp:  # -request_beginn_delay
            flag_log = open(filename, "w+")
            print("Session started")
            flag_log.write("Session started" + '\n')
            Thread(target=get_flag_and_write).start()
            Thread(target=get_lap_and_write_lapcounter).start()
            Thread(target=session_end).start()

            # change das nocht auftritt bei currentlap > 0
            flag_queue.append(6)
            time.sleep(stream_delay)
            started.set()               # started is delay because of video feed
            # Thread(target=setup_arduino).start()
            # flag_queue.append(6)
            # !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            time.sleep(500000)

        else:
            print('This is not the Way')
            if not flag_queue:
                # print("QUEUE NOT EPMTY")
                flag_queue.append(0)
            # else:
            #     print("nothing in queue")

            # flag_queue.append(0) #maybe 2 mal machen um absicherung das kein leerlauf
            time.sleep(15)


def session_end():
    # race_number = race_info()
    # filename = "Race %s.txt" % race_number
    filename = session_info()[0]
    flag_log = open(filename, "w+")     # maybe delete because used 2 times?
    # time.sleep(200)
    time.sleep(30000)
    while not finished.is_set():                                                    # Get Sessiondata
        sessiontype = webdriver.execute_script('return sessionType')
        sessionlaps = webdriver.execute_script(
            'return sessionLeftLaps')
        sessionremaining = webdriver.execute_script(
            'return sessioninfo.remaining')
        #
        current_timestamp = round(time.time())
        next_event_timestamp = (webdriver.execute_script(
            'return calendarNextEventTimestamp'))/1000
        #

        # Sessiontype == RACE
        if sessiontype == 1 and sessionlaps == 0 and ((next_event_timestamp + 900) <= current_timestamp):
            # Race Finished
            print('Race finished')
            flag_log.write('Race finished ')
            # LED FLG CHECKERED - LED CHECKERED - flashing
            flag_queue.append(str(6))
            time.sleep(endtime)
            # back to white LED
            flag_queue.append(str(0))
            finished.set()
            webdriver.close()
            # sys.exit()

        # Practice/Quali/Sprint
        elif (sessiontype == 3 or sessiontype == 4) and sessionremaining == 0:
            print('Practice/Sprint finished')
            flag_log.write('Practice/Sprint finished')
            # LED FLG CHECKERED - LED CHECKERED - flashing
            flag_queue.append(6)
            time.sleep(endtime)
            # back to white LED
            flag_queue.append(0)
            finished.set()
            webdriver.close()
            # sys.exit()

        elif (sessiontype == 2 and sessionremaining == 0):          # TEST QUALI
            print('Quali Session finished')
            flag_log.write('Quali finished')

            timeout = time.time() + 60*30  # 30 min from now
            while not finished.is_set():
                sessionremaining = webdriver.execute_script(
                    'return sessioninfo.remaining')
                if sessionremaining != 0 or time.time() > timeout:
                    print('Quali Session started')
                    flag_queue.append(6)
                    break
                elif time.time() > timeout:
                    print('Quali Timeout')
                    break
        # sys.exit() #???
        # else:


def setup_arduino():
    # ser_usb = serial.Serial('/dev/ttyUSB0', 57600, timeout=1)   # 57600
    # ser_usb = serial.Serial('COM13', 57600, timeout=1)
    # ser_usb = serial.Serial('COM4', 57600, timeout=1)
    ser_usb.reset_input_buffer()
    time.sleep(3)
    ser_usb.write((brightness + '\n').encode())
    print("sending brightness: " + brightness)
    # bright_line = ser_usb.readline().decode('utf-8').rstrip()
    # print(bright_line)
    while True:
        if started.is_set():
            while not finished.is_set():
                flag_state, lap_state = read_queue()
                write_arduino(flag_state, lap_state)
        else:
            lap_state = flag_state = str(0)      # standby mode
            write_arduino(flag_state, lap_state)


def write_arduino(flag_state, lap_state):
    ser_usb.write((lap_state + '\n').encode())
    print("sending lapcounter: " + lap_state)

    ser_usb.write((flag_state + '\n').encode())
    print("sending state: " + flag_state)
    time.sleep(5)

    lap_line = ser_usb.readline().decode('utf-8').rstrip()
    flag_line = ser_usb.readline().decode('utf-8').rstrip()

    print(" ARD1:" + lap_line)
    print(" ARD2:" + flag_line)  # '\n'


def get_lap_and_write_lapcounter():
    sessionlaps = webdriver.execute_script('return mapLaps')
    if sessionlaps == 0:
        sessionlaps = 1

    while not finished.is_set():

        sessionleftlaps = webdriver.execute_script('return sessionLeftLaps')
        current_lap = sessionlaps - sessionleftlaps
        # (inVal - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
        lap_state = str(((led_count)/(sessionlaps)) * (current_lap))
        lap_queue.append(lap_state)
        time.sleep(5)

        # DIVISION WITH ZERO


started = Event()
finished = Event()


flag_queue = [0]  # [0, 1, 2, 3, 4, 5, 6, 7, 8]
lap_queue = [0]
# lap_queue = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,13 ,14 ,15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]

Thread(target=sessionstart).start()
Thread(target=setup_arduino).start()

# Thread(target=f1_archive_skip_to_Lap1).start()
# Thread(target=get_flag_and_write).start()
# Thread(target=lap_counter).start()


# BRIGHTNESS FIXEN !!! !!!!!!!!

# Thread(target=get_flag_and_write).start()
# time.sleep(15)
# Thread(target=read_queue).start()
# Thread(target=send_arduino).start()

# Thread(target=endclauseln, args=(flag_queue,)).start()
# time.sleep(output_delay)
# Thread(target=send_to_arduino, args=(flag_queue,)).start()


# IDEAS:
# Button press to start timer and synch website with video feed = timeoffset
# offset: 88 sec ( Race 1), P3 (2 min )
# delay = input('Input Delay: ')

# Automatic start of python script when booted

# second led Strip seperate connection
# an Arduino brightness schicken (INPUT 1 time at beginn)
# maybe add suport for historical races? same website or other API ?
# maybe ADD SEPERATE VERSION only for test loggin gpurpose of all variables (later evaluation of maybe anomalys)
# + TIMINGS OPTIMIZEN / RECORDEN
# ARDUINO MAYBE WHENN FOR TIME NO MODE GO MODE 0
# arduino FIX MIT brogohtness -1
# maybe try:
#  if (myvariable!=NULL)
# {
#  printfucntion(myvariable);
# }
# PERFPRMANCE
# maybe change chrome_driver_path accordindg to device (win or Raspberry)
# start script on boot
# maybe voicecomms delayed???
# Arduino if -1 DONT CHANGE FLAG

# INITIAL DELAY to vid stream
# time countdown before session ?
# flag effekt for session started

# ERROR: - 300s FUNKTIONIERT NICHT
# writet flag schneller als er liest (time.sleep(10) als fix? temporalrily)
# use colour for print Flag font
# set finished later to let mode 6 finish
# stream delay?!?
# https://f1.tfeed.net/tt.js?0.39271834533555516
# funciton race info return multiple vars as list (sessionremianing, ... )
# archive data for Quali?
# acestream?
# race finsihed immediatly after start because lap == 0? timesleep 2000 temp fix
# lap queue ?
# sessionleftlaps not changign remaining 0 ? FIXED /live URL
# sessinleftlaps -> session end delay queue
# flag_queue pop from empty list????
# next event timestamp doesnt change immediatly after race finsieh (So 21:15 , race finished 19:20)
# cleanup loop arduino write nearly all similar
# add timestamp or date or sesison type when created to FILENAME

# TIME DELAY bei Archive removen (maybe different watch_modes ?)
# countdown (5-1) for race archive


# NOTES: - Beginn delay ist Delay + 5 Sek why? KP


# Fixed:
# time stamp gilt during session
# timestamp for session beginn funktioniert nicht ?
# time remianing is for every Q Session -> script für Quali ändern , oder abfrage weclhes Q ?
# session end für quali ändern
# time remaining resettet sich after each Q -> maybe delay betwenn end end next start? (cant work for red flags?) maybe check historical races to collect data?
