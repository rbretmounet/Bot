from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import pathlib

def isElementExist(browser, element):
    flag = True
    try:
        browser.find_element_by_css_selector(element)
        return flag
    except:
        flag = False
        return flag

def upload_video(browser):
    path = str(pathlib.Path(__file__).parent.absolute())
    # Close Verification Window:
    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'verify-bar-close'))
    )
    verification_button = browser.find_element_by_class_name('verify-bar-close')
    verification_button.click()

    # Open Upload Menu
    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'jsx-2482409767'))
    )

    upload_button = browser.find_element_by_class_name('jsx-2482409767')
    upload_button.click()
    
    # Uploads Video
    WebDriverWait(browser, 100).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, 'upload-btn-input'))
    )
    video_upload_button = browser.find_element_by_class_name('upload-btn-input')
    video_upload_button.send_keys(path + '\\downloaded\\main.mp4')

    WebDriverWait(browser, 100).until_not(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.button.disabled.jsx-352266594'))
    )

    # Adds video description
    video_title_input = browser.find_element_by_class_name("public-DraftStyleDefault-block")
    myFile = open(path + "\\downloaded\\desc.txt", "rt")
    contents = str(myFile.read())

    myFile.close()
    video_title_input.send_keys(contents)
    
    # Posts video
    submit_button = browser.find_element_by_class_name('btn-post')
    submit_button.click()


options = Options()
options.add_argument("user-data-dir=selenium")

PATH = "C:\chromedriver.exe"

browser = webdriver.Chrome(PATH, options=options)

browser.get("https://www.tiktok.com/foryou")

isExistLogin = isElementExist(browser, '.login-button')

if isExistLogin:
    login_button = browser.find_element_by_class_name('login-button')
    login_button.click()
    print('You have 1 minute to login and relaunch')
    time.sleep(60)
    browser.exit()
else:
    print('You are already logged in')
    upload_video(browser)
    browser.exit()