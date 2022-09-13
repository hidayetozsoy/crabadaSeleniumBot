import requests, shutil, os, sys
sys.path.append((os.path.dirname(__file__)))
from consts import *

CAPTCHA_IMAGES_PATH = "./captchaImages/" #slash koymayi unutma 

def downloadMainImg(mainImgId, mainImgUrl):
    mainImgJpg = mainImgId + ".jpg"
    mainImg = requests.get(mainImgUrl, stream = True, headers=HEADERS)
    if mainImg.status_code == 200:
        mainImg.raw.decode_content = True
        folderPath = CAPTCHA_IMAGES_PATH + mainImgId
        print(folderPath)
        if not os.path.isdir(folderPath):
            os.mkdir(folderPath)
        with open(folderPath+"/"+mainImgJpg,'wb') as f:
            shutil.copyfileobj(mainImg.raw, f)
        print('Image sucessfully Downloaded: ',mainImgId)
    else:
        print('Image Couldn\'t be retreived')

def downloadQues(ques, mainImgId):
    ques1url = "https://static.geetest.com/" + ques[0]
    ques2url = "https://static.geetest.com/" + ques[1]
    ques3url = "https://static.geetest.com/" + ques[2]
    ques1Img = requests.get(ques1url, stream = True, headers=HEADERS)
    ques2Img = requests.get(ques2url, stream = True, headers=HEADERS)
    ques3Img = requests.get(ques3url, stream = True, headers=HEADERS)

    quesIds = list()
    folderPath = CAPTCHA_IMAGES_PATH + mainImgId

    for que in ques:
        quesIds.append(que.split("/")[-1])
    if ques1Img.status_code == 200:
        ques1Img.raw.decode_content = True
        with open(folderPath+"/q1-"+quesIds[0],'wb') as f:
            shutil.copyfileobj(ques1Img.raw, f)
        print('Image sucessfully Downloaded: ',quesIds[0])
    else:
        print('Image Couldn\'t be retreived')
    if ques2Img.status_code == 200:
        ques2Img.raw.decode_content = True
        with open(folderPath+"/q2-"+quesIds[1],'wb') as f:
            shutil.copyfileobj(ques2Img.raw, f)
        print('Image sucessfully Downloaded: ',quesIds[1])
    else:
        print('Image Couldn\'t be retreived')
    if ques3Img.status_code == 200:
        ques3Img.raw.decode_content = True
        with open(folderPath+"/q3-"+quesIds[2],'wb') as f:
            shutil.copyfileobj(ques3Img.raw, f)
        print('Image sucessfully Downloaded: ',quesIds[2])
    else:
        print('Image Couldn\'t be retreived')

