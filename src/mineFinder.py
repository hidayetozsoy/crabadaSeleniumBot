import time, requests, sys, os
sys.path.append((os.path.dirname(__file__)))
from utils.funcs import *

def mineFinder():
    printn("Looking for mines...")
    address = randomAddressCreator()
    totalMinesUrl = f"https://idle-game-api.crabada.com/public/idle/mines?page=1&status=open&looter_address={address}&can_loot=1&limit=100"
    totalPagesData= requests.get(totalMinesUrl, headers=HEADERS, timeout=10)
    totalPages = totalPagesData.json()["result"]["totalPages"]
    for page in range(1, totalPages+1):
        printn(f"Page: {page}")
        minesUrl = f"https://idle-game-api.crabada.com/public/idle/mines?page={page}&status=open&looter_address={address}&can_loot=1&limit=100"
        minesData = requests.get(minesUrl, headers=HEADERS, timeout=10)
        mines = minesData.json()["result"]["data"]
        mineNum = 0
        stop = False
        for mine in mines:
            mineNum += 1
            if mineNum % 10 == 0:
                printn(f"%{mineNum}")
            if page == 1 and mineNum < 32:
                continue
            mineStartTime, mineId, mineStartTime, defenseFaction, defenseAttackPoint, minerAddress = mine["start_time"], mine["game_id"], mine["start_time"], mine["faction"], mine["defense_point"], mine["owner"]
            if isSafe(mineStartTime):
                stop = True
                break
            for faction in factions: #faction = (faction, battlePoint)
                attackFaction, attackPoint= faction[0], faction[1]
                if isAttackable(attackFaction, defenseFaction, attackPoint, defenseAttackPoint):
                    info ={
                        "page":page, 
                        "defenseFaction":defenseFaction, 
                        "defenseAttackPoint":defenseAttackPoint,
                        "startTime":mineStartTime
                        }  
                    if checkAttackableMineHistory(minerAddress):
                        writeMineToData(mineId, info, "WithHistory")
                        break
                    else:
                        writeMineToData(mineId, info, "")
                        break
            time.sleep(0.3)
        if stop:
            printn("mines finished.")
            break 

def main():
    global factions
    while True:
        try:
            delSafeMines()
            factions = getTeamFactions()
            if factions:
                mineFinder()
            else:
                Exception("There is no suitable team in any account.")
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            printn(exc_type, fname, f"line:{exc_tb.tb_lineno}")
            sleepy(120)

if __name__ == "__main__":
    main() 
