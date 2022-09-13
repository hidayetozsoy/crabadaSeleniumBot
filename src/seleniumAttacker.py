import time, os, requests, fuckit, sys
from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from utils.config import ADDRESSES, METAMASK_PASSWORD
from utils.imageDownloader import downloadMainImg, downloadQues
from utils.captchaResolver import resolveCaptcha
from utils.consts import *
from utils.mineChooser import *

def openChrome():
    global driver, mainPage
    chromeProfilePath = f"chromeProfiles/{ADDRESS}"
    service = Service(ChromeDriverManager().install())
    chromeOptions = Options()
    chromeOptions.add_argument(f'user-data-dir={chromeProfilePath}')
    chromeOptions.add_argument("--profile-directory=Default")    
    chromeOptions.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(
        options=chromeOptions, 
        service = service,
    )

    mainPage = driver.current_window_handle

def closeChrome():
    os.system("killall -9 'Google Chrome'")

def openMetamask():
    try:
        print("opening metamask")
        driver.get(f"{METAMASK_HOME_URL}#unlock")
        waitAndSendKeys("/html/body/div[1]/div/div[3]/div/div/form/div/div/input", METAMASK_PASSWORD)
        waitAndClick("/html/body/div[1]/div/div[3]/div/div/button")
        metamaskMainPageConfirmButton()
        print("metamask opened")
    except:
        pass

def clickByXpath(xpath, sleepTime=1):
    driver.find_element(by=By.XPATH, value=xpath).click()
    sleep(sleepTime)

def clickBySelector(selector, sleepTime=1):
    driver.find_element(by=By.CSS_SELECTOR, value=selector).click()
    sleep(sleepTime)

def waitAndSendKeys(xpath, *keys):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath))).send_keys(keys)

def waitAndClick(xpath):
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.XPATH, xpath))).click()

def sendKeysByXpath(xpath, *keys, sleepTime=0.1):
    driver.find_element(by=By.XPATH, value=xpath).send_keys(*keys)
    sleep(sleepTime)

def clickByAltWay(xpath, sleepTime=2.5):
    element = driver.find_element(by=By.XPATH, value=xpath)
    driver.execute_script("arguments[0].click();", element)
    sleep(sleepTime)

def switchToMetamask(): 
    for handle in driver.window_handles:
        if handle != mainPage:
            metamaskPage = handle
            driver.switch_to.window(metamaskPage)

def switchToMainPage():
    driver.switch_to.window(mainPage)

def changeAccountOnMetamask(accountNum: int):
    openMetamask()
    metamaskMainPageConfirmButton()
    metamaskMainPageSignButton()
    sleepy(3)     
    clickByAltWay("/html/body/div[1]/div/div[1]/div/div[2]/div[2]/div", 0.3)
    clickByAltWay(f"/html/body/div[1]/div/div[3]/div[4]/div[3]/div[{accountNum}]", 0.3)

def goToPageNum(pageNum):
    sendKeysByXpath("//*[@id='root']/div/div/section/main/div[1]/ul/li[1]/input", Keys.BACKSPACE, Keys.BACKSPACE, Keys.BACKSPACE, pageNum, Keys.ENTER,sleepTime=2)

def goToNextPage():
    clickByAltWay("/html/body/div/div/div/section/main/div[1]/ul/li[4]/div/button/span")

def goToPreviousPage(): 
    clickByAltWay("/html/body/div/div/div/section/main/div[1]/ul/li[3]/div/button/span")

def checkMineIdInPage(selectedMineId):
    order = 0
    for xpath in MINE_XPATHS:
        if selectedMineId == int(driver.find_element(by=By.XPATH, value=xpath[0]+xpath[1]).text.split()[1]):
            return (True, order)
        order += 1
    return (False, -1)

def isAccountAvailable():
    teamsUrl = f"https://idle-game-api.crabada.com/public/idle/teams?user_address={ADDRESS}&page=1&limit=10"
    teams = requests.get(teamsUrl, headers=HEADERS).json()["result"]["data"]
    for team in teams:
        status, battlePoint, lootingPoint= team["status"], team["battle_point"], team["looting_point"]
        print(ADDRESS, status, battlePoint)
        if status == "AVAILABLE" and battlePoint > 500 and not("latest_game_attack" in team) and lootingPoint != 0:
            return int(ADDRESSES[ADDRESS])
    return False

@fuckit
def clickLogOutButton():
    logOutButtonXpath = "/html/body/div[2]/div/div[2]/div/div[2]/div/div/div[2]/button"   
    clickByAltWay(logOutButtonXpath, 3)

@fuckit  
def connectWalletButton():
    logOutButtonXpath = "/html/body/div[3]/div/div[2]/div/div[2]/div/div/div[2]/button"   
    clickByAltWay(logOutButtonXpath, 3)

