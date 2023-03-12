#import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import time
import sys
from datetime import datetime
#from time import sleep
from threading import Thread
from threading import Event
import serial

#pip install webdriver-manager selenium pandas
#sudo apt-get install chromium-chromedriver
# Raspberry chrome_driver_path = '/usr/lib/chromium-browser/chromedriver'

# serial connection to arduino via USB
# smae serial frequency ? wie arduino


# Scraper
chrome_driver_path = 'H:\\Chromedriver'
#chrome_driver_path = '/usr/lib/chromium-browser/chromedriver'
chrome_options = Options()
chrome_options.add_argument('--headless')

webdriver = webdriver.Chrome(
    executable_path=chrome_driver_path, options=chrome_options
)

url = "https://f1.tfeed.net/"

webdriver.get(url)
time.sleep(8)

#output_delay = input('Input Delay: ')
#LED
#var
request_beginn_delay = 300          # in s
endtime = 10                        # in s
led_count = 55                      # how many LEDs on LED-Strip      

def race_info ():
    year_calendar = webdriver.execute_script('return calendar')
    next_finished = webdriver.execute_script('return calendarNextEvent')
    race_number = str(year_calendar[next_finished])
    print(race_number)    
    return race_number
    

def get_flag_and_write():                     # Flag
    race_number = race_info()
    filename = "Race %s.txt" % race_number
    flag_log = open(filename, "w+")
    flag_queue.clear() 
    while not finished.is_set():
        Flag = str(webdriver.execute_script('return sessionFlag'))
        print('Flag: ' + Flag)
        flag_log.write("Flag: " + Flag + '\n')
        flag_log.flush()
        flag_queue.append(Flag)
        time.sleep(5)
        
def read_queue():
    #flag_queue.append(0)
    while not finished.is_set():
        state = str(flag_queue.pop(0))  
        time.sleep(3) 
        return state
          


def sessionstart():
    while True:
        current_timestamp = round(time.time())
        next_finished_timestamp = (webdriver.execute_script(
            'return calendarNextEventTimestamp'))/1000
                                                                                        # Test if next_finished_timestamp changes while event is runnnig or only after 
                                                                                        #maybe add time to timestamp to cover event duration 
                                                                                        
        while not finished.is_set():
            if (next_finished_timestamp-request_beginn_delay) <= current_timestamp:     # Checking if Time = next finished - 5 min
                Thread(target=get_flag_and_write).start()
                Thread(target=session_end).start()
                time.sleep(15)
                Thread(target=read_queue).start()
                Thread(target=lap_counter).start()
                 
            else: 
                print('This is not the Way')
                flag_queue.append(0) 
                #flag_queue.append(0) #maybe 2 mal machen um absicherung das kein leerlauf 
                time.sleep(3)

        time.sleep(10)

def session_end():
    flag_log = open("flaglog.txt", "w+")  
    while not finished.is_set():                                                    # Get Sessiondata
            sessiontype = webdriver.execute_script('return sessionType')
            sessionleftlaps = webdriver.execute_script(
                'return sessionLeftLaps')
            sessionremaining = webdriver.execute_script(
                'return sessioninfo.remaining')

            if sessiontype == 1 and sessionleftlaps == 0:                           # Sessiontype == RACE            
                print('Race finished')                                              # Race Finished
                flag_log.write('Race finished ')
                flag_queue.append(6)                                                # LED FLG CHECKERED - LED CHECKERED - flashing
                time.sleep(endtime)
                flag_queue.append(0)                                                # back to white LED
                finished.set()
                webdriver.close()
                sys.exit()            

            elif (sessiontype == 2 or sessiontype == 3 or sessiontype == 4) and sessionremaining == 0:          # Practice/Quali/Sprint                 
                print('Practice/Quali/Sprint finished')
                flag_log.write('Practice/Quali/Sprint finished')
                flag_queue.append(6)                                                # LED FLG CHECKERED - LED CHECKERED - flashing
                time.sleep(endtime)
                flag_queue.append(0)                                                # back to white LED
                finished.set()
                webdriver.close()
                sys.exit()  
                  
            sys.exit()
            # else:

def send_arduino():
    #ser_usb = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)   # 57600
    #ser_usb.reset_input_buffer()
    while not finished.is_set():
        state = read_queue()
        lap_state = lap_counter()
        #ser_usb.write(state.encode())
        #ser_usb.write(lap_counter)
        print("sending state: " + state + '\n')  
        print("sending lapcounter: " + lap_state + '\n')  
        #line = ser_usb.readline().decode('utf-8').rstrip()
        #print("Arduino received: " + line)


def lap_counter():
    while not finished.is_set():
        # maybe sessionlaps
        sessionlaps = webdriver.execute_script('return mapLaps')
        sessionleftlaps = webdriver.execute_script('return sessionLeftLaps')
        current_lap = sessionlaps - sessionleftlaps
        lap_state = str(((led_count)/(sessionlaps)) * (current_lap))
        time.sleep(5)
        return lap_state
        
        #(inVal - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
                


finished = Event()
flag_queue = [0]

Thread(target=sessionstart).start()
Thread(target=send_arduino).start()
Thread(target=get_flag_and_write).start()


# Thread(target=get_flag_and_write).start()
# time.sleep(15)
# Thread(target=read_queue).start()
# Thread(target=send_arduino).start()

# Thread(target=endclauseln, args=(flag_queue,)).start()
# time.sleep(output_delay)
# Thread(target=send_to_arduino, args=(flag_queue,)).start()

# IDEAS:
    # Button press to start timer and synch website with video feed = timeoffset
        # offset: 88 sec ( Race 1)
        # delay = input('Input Delay: ')
        
    # RACE NUMBER IN FILE TITLE!
    
    # UPLOAD GITHUB
    # Automatic start of python script when booted

    # Arduino connection 
        #ttyUSB0
    # second led Strip seperate connection   

# NOTES: - Beginn delay ist Delay + 5 Sek why? KP
        # maybe change chrome_driver_path accordindg to device (win or Raspberry)
        # start script on boot

#scraps:  
            # def send_to_arduino(state):
            #   ser_usb = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
            #   ser_usb.reset_input_buffer()
            #   while True:
            #   ser_usb.write(state)
            #   print("sending: " + state)
            #   time.sleep(5) 

# def read_queue_and_send_arduino():
#     #ser_usb = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
#     #ser_usb.reset_input_buffer()
#     while not finished.is_set():
#         state = flag_queue.pop(0)  
#         #ser_usb.write(state)
#         print("sending: " + state)
#         time.sleep(5)  