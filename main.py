import os, shutil, sys
from time import sleep
from src.utils.config import ADDRESSES

SUB_PATH = "src/chromeProfiles/"
MAIN_PATH = os.path.dirname(__file__)

def closeTerminals():
    os.system('''killall "Terminal" ''')

def checkSubSrc():
    for address in ADDRESSES.keys():
        addressProfilePath = SUB_PATH + address
        if not os.path.isdir(addressProfilePath):
            print(address, "sub source created.")
            defaultSrcPath = SUB_PATH + "default"
            shutil.copytree(defaultSrcPath, addressProfilePath)

def deleteSubSrcs():
    addresses = os.listdir(SUB_PATH)
    for address in addresses:
        if address == ".DS_Store" or address == "default":
            continue
        shutil.rmtree(SUB_PATH+address)

def runCommand(command):
    os.system( f'''/usr/bin/osascript -e  'tell application "Terminal" to do script with command "{command}"' ''')

def runMiner():
    command = f"cd {MAIN_PATH}/src && python3 miner.py"
    runCommand(command)

def runLooter():
    command = f"cd {MAIN_PATH}/src && python3 looter.py"
    runCommand(command)

def runMineFinder():
    command = f"cd {MAIN_PATH}/src && python3 mineFinder.py"
    runCommand(command)

def runSeleniums():
    for address in ADDRESSES.keys():
        command = f"cd {MAIN_PATH}/src/ && python3 seleniumAttacker.py {address}"
        runCommand(command)
        sleep(10)
   
def main():
    closeTerminals()
    sleep(5)
    checkSubSrc()
    runMiner()
    sleep(3)
    runLooter()
    sleep(3)
    runMineFinder()
    sleep(3)
    runSeleniums()

def run():
    while True:
        main()
        sleep(6*3600)

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "update":
        deleteSubSrcs()
    run()
