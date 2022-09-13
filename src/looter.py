import time, requests, sys, os
sys.path.append((os.path.dirname(__file__)))
from datetime import timedelta
from utils.funcs import *
from utils.consts import *

#checks for the games reserved but not tx sent
def checkResendAttacks():
    teamsUrl = f"https://idle-game-api.crabada.com/public/idle/teams?user_address={ADDRESS}&page=1&limit=10"
    teams = requests.get(teamsUrl, headers=HEADERS, timeout=10).json()["result"]["data"]
    for team in teams:
        if ("latest_game_attack" in team) and team["status"] == "AVAILABLE":
            game = team["latest_game_attack"]
            now = int(time.time())
            expiredTime = int(game["expire_time"])
            timeLeft = expiredTime - now
            printn(timeLeft, "secs left to resend")
            if timeLeft < 500 and timeLeft > 10:
                sendAttackTx(address=ADDRESS, game=game)

#reinforces with given game id, difference
def reinforce(gameId):
    hireUrl = f"https://idle-game-api.crabada.com/public/idle/crabadas/lending?class_ids[]=4&orderBy=battle_point&order=desc&page=1&limit=100"
    crabs = requests.get(hireUrl,headers=HEADERS, timeout=10).json()["result"]["data"]
    for crab in crabs[15:]:
        crabId, battlePoint, borrowPrice, battlePoint = crab["crabada_id"], crab["battle_point"], crab["price"], crab["battle_point"]
        if crab["battle_point"] == 237 and borrowPrice < 10 * pow(10,18):
            break
    printn(f"Selected crab -> Bp:{battlePoint}, Id:{crabId}, Price: {borrowPrice/pow(10,18)}")
    dataInput = METHODS["reinforceAttack"] + zeroHex(gameId) + zeroHex(crabId) + zeroHex(borrowPrice)
    sendTx(address=ADDRESS, dataInput=dataInput, value=int(borrowPrice))            

#checks open games 
def checkGames():
    checkResendAttacks()
    printn("Checking games...")
    teams = getTeamsData(ADDRESS)
    for team in teams:
        if team["status"] == "LOCK":
            teamId, gameId= team["team_id"], team["game_id"]    
            if not team["game_id"]:
                printn(f"{teamId} Waiting for locked team...")
                continue
            game = requests.get(f"https://idle-game-api.crabada.com/public/idle/mine/{gameId}", headers=HEADERS, timeout=10).json()["result"]
            round, startTime, lastProcess = game["round"], team["game_start_time"], game["process"][-1]
            lastAction, lastProcessTime = lastProcess["action"], lastProcess["transaction_time"]
            now = time.time()
            timeLeft, timeForMove = 3600-(now-startTime), 1800-(now-lastProcessTime)
            if lastAction == "settle":
                printn(f"{teamId} Waiting for locked team...")
                continue
            if (timeForMove < 0 or round == 4): 
                settle(address=ADDRESS, gameId=gameId)
            else:
                if (round == 1 or round == 3) and timeForMove > 5:
                    bp, dp = getPoints(gameId)
                    diff = dp-bp+1
                    if diff > 237:
                        printn("Reinforce diff is too big.")
                        continue
                    printn(f"Reinforce needed... Round: {round} Diff: {diff}")
                    reinforce(gameId)
                else:
                    printn(f"{teamId} Time left until move: {str(timedelta(seconds=1800-(now-lastProcessTime)))[:7]}")
                    printn(f"{teamId} Loot in process, Round: {round}, Time left: {str(timedelta(seconds=timeLeft))[:7]}")
            printLine()

def main():
    global ADDRESS
    while True:
        try:
            for address in PRIVATE_KEYS.keys():
                ADDRESS = address
                printn(address)
                checkGames()
                printLine()
            sleepy(30)
        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            printn(exc_type, f"line:{exc_tb.tb_lineno}")
            sleepy(60)

if __name__ == "__main__":
    main()