@fuckit
def clickSignButton():
    connectButtonXpath = "/html/body/div[1]/div/div[2]/div/div[3]/button[2]"
    switchToMetamask()
    clickByAltWay(connectButtonXpath,3)
    switchToMainPage()
    driver.get(START_LOOTING_URL)

def clickConfirmButton():
    confirmButtonXpath = "/html/body/div[1]/div/div[2]/div/div[4]/div[3]/footer/button[2]"
    confirmButtonAltXpath = "/html/body/div[1]/div/div[2]/div/div[5]/div[3]/footer/button[2]"
    try:
        clickByAltWay(confirmButtonXpath, 5)
        switchToMainPage()
    except NoSuchElementException:
        try:
            clickByAltWay(confirmButtonAltXpath, 5)
            switchToMainPage()
        except NoSuchElementException:
            pass
    try:
        switchToMetamask()
        clickByAltWay(confirmButtonXpath, 5)
        switchToMainPage()
    except:
        try:
            switchToMetamask()
            clickByAltWay(confirmButtonAltXpath, 5)
            switchToMainPage()
        except:
            pass

def checkManageTeamButton():
    try:
        manageTeamButtonXpath = driver.find_element(by=By.XPATH, value="/html/body/div[4]/div/div[2]/div/div[2]/div/div/div[2]/button")
        return True
    except NoSuchElementException:
        try:
            manageTeamButtonCss = driver.find_element(by=By.CSS_SELECTOR, value="body > div:nth-child(9) > div > div.ant-modal-wrap.ant-modal-centered > div > div.ant-modal-content > div > div > div:nth-child(4) > button")
            return True
        except NoSuchElementException:
            return False

def isAttacked():
    try:
        driver.find_element(by=By.CSS_SELECTOR, value="body > div:nth-child(8) > div > div.ant-modal-wrap.ant-modal-centered > div > div.ant-modal-content > div > div > div:nth-child(4) > button").click()
        return True
    except NoSuchElementException:
        return False
    
@fuckit
def metamaskMainPageConfirmButton():
    switchToMetamask()
    clickConfirmButton()
    clickByAltWay("/html/body/div[1]/div/div[3]/div/div[4]/div[3]/footer/button[2]")
    clickByAltWay("/html/body/div[1]/div/div[3]/div/div[5]/div[3]/footer/button[2]")

@fuckit
def metamaskMainPageSignButton():
    clickByAltWay("/html/body/div[1]/div/div[3]/div/div[3]/button[2]")

@fuckit
def selectButton():
    clickByAltWay("/html/body/div[2]/div/div[2]/div/div[2]/div/div[3]/div/button", 1.5)
    clickBySelector("body > div:nth-child(6) > div > div.ant-modal-wrap.ant-modal-centered > div > div.ant-modal-content > div > div.modal-footer > div > button", 1.5)

def lookForCaptcha():
    now = time.time()
    expireTime = now + 10
    while expireTime > now:
        now = time.time()
        try:
            sleep(1)
            captcha = driver.find_element(by=By.CSS_SELECTOR, value = "body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_boxShow.geetest_freeze_wait > div.geetest_box_wrap > div.geetest_box > div.geetest_container > div > div > div.geetest_window > div.geetest_bg")
            captchaStyle = captcha.get_attribute("style")             
            captchaId = captchaStyle.split("/")[-1].split(".")[0]
            captchaUrl = captchaStyle.split('"')[-2]
            print("captcha id:", captchaId)
            q1 = driver.find_element(by=By.CSS_SELECTOR, value = "body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_boxShow.geetest_freeze_wait > div.geetest_box_wrap > div.geetest_box > div.geetest_header > div.geetest_title.geetest_space_between > div.geetest_ques_tips.geetest_ques_back > img:nth-child(1)").get_attribute("src")[27:]
            q2 = driver.find_element(by=By.CSS_SELECTOR, value = "body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_boxShow.geetest_freeze_wait > div.geetest_box_wrap > div.geetest_box > div.geetest_header > div.geetest_title.geetest_space_between > div.geetest_ques_tips.geetest_ques_back > img:nth-child(2)").get_attribute("src")[27:]
            q3 = driver.find_element(by=By.CSS_SELECTOR, value = "body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_boxShow.geetest_freeze_wait > div.geetest_box_wrap > div.geetest_box > div.geetest_header > div.geetest_title.geetest_space_between > div.geetest_ques_tips.geetest_ques_back > img:nth-child(3)").get_attribute("src")[27:]
            return (captchaId, captchaUrl), (q1, q2, q3)
        except NoSuchElementException:
            try:
                sleep(1)
                newCaptcha = driver.find_element(by=By.CSS_SELECTOR, value="body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_freeze_wait.geetest_nextReady > div.geetest_box_wrap > div.geetest_box > div.geetest_container > div > div > div.geetest_window > div.geetest_bg")
                newCaptchaStyle = newCaptcha.get_attribute("style")             
                newCaptchaId = newCaptchaStyle.split("/")[-1].split(".")[0] 
                newCaptchaUrl = newCaptchaStyle.split('"')[-2]
                print("captcha id:", newCaptchaId)
                newQ1 = driver.find_element(by=By.CSS_SELECTOR, value = "body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_freeze_wait.geetest_nextReady > div.geetest_box_wrap > div.geetest_box > div.geetest_header > div.geetest_title.geetest_space_between > div.geetest_ques_tips.geetest_ques_back > img:nth-child(1)").get_attribute("src")[27:]
                newQ2 = driver.find_element(by=By.CSS_SELECTOR, value = "body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_freeze_wait.geetest_nextReady > div.geetest_box_wrap > div.geetest_box > div.geetest_header > div.geetest_title.geetest_space_between > div.geetest_ques_tips.geetest_ques_back > img:nth-child(2)").get_attribute("src")[27:]
                newQ3 = driver.find_element(by=By.CSS_SELECTOR, value = "body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_freeze_wait.geetest_nextReady > div.geetest_box_wrap > div.geetest_box > div.geetest_header > div.geetest_title.geetest_space_between > div.geetest_ques_tips.geetest_ques_back > img:nth-child(3)").get_attribute("src")[27:]
                return (newCaptchaId, newCaptchaUrl), (newQ1, newQ2, newQ3)
            except NoSuchElementException:
                if isAttacked():
                    return False
                else:
                    return None

