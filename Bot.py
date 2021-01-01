from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import pathlib
import os
import youtube_dl
from moviepy.editor import *
from moviepy.video.fx.all import crop
from moviepy.video.fx.all import resize
import math
from random import randrange
from moviepy.config import change_settings
from datetime import datetime,date,timedelta

change_settings({"IMAGEMAGICK_BINARY": "C:\Program Files\ImageMagick-6.9.11-Q8\convert.exe"})

def delete_file(path):
    try:
        os.remove(str(path))
    except :
        print("Incorrect file name.")
    
def add_desc(desc):
    try:
        with open('desc.txt', 'r+') as f:
            f.truncate(0)
            f.write(desc)
            f.close()
    except:
        print("File does not exist.")


def generate_clips(video):
    video_path = "raw_videos/%s" % str(video)
    clip = VideoFileClip(video_path) 
    clip = crop(clip,y2=635)
    duration = clip.duration
    clip_start = 0
    clip_end = 60
    number = 1
    if duration > 31:
        trim = duration - 31
    clip = clip.subclip(clip_start,trim)
    duration = clip.duration
    if duration > 60:
        parts = duration/60
        frac, whole = math.modf(parts)

        while clip_end <= duration:
            temp = clip.subclip(clip_start,clip_end)
            text = 'Part %s' % str(number)
            temp_txt = TextClip(text, fontsize=50, color='white') 
            temp_txt = temp_txt.set_pos('top').set_duration(clip_end-clip_start)
            temp = CompositeVideoClip([temp,temp_txt])
            clip_start += 60
            if clip_end == (whole*60):
                clip_end += 60 * frac
            else:
                clip_end += 60 
            output = "final_videos/clip%s.mp4"  % str(number)
            temp.write_videofile(output)
            number += 1
    clip.close()
    temp.close()

def isElementExist(browser, element):
    flag = True
    try:
        browser.find_element_by_css_selector(element)
        return flag
    except:
        flag = False
        return flag

def download_new_videos():
    ydl_opts = {
        'outtmpl': 'raw_videos/%(title)s.mp4',
        'ignoreerrors': True,
        'max_downloads': 2,
        'download_archive': 'archive',
        'format': 'best',
    }
    with youtube_dl.YoutubeDL(ydl_opts) as ydl:
        try:
            ydl.download(["https://www.youtube.com/playlist?list=PLjTI-fmjC4hWzJWz4_GTx1OzU8IZPUpfO"])
        except:
            return
    


def upload_video(browser,video):
    path = str(pathlib.Path(__file__).parent.absolute())
    # Close Verification Window:
    if browser.find_element_by_class_name('verify-bar-close'):
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
    video_path = "\\final_videos\\%s" % video
    video_upload_button.send_keys(path + video_path)

    WebDriverWait(browser, 100).until_not(
        EC.presence_of_all_elements_located((By.CSS_SELECTOR, '.button.disabled.jsx-352266594'))
    )

    # Adds video description
    video_title_input = browser.find_element_by_class_name("public-DraftStyleDefault-block")
    myFile = open(path + "\desc.txt", "rt")
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
    browser.quit()
else:
    print('You are logged in!')
    browser.close()
    while True:        
        if len(os.listdir('final_videos')) != 0:
            current_time = datetime.now().time()
            min_time = datetime.now().time()
            max_time = datetime.now().time()
            min_time = current_time.replace(hour=15,minute=0,second=0,microsecond=0)
            max_time = current_time.replace(hour=23,minute=0,second=0,microsecond=0)
            if current_time > min_time and current_time < max_time: 
                wait_time = randrange(1,6) * 3600
                print("Uploading Video...")
                edited_clips = os.listdir("final_videos")
                browser = webdriver.Chrome(PATH, options=options)
                browser.get("https://www.tiktok.com/foryou")
                upload_video(browser,edited_clips[0])
                browser.close()
                file_path = "final_videos/%s" % edited_clips[0]
                delete_file(file_path)
                print('Video Successfully Uploaded! Timestamp: ' + current_time.strftime("%H:%M:%S"))
                print("Next video will upload in: " + str((wait_time/3600)) + "hr(s)")
                time.sleep(wait_time)
            else:
                if current_time < min_time:
                    wait_time = datetime.combine(date.min, min_time) - datetime.combine(date.min, current_time)
                else:
                    wait_time = datetime.combine(date.min, current_time) - datetime.combine(date.min, max_time)
                    hours = int(min_time.strftime('%H'))
                    time_added = timedelta(hours=hours)
                    wait_time = wait_time + time_added
                wait_time = wait_time.total_seconds()   
                print("Not the right time to upload.") 
                print("Waiting " + str(wait_time) + "hr(s) to upload")
                time.sleep(wait_time)
        else:
            if len(os.listdir('raw_videos')) != 0:
                print("Editing New Videos...")
                raw_clips = os.listdir("raw_videos")
                title = raw_clips[0].split('(')
                description = "Follow for more great movie clips! Movie: " + title[0] + "#movies #movie #film #cinema #films #actor #hollywood" 
                add_desc(description)
                generate_clips(raw_clips[0])
                file_path = "raw_videos/%s" % raw_clips[0]
                delete_file(file_path)
                print("New videos Added!")
            else:
                print("Downloading new videos from playlist...")
                download_new_videos()

