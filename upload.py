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
API_KEY = config('YT_API_KEY')

YOUTUBE = build('youtube', 'v3', developerKey=API_KEY)

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

def download_new_videos():
    with youtube_dl.YoutubeDL({}) as ydl:
        ydl.download(['https://www.youtube.com/playlist?list=PLjTI-fmjC4hWzJWz4_GTx1OzU8IZPUpfO'])

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

playlist_id = 'PLjTI-fmjC4hWzJWz4_GTx1OzU8IZPUpfO'

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
    while len(os.listdir('Videos')) != 0:
        upload_video(browser)
    print('No more videos')
    # Execute code to add new video and delete previous clips
