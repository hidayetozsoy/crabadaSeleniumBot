import json, os, sys
sys.path.append((os.path.dirname(__file__)))
from funcs import *
from consts import *

def chooseMine(teamsData: dict, data=""):
    dataPath = os.path.dirname(os.path.realpath(__file__)) + f"/attackable{data}.json"
    with open(dataPath, "r") as file:
        foundMines = json.load(file)
    printn(len(foundMines), f"mines in data {data}")
    if len(foundMines) == 0:
        printn(f"no mines left... {data}")
        return None
    for mineId in foundMines:
        mine = foundMines[mineId]
        mineStartTime = mine["startTime"]
        if isSafe(mineStartTime):
            printn(mineId, "is now safe")
            delMineFromData(mineId, data)
            continue
        defenseFaction = mine["defenseFaction"]
        defenseAttackPoint = mine["defenseAttackPoint"]
        for teamId in teamsData.keys():
            attackFaction = teamsData[teamId]["faction"]
            attackPoint = teamsData[teamId]["attackPoint"]
            if isAttackable(attackFaction, defenseFaction, attackPoint, defenseAttackPoint):
                delMineFromData(mineId, data)
                info = (mineId, teamId)
                printn(f"Mine ID: {info[0]} Team Id: {info[1]}")
                return info
    printn(f"no suitable mine {data}...")

if __name__ == "__main__":
    printn(chooseMine({1: {'faction': 'TRENCH', 'attackPoint': 665}}, data="WithHistory"))