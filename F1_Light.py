from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
from selenium.webdriver.support.ui import Select
import time
from datetime import datetime
from threading import Thread
from threading import Event
import serial

from inputimeout import inputimeout

# Install
# pip install webdriver-manager selenium pandas
# sudo apt-get install chromium-chromedriver
# pip install inputimeout





# Scraper

# chrome_driver_path = '/usr/lib/chromium-browser/chromedriver'  # Raspberry
chrome_driver_path = 'H:\\Chromedriver'     # Desktop
#chrome_driver_path = 'C:\\Chromedriver'    # Laptop

#ser_usb = serial.Serial('/dev/ttyUSB0', 57600, timeout=1)   # Raspberry
ser_usb = serial.Serial('COM13', 57600, timeout=1)  # Desktop
#ser_usb = serial.Serial('COM4', 57600, timeout=1)  # Laptop


chrome_options = Options()
chrome_options.add_argument('--headless')

webdriver = webdriver.Chrome(
    executable_path=chrome_driver_path, options=chrome_options
)

# URLs
url_dict = {"l": "https://f1.tfeed.net/live",
            "i": "https://racecontrol.indycar.com/",    # COMING SOON
            "a": "https://getraceresults.com/",         # COMING SOON
            }


standart_F1_url = "https://f1.tfeed.net/live"
archive_F1_url = "https://f1.tfeed.net/year/racetrack"


def get_url():
    try:
        watch_type = (inputimeout(
            prompt='[L]ive or "Year/location" ', timeout= 15)).lower()
        print("Live" if watch_type in url_dict else "Archive")
        url = url_dict.get(watch_type, f"https://f1.tfeed.net/{watch_type}")
        return url
    except Exception:
        url = url_dict.get("l")
        return url

def get_watch_mode(url):
    print(url)
    time.sleep(2)
    if url == "https://f1.tfeed.net/live" in url:
        watch_mode = 1                      # F1 - LIVE
    elif "https://f1.tfeed.net/20" in url:
        watch_mode = 2                      # F1 - ARCHIVE
    else:
        watch_mode = -1
    print("watchmode: " + str(watch_mode))
    return watch_mode


url = get_url()
print(url)

webdriver.get(url)
time.sleep(10)

# output_delay = int(input('Input Delay: '))

# Session Setup
request_beginn_delay = 200        # in s (time before session starts)
endtime = 100                      # in s (time after session end)
led_count = 50                      # how many LEDs on LED-Strip
brightness = str(0.25)               # brightness LED-Strip
stream_delay = 100                   # delay of Live-Stream to data

def f1_archive_skip_to_Lap1(): # NOT RELIABLE maybe remove 
     time.sleep(5)
     select = Select(webdriver.find_element(By.ID, 'replay_laps_select'))
     select.select_by_index(5)


def session_info():
    year_calendar = webdriver.execute_script('return calendar')
    next_event = webdriver.execute_script('return calendarNextEvent')
    race_number = str(year_calendar[next_event])
    next_event_timestamp = (webdriver.execute_script(
        'return calendarNextEventTimestamp'))/1000
    filename = "Race %s.txt" % race_number
    return filename, next_event_timestamp

def get_flag_and_write():       # Flag
    flag_queue.clear()
    lap_queue.clear()
    filename = session_info()[0]
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
    watch_mode = get_watch_mode(url)
    while not started.is_set():
        if watch_mode == 1:
                current_timestamp = round(time.time())
                filename = session_info()[0]
                next_event_timestamp = get_time_stamp()
                if (next_event_timestamp - request_beginn_delay) <= current_timestamp:  
                    flag_log = open(filename, "w+")
                    print("Session started")
                    flag_log.write("Session started" + '\n')
                    Thread(target=get_flag_and_write).start()
                    Thread(target=get_lap_and_write_lapcounter).start()
                    Thread(target=session_end).start()

                    # change das nocht auftritt bei currentlap > 0
                    flag_queue.append(-2)       
                    time.sleep(stream_delay)         # started is delay because of video feed
                    started.set()              
                else:
                    print('This is not the Way')
                    time.sleep(15)
        elif watch_mode == 2:
            print("Starting in 5 Seconds")
            for i in range(6):
                print(i)
                time.sleep(1)
            print("Session started")
            Thread(target=f1_archive_skip_to_Lap1).start()
            Thread(target=get_flag_and_write).start()
            Thread(target=get_lap_and_write_lapcounter).start()
            Thread(target=session_end).start()
            flag_queue.append(-2)
            
            time.sleep(2)
            started.set()
        else: 
            while True:
                print("UNKNOWN WATCH_MODE")
                time.sleep(2)


