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
time.sleep(7)

#output_delay = input('Input Delay: ')
#LED
#var
request_beginn_delay = 200         # in s
endtime = 10                        # in s
led_count = 60                      # how many LEDs on LED-Strip      
brightness = str(0.5)               # USE INPUT?
stream_delay = 60

def race_info ():
    year_calendar = webdriver.execute_script('return calendar')
    next_event = webdriver.execute_script('return calendarNextEvent')
    race_number = str(year_calendar[next_event])
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
        time.sleep(10)
        
def read_queue():
    #flag_queue.append(0)
    #while not finished.is_set()
    state = str(flag_queue.pop(0))  
                                        #time.sleep(3) 
    return state
          


def sessionstart():
    race_number = race_info()
    filename = "Race %s.txt" % race_number
    flag_log = open(filename, "w+")     
                                                                                        # Test if next_event_timestamp changes while event is runnnig or only after 
                                                                                        #maybe add time to timestamp to cover event duration 
                                                                                        #  or use calendar info?
                                                                             
    while not finished.is_set():
        current_timestamp = round(time.time())
        next_event_timestamp = (webdriver.execute_script('return calendarNextEventTimestamp'))/1000

        if (next_event_timestamp - request_beginn_delay) <= current_timestamp:  #-request_beginn_delay
            print("Session started")    
            flag_log.write("Session started" + '\n')
            # print in file?
            Thread(target=get_flag_and_write).start()
            #Thread(target=session_end).start()
            time.sleep(stream_delay)
            Thread(target=send_arduino).start()
            #Thread(target=lap_counter).start()
            time.sleep(500000)
        else: 
            print('This is not the Way')
            if flag_queue:
                #print("QUEUE NOT EPMTY")
                flag_queue.append(0)
            else:
                print("nothing in queue")

            #flag_queue.append(0) #maybe 2 mal machen um absicherung das kein leerlauf 
            time.sleep(5)

    time.sleep(10)

def session_end():
    race_number = race_info()
    filename = "Race %s.txt" % race_number
    flag_log = open(filename, "w+")     # maybe delete because used 2 times?
    while not finished.is_set():                                                    # Get Sessiondata
            sessiontype = webdriver.execute_script('return sessionType')
            sessionleftlaps = webdriver.execute_script(
                'return sessionLeftLaps')
            sessionremaining = webdriver.execute_script(
                'return sessioninfo.remaining')

            if sessiontype == 1 and sessionleftlaps == 0:                           # Sessiontype == RACE            
                print('Race finished')                                              # Race Finished
                flag_log.write('Race finished ')
                flag_queue.append(str(6))                                                # LED FLG CHECKERED - LED CHECKERED - flashing
                time.sleep(endtime)
                flag_queue.append(str(0))                                                # back to white LED
                finished.set()
                webdriver.close()
                #sys.exit()            

            elif (sessiontype == 2 or sessiontype == 3 or sessiontype == 4) and sessionremaining == 0:          # Practice/Quali/Sprint                 
                print('Practice/Quali/Sprint finished')
                flag_log.write('Practice/Quali/Sprint finished')
                flag_queue.append(6)                                                # LED FLG CHECKERED - LED CHECKERED - flashing
                time.sleep(endtime)
                flag_queue.append(0)                                                # back to white LED
                finished.set()
                webdriver.close()
                #sys.exit()  
                  
            #sys.exit() #???
            # else:

def send_arduino():
    #ser_usb = serial.Serial('/dev/ttyUSB0', 57600, timeout=1)   # 57600
    ser_usb = serial.Serial('COM13', 57600, timeout=1)
    ser_usb.reset_input_buffer()
    time.sleep(3)
    ser_usb.write((brightness + '\n' ).encode())
    print("sending brightness: " + brightness )
    # bright_line = ser_usb.readline().decode('utf-8').rstrip()
    # print(bright_line)
    while True: #not finished.is_set()
        
        lap_state = lap_counter()
        state = read_queue()

        ser_usb.write((lap_state + '\n' ).encode())
        print("sending lapcounter: " + lap_state )
        #time.sleep(1)
        #state = str(flag_queue.pop(0))
        ser_usb.write((state + '\n' ).encode())        
        print("sending state: " + state + '\n')
        time.sleep(5)  

        lap_line = ser_usb.readline().decode('utf-8').rstrip()
        state_line = ser_usb.readline().decode('utf-8').rstrip()
        print(" ARD1:" + lap_line + '\n')
        print(" ARD2:" + state_line +'\n')
        
      

def lap_counter():
    while not finished.is_set():
        sessionlaps = webdriver.execute_script('return mapLaps')
        sessionleftlaps = webdriver.execute_script('return sessionLeftLaps')
        # sessionlaps = 50
        # current_lap = lap_queue.pop(0)
        # # sessionleftlaps = 32
        current_lap = sessionlaps - sessionleftlaps
        lap_state = str(((led_count)/(sessionlaps)) * (current_lap))
        time.sleep(5)
        return lap_state
    else:
        lap_state = str(0)  
        #(inVal - inMin) * (outMax - outMin) / (inMax - inMin) + outMin
               

finished = Event()

flag_queue = [0]      #[0, 1, 2, 3, 4, 5, 6, 7, 8]
#lap_queue = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12,13 ,14 ,15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39]

Thread(target=sessionstart).start()
#Thread(target=send_arduino).start()
#Thread(target=get_flag_and_write).start()
#Thread(target=lap_counter).start()


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
    #maybe ADD SEPERATE VERSION only for test loggin gpurpose of all variables (later evaluation of maybe anomalys) 
            # + TIMINGS OPTIMIZEN / RECORDEN
    #ARDUINO MAYBE WHENN FOR TIME NO MODE GO MODE 0
    # arduino FIX MIT brogohtness -1 
    #maybe try: 
    #  if (myvariable!=NULL)
    # {
    #  printfucntion(myvariable);
    # }
    #PERFPRMANCE



    #INITIAL DELAY to vid stream
    # time countdown before session ?
    # flag effekt for session started

    # ERROR: - 300s FUNKTIONIERT NICHT
            # writet flag schneller als er liest (time.sleep(10) als fix? temporalrily)
        #time stamp gilt during session
                #timestamp for session beginn funktioniert nicht ?
                # use colour for print Flag font
                 # set finished later to let mode 6 finish
        # stream delay?!?
                # sesson stareted only after reboot of script?
        # time remianing is for every Q Session -> script für Quali ändern , oder abfrage weclhes Q ?
        # session end für quali ändern 
            #https://f1.tfeed.net/tt.js?0.39271834533555516
        # time remaining resettet sich after each Q -> maybe delay betwenn end end next start? (cant work for red flags?) maybe check historical races to collect data?
        # sessions started for Q changen  
        # more different script for session types ( session start and session end)
        # maybe start event?

# NOTES: - Beginn delay ist Delay + 5 Sek why? KP
        # maybe change chrome_driver_path accordindg to device (win or Raspberry)
        # start script on boot
