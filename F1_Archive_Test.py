#import threading
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.expected_conditions import presence_of_element_located
import time
import sys
import time
import datetime
from datetime import datetime
#from time import sleep
from threading import Thread
from threading import Event
import serial

from inputimeout import inputimeout

chrome_driver_path = 'H:\\Chromedriver' 

chrome_options = Options()
chrome_options.add_argument('--headless')

webdriver = webdriver.Chrome(
    executable_path=chrome_driver_path, options=chrome_options
)

url = "https://f1.tfeed.net/live"

webdriver.get(url)
time.sleep(7)


current_timestamp = round(time.time())
year_calendar = webdriver.execute_script('return calendar')
next_event = webdriver.execute_script('return calendarNextEvent')
race_number = str(year_calendar[next_event])
next_event_timestamp = (webdriver.execute_script(
    'return calendarNextEventTimestamp'))/1000
filename = "Race %s.txt" % race_number

next_date = year_calendar[next_event+1]
next_time = year_calendar[next_event+2]

next_time_stamp = f'{next_date} {next_time}'
TT = datetime.strptime(next_time_stamp, '%d/%m/%Y %H:%M')
time_stamp = TT.timestamp()-3600
print(time_stamp)
# - 1H due to Original timestamp is UTC
# - maybe next Event not changing ? - change manually 
# if new timestamp > current 
    # set new timestmap , mextevent

#FUKNTIONIERT:
    # next_date = str(year_calendar[next_event+1])
    # next_time = str(year_calendar[next_event+2])

    # next_time_stamp = f'{next_date} {next_time}'
    # TT = datetime.strptime(next_time_stamp, '%d/%m/%Y %H:%M')
    # time_stamp = TT.timestamp()
    # print(time_stamp)
    # # - 1H 





# element = datetime.strptime(next_time_stamp,"%d/%m/%Y")
 
# timestamp = datetime.timestamp(element)
# print(timestamp)



# if next_event_timestamp < current_timestamp:
#     next_event_timestamp 
#     time.sleep(5)

#                 filename, next_event_timestamp = session_info() 

#                 if (next_event_timestamp - request_beginn_delay) <= current_timestamp:  # -request_beginn_delay

time.sleep(50)