def session_end():
    filename = session_info()[0]
    flag_log = open(filename, "w+")     
    time.sleep(800)
    while not finished.is_set():                                                    # Get Sessiondata
        sessiontype = webdriver.execute_script('return sessionType')
        sessionlaps = webdriver.execute_script(
            'return sessionLeftLaps')
        sessionremaining = webdriver.execute_script(
            'return sessioninfo.remaining')
        current_timestamp = round(time.time())
        next_event_timestamp = (webdriver.execute_script(
            'return calendarNextEventTimestamp'))/1000
        session_finished = webdriver.execute_script('return sessionFinished')
        watch_mode = get_watch_mode(url)
        
        # RACE
        if (sessiontype == 1 and sessionlaps == 0 and ((next_event_timestamp + 900) <= current_timestamp)) or (watch_mode == 2 and session_finished == 1):
            print('Race finished')
            flag_log.write('Race finished ')
            flag_queue.append(str(6))
            time.sleep(endtime)
            flag_queue.append(str(0))
            finished.set()
            started.clear()
            Thread(target=sessionstart).start()
            webdriver.close()

        # Practice/Sprint
        elif (sessiontype == 2 or sessiontype == 4) and sessionremaining == 0 and ((next_event_timestamp + 900) <= current_timestamp):
            print('Practice/Sprint finished')
            flag_log.write('Practice/Sprint finished')
            flag_queue.append(6)
            time.sleep(endtime)
            flag_queue.append(0)
            finished.set()
            started.clear()
            webdriver.close()

        # Qualifying
        elif (sessiontype == 3 and sessionremaining == 0 and ((next_event_timestamp + 900) <= current_timestamp)):
            print('Quali Session finished')
            flag_log.write('Quali finished')
            flag_queue.append(-2)
            timeout = time.time() + 60*30  # 30 min from now
            while not finished.is_set():
                sessionremaining = webdriver.execute_script(
                    'return sessioninfo.remaining')
                if sessionremaining != 0 or time.time() > timeout:
                    print('Quali Session started')
                    flag_queue.append(-2)
                    break
                elif time.time() > timeout:
                    print('Quali Timeout')
                    flag_queue.append(0)
                    lap_queue.append(0)
                    finished.set()
                    started.clear()
                    break
                time.sleep(5)
                 

def setup_arduino():
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
    sessiontype = webdriver.execute_script('return sessionType')

    while not finished.is_set():
        if sessiontype == 2 or sessiontype == 3:
            lap_queue.append(led_count)
            
        else:
            sessionlaps = webdriver.execute_script('return mapLaps')
            sessionleftlaps = webdriver.execute_script('return sessionLeftLaps')
            current_lap = sessionlaps - sessionleftlaps +1
            # (inVal - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
            lap_state = str(((led_count)/(sessionlaps)) * (current_lap))
            lap_queue.append(lap_state)
            
        time.sleep(5)
        

def get_time_stamp():
    year_calendar = webdriver.execute_script('return calendar')
    next_event_timestamp = (webdriver.execute_script(
        'return calendarNextEventTimestamp'))/1000
    current_timestamp = round(time.time())
    time.sleep(5)
    
    if (next_event_timestamp + 3600) < current_timestamp:
        next_event = webdriver.execute_script('return calendarNextEvent')
        next_date = year_calendar[next_event+1]
        next_time = year_calendar[next_event+2]
        next_time_stamp = f'{next_date} {next_time}'
        TT = datetime.strptime(next_time_stamp, '%d/%m/%Y %H:%M')
        next_event_timestamp = TT.timestamp()-3600
        print(next_event_timestamp)
        for i in range(10):
            print("NEW TIMESTAMP SET")
        time.sleep(20)
        return next_event_timestamp 
    next_event_timestamp = (webdriver.execute_script(
        'return calendarNextEventTimestamp'))/1000
    print("Timestamp check")
    return next_event_timestamp

started = Event()
finished = Event()


flag_queue = []  
lap_queue = []
# lap_queue = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,13 ,14 ,15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]
# [0, 1, 2, 3, 4, 5, 6, 7, 8]

Thread(target=sessionstart).start()
Thread(target=setup_arduino).start()
Thread(target=session_info).start()


# IDEAS:
    # Button press to start timer and synch website with video feed = timeoffset
    # + TIMINGS OPTIMIZEN / RECORDEN
    # PERFPRMANCE
    # maybe change chrome_driver_path accordindg to device (win or Raspberry)
    # start script on boot

# ERROR:
    # https://f1.tfeed.net/tt.js?0.39271834533555516
    # archive data for Quali?
    # sessionleftlaps -> session end delay queue
    # flag_queue pop from empty list????
    # next event timestamp doesnt change immediatly after race finsieh (So 21:15 , race finished 19:20)
    # cleanup loop arduino write nearly all similar
    # add timestamp or date or sesison type when created to FILENAME

# NOTES: - Beginn delay ist Delay + 5 Sek why? KP


# Fixed:
    # time stamp gilt during session
    # timestamp for session beginn funktioniert nicht ?
    # time remianing is for every Q Session -> script für Quali ändern , oder abfrage weclhes Q ?
    # session end für quali ändern
    # time remaining resettet sich after each Q -> maybe delay betwenn end end next start? (cant work for red flags?) maybe check historical races to collect data?