def clickRefreshCaptcha():
    try:
        refreshCaptcha = "body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_boxShow.geetest_freeze_wait > div.geetest_box_wrap > div.geetest_box > div.geetest_footer > div.geetest_footer_left > a.geetest_refresh"
        refreshCaptchaElement= driver.find_element(by=By.CSS_SELECTOR, value=refreshCaptcha)
        refreshCaptchaElement.click()
    except NoSuchElementException:
        try:
            newRefreshCaptcha = "body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_freeze_wait.geetest_nextReady > div.geetest_box_wrap > div.geetest_box > div.geetest_footer > div.geetest_footer_left > a.geetest_refresh"
            newRefreshCaptchaElement= driver.find_element(by=By.CSS_SELECTOR, value=newRefreshCaptcha)
            newRefreshCaptchaElement.click()
        except Exception as e:
            print(e)

def tryResolveCaptcha(mainImg, ques):
    mainImgId, mainImgUrl = mainImg[0], mainImg[1]
    downloadMainImg(mainImgId, mainImgUrl)
    downloadQues(ques, mainImgId)
    captchaResolveResult = resolveCaptcha(mainImgId)
    if captchaResolveResult:
        return captchaResolveResult
    return False

def solveCaptcha():
    while True:
        try:
            captcha = driver.find_element(by=By.CSS_SELECTOR, value = "body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_boxShow.geetest_freeze_wait > div.geetest_box_wrap > div.geetest_box > div.geetest_container > div > div > div.geetest_window > div.geetest_bg")
            suitableCaptcha = searchSuitableCaptcha()
            if suitableCaptcha:
                clickCaptcha(suitableCaptcha)
        except NoSuchElementException:
            try:
                newCaptcha = driver.find_element(by=By.CSS_SELECTOR, value = "body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_freeze_wait.geetest_nextReady > div.geetest_box_wrap > div.geetest_box > div.geetest_container > div > div > div.geetest_window > div.geetest_bg")
                newSuitableCaptcha = searchSuitableCaptcha()
                if newSuitableCaptcha:
                    clickCaptcha(newSuitableCaptcha)
            except NoSuchElementException:
                break

def searchSuitableCaptcha():
    now = time.time()
    expireTime = now + 30
    while expireTime > now:
        now = time.time()
        mainImg, ques = lookForCaptcha()
        if mainImg:
            captchaResolveResult = tryResolveCaptcha(mainImg, ques)
            if captchaResolveResult:
                return captchaResolveResult
            else:
                clickRefreshCaptcha()
                sleep(3)
    return None

