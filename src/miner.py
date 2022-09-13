import time, requests, sys, os
sys.path.append((os.path.dirname(__file__)))
from utils.funcs import *
from utils.consts import *

#checks all teams. 
def checkGames():
    printn("Checking games...")
    games = requests.get(f"https://idle-game-api.crabada.com/public/idle/mines?user_address={ADDRESS}&page=1&status=open&limit=8", headers=HEADERS, timeout=10).json()["result"]["data"]
    for game in games:
        now = time.time()
        gameEndTime, gameId, lastProcess, round, teamId = game["end_time"], game["game_id"], game["process"][-1], game["round"], game["team_id"]
        lastProcessAction, lastProcessTime = lastProcess["action"], lastProcess["transaction_time"]
        timeForMove = 1800 - (now - lastProcessTime)
        if gameEndTime + 10 < now:
            closeGame(address=ADDRESS, gameId=gameId)
            continue
        if (round == 0 or round == 2) and timeForMove > 0 and lastProcessAction != "settle":
            reinforce(gameId)
        if round == 4:
            printn(f"Game Finished... Game Id: {gameId} Team Id: {teamId}")

#reinforces with mine point > 80, less then 10 TUS.
def reinforce(gameId):
    hireUrl = f"https://idle-game-api.crabada.com/public/idle/crabadas/lending?orderBy=time_point&order=desc&page=1&limit=99"
    crabs = requests.get(hireUrl, headers=HEADERS, timeout=10).json()["result"]["data"]
    for crab in crabs[10:]:
        crabId, minePoint, borrowPrice, battlePoint = crab["crabada_id"], crab["mine_point"], crab["price"], crab["battle_point"]
        if minePoint >= 80 and borrowPrice < 10 * pow(10,18):
            break
    printn(f"Selected crab -> Bp:{battlePoint}, Id:{crabId}, Price: {borrowPrice/pow(10,18)}")
    dataInput = METHODS["reinforceDefense"] + zeroHex(gameId) + zeroHex(crabId) + zeroHex(borrowPrice)
    sendTx(address=ADDRESS, dataInput=dataInput, value=int(borrowPrice))

def main():
    global ADDRESS
    while True:
        try:   
            for address in PRIVATE_KEYS.keys():
                ADDRESS = address
                printn(address)
                checkGames()
                availableTeam = getAvailableMineTeam(ADDRESS)
                if availableTeam:
                    startGame(address=ADDRESS, teamId=availableTeam)
                printLine()
            printLine()
            sleepy(30)
        except Exception as e:
            printn(f"Exception: {e}")
            sleepy(60)

if __name__ == "__main__":
    main()
