from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import pathlib
import os
import youtube_dl
from googleapiclient.discovery import build
from moviepy.editor import *
from moviepy.video.fx.all import crop
import math
from random import randrange


def delete_file(path):
    os.remove(str(path))
    
def generate_clips(video):
    video_path = "raw_videos/%s" % str(video)
    clip = VideoFileClip(video_path) 
    clip = crop(clip,y2=640)
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
        'outtmpl': 'raw_videos/%(id)s.mp4',
        'ignoreerrors': True,
        'max_downloads': 10,
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
    # WebDriverWait(browser, 100).until(
    #     EC.presence_of_all_elements_located((By.CLASS_NAME, 'verify-bar-close'))
    # )
    # verification_button = browser.find_element_by_class_name('verify-bar-close')
    # verification_button.click()

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
    browser.quit()
else:
    print('You are already logged in')
    while True:        
        if len(os.listdir('final_videos')) != 0:
            wait_time = randrange(1,6) * 3600
            print("Uploading Video...")
            edited_clips = os.listdir("final_videos")
            upload_video(browser,edited_clips[0])
            browser.get("https://www.tiktok.com/foryou")
            file_path = "final_videos/%s" % edited_clips[0]
            delete_file(file_path)
            print('Video Successfully Uploaded.')
            print("Next video will upload in: "+ str((wait_time/3600)) + "hr(s)")
            time.sleep(wait_time)
        else:
            print('No more videos')
            print('Adding new video')
            if len(os.listdir('raw_videos')) != 0:
                raw_clips = os.listdir("raw_videos")
                generate_clips(raw_clips[0])
                file_path = "raw_videos/%s" % raw_clips[0]
                delete_file(file_path)
            else:
                download_new_videos()
                raw_clips = os.listdir("raw_videos")
                generate_clips(raw_clips[0])
                file_path = "raw_videos/%s" % raw_clips[0]
                delete_file(file_path)