def searchMine(selectedMine):
    for tryCount in range(5):
        firstMineInPage = int(driver.find_element(by=By.XPATH, value="/html/body/div/div/div/section/main/div[1]/div[2]/div[2]/div/div[2]/div[1]/div[1]/div/div[2]/div[1]/h5").text.split()[1])
        lastMineInPage = int(driver.find_element(by=By.XPATH, value="/html/body/div/div/div/section/main/div[1]/div[2]/div[2]/div/div[2]/div[4]/div[2]/div/div[2]/div[1]/h5").text.split()[1])
        if selectedMine[0] < lastMineInPage:
            goToNextPage()
            continue
        elif selectedMine[0] > firstMineInPage:
            goToPreviousPage()
            continue
        else:
            checkedMines = checkMineIdInPage(selectedMine[0])
            if checkedMines[0]:
                clickByAltWay(MINE_XPATHS[checkedMines[1]][0]+"/div/div[3]/div/button")
                clickByAltWay(f"/html/body/div[2]/div/div[2]/div/div[2]/div/div[2]/div[3]/div/div[1]/div[1]/div/div[{selectedMine[2]}]")
                selectButton()
                return True  
            else:
                return False
                
def clickCaptcha(captchaPositions):
    print("clicking captcha")
    que1 = captchaPositions["1"]
    que2 = captchaPositions["2"]
    que3 = captchaPositions["3"]
    try:
        captcha = driver.find_element(by=By.CSS_SELECTOR, value = "body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_boxShow.geetest_freeze_wait > div.geetest_box_wrap > div.geetest_box > div.geetest_container > div > div > div.geetest_window > div.geetest_bg")
    except NoSuchElementException:
        captcha = driver.find_element(by=By.CSS_SELECTOR, value="body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_freeze_wait.geetest_nextReady > div.geetest_box_wrap > div.geetest_box > div.geetest_container > div > div > div.geetest_window > div.geetest_bg")
    ac = ActionChains(driver)                                  
    xOffset = 150
    yOffset = 100
    sleep(2)
    ac.move_to_element_with_offset(captcha, 0, 0).move_by_offset(que1["x"]-xOffset, que1["y"]-yOffset).click().perform()
    sleep(0.5)
    ac.move_to_element_with_offset(captcha, 0, 0).move_by_offset(que2["x"]-xOffset, que2["y"]-yOffset).click().perform()
    sleep(0.5)
    ac.move_to_element_with_offset(captcha, 0, 0).move_by_offset(que3["x"]-xOffset, que3["y"]-yOffset).click().perform()
    sleep(1)
    try:
        submitBtn = driver.find_element(by=By.CSS_SELECTOR, value = "body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_boxShow.geetest_freeze_wait > div.geetest_box_wrap > div.geetest_box > div.geetest_container > div > div > div.geetest_submit")
    except NoSuchElementException:
        submitBtn = driver.find_element(by=By.CSS_SELECTOR, value = "body > div.geetest_captcha.geetest_bind.geetest_customTheme.geetest_freeze_wait.geetest_nextReady > div.geetest_box_wrap > div.geetest_box > div.geetest_container > div > div > div.geetest_submit")
        
    submitBtn.click()

def openCrabada():  
    driver.get(START_LOOTING_URL) #go to crabada
    sleep(5)
    clickLogOutButton()
    connectWalletButton() 
    clickSignButton()
    driver.get(START_LOOTING_URL) #go to crabada

def attack():
    openCrabada()
    now = time.time()
    expireTime = now + 300
    stop = False
    while expireTime > now and not stop:
        now = time.time()
        teamsInfo = getTeamsInfo(ADDRESS)
        try:
            selectedMine = chooseMine(teamsInfo, data="WithHistory")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            printn(exc_type, f"line:{exc_tb.tb_lineno}")
            sleepy(120)
            return 
        if not selectedMine:
            selectedMine = chooseMine(teamsInfo, data="")
            if not selectedMine:
                sleepy(30)
                return
        goToPageNum(selectedMine[1])
        while True:
            sleep(1)
            if checkManageTeamButton():
                print("there is no available team in this account")
                stop = True
                break
            if not searchMine(selectedMine):
                print("mine couldn't found")
                break
            stop = True

            solveCaptcha()
            
            sleep(9)

            if isAttacked():
                print("mine is being attacked by someone else")
                driver.get(START_LOOTING_URL)
                stop = True
                break

            clickConfirmButton()
            switchToMainPage()
            sleep(6)
            stop = True
            driver.get(START_LOOTING_URL)
            break

def main():
    openChrome()
    openMetamask()
    while True:
        try:
            metamaskMainPageConfirmButton()
            availableAccount = isAccountAvailable()
            if not availableAccount:
                print("no available team...")
                sleepy(20)
                continue
            changeAccountOnMetamask(availableAccount)
            attack()
        except Exception as e:
            print(e.__class__)
            sleep(120)

def run(address):
    global ADDRESS
    ADDRESS = address
    while True:
        try:
            main()
        except Exception as e:
            print(e)
            sleep(10)

if __name__ == "__main__":
    run(sys.argv[1])


