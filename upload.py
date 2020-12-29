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
from decouple import config
from moviepy.editor import *
from moviepy.video.fx.all import crop
import math

API_KEY = config('YT_API_KEY')

YOUTUBE = build('youtube', 'v3', developerKey=API_KEY)

def delete_files(path):
    if os.path.exists(str(path)):
        os.remove(str(path))
    else:
        print("The file does not exist")

def generate_clips(video):
    video_path = "raw_videos/%s.mp4" % str(video)
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
    video = None


def sort_playlist(playlist_id, videos):
    nextPageToken = None
    while True:
        pl_request = YOUTUBE.playlistItems().list(
            part='contentDetails',
            playlistId=playlist_id,
            maxResults=50,
            pageToken=nextPageToken
        )

        pl_response = pl_request.execute()

        vid_ids = []
        for item in pl_response['items']:
            vid_ids.append(item['contentDetails']['videoId'])

        vid_request = YOUTUBE.videos().list(
            part="statistics",
            id=','.join(vid_ids)
        )

        vid_response = vid_request.execute()

        for item in vid_response['items']:
            vid_views = item['statistics']['viewCount']

            vid_id = item['id']
            yt_link = f'https://youtu.be/{vid_id}'

            videos.append(
                {
                    'views': int(vid_views),
                    'url': yt_link
                }
            )

        nextPageToken = pl_response.get('nextPageToken')

        if not nextPageToken:
            break

    videos.sort(key=lambda vid: vid['views'], reverse=True)


def isElementExist(browser, element):
    flag = True
    try:
        browser.find_element_by_css_selector(element)
        return flag
    except:
        flag = False
        return flag

def download_new_videos(videos):
    ydl_opts = {
        'outtmpl': 'raw_videos/download.mp4'
    }
    for video in videos[:10]:
        with youtube_dl.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video['url']])

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
    video_upload_button.send_keys(path + '\\final_videos\\main.mp4')

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

playlist_id = 'PLjTI-fmjC4hWzJWz4_GTx1OzU8IZPUpfO'

options = Options()
options.add_argument("user-data-dir=selenium")

PATH = "C:\chromedriver.exe"

#browser = webdriver.Chrome(PATH, options=options)

#browser.get("https://www.tiktok.com/foryou")

#isExistLogin = isElementExist(browser, '.login-button')
videos = []
#sort_playlist(playlist_id, videos)
generate_clips("clip4")
delete_files("raw_videos/clip4.mp4")
# if isExistLogin:
#     login_button = browser.find_element_by_class_name('login-button')
#     login_button.click()
#     print('You have 1 minute to login and relaunch')
#     time.sleep(60)
#     browser.quit()
# else:
#     print('You are already logged in')
#     while len(os.listdir('final_videos')) != 0:
#         upload_video(browser)
#     print('No more videos')
#     print('Adding new video')
#     if len(os.listdir('final_videos')) == 0:
#         download_new_videos(videos)
#     else:
#         #take raw_video and generate clips.
#         generate_clips()
    
    # Execute code to add new video and delete previous clips
