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

from inputimeout import inputimeout

chrome_driver_path = 'H:\\Chromedriver' 

chrome_options = Options()
chrome_options.add_argument('--headless')

webdriver = webdriver.Chrome(
    executable_path=chrome_driver_path, options=chrome_options
)

url = "https://f1.tfeed.net/2022/suzuka"

webdriver.get(url)
time.sleep(7)

# def A():
#     while True:
#         Flag = webdriver.execute_script('return sessionFlag')
#         session_started= webdriver.execute_script('return sessionStarted')
#         session_finished = webdriver.execute_script('return sessionFinished')
#         print(Flag)
#         print(session_finished)
#         print(session_started)
#         print()
#         time.sleep(10)

# A()

# element = webdriver.find_element(By.ID, "replay_laps_select")
# all_options = element.find_elements(By.TAG_NAME, "option")
# for option in all_options:
#     print("Value is: %s" % option.get_attribute("value"))
#     option.click()

from selenium.webdriver.support.ui import Select
select = Select(webdriver.find_element(By.ID, 'replay_laps_select'))
select.select_by_index(1)

time.sleep(5)

Flag = webdriver.execute_script('return sessionFlag')
session_started= webdriver.execute_script('return sessionStarted')
session_finished = webdriver.execute_script('return sessionFinished')
print(Flag)
print(session_finished)
print(session_started)
print()

# select.select_by_visible_text("text")
# select.select_by_value(value)
