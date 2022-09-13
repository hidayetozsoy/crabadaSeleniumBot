import time, requests, json, os, sys
sys.path.append((os.path.dirname(__file__)))
from random import randint
from web3 import Web3 
from web3.middleware import geth_poa_middleware
from web3.exceptions import ContractLogicError
from consts import *
from config import *

#returns string hex number without '0x'
def Hex(num):
    return str(hex(num))[2:]

#returns string completed to 64 characters using 0 to the left
def zeroHex(num):
    return Hex(num).rjust(64,"0")

#prints new line and given texts
def printn(*text):
    print("\n", *text)

#prints straight line
def printLine():
    printn(40*"-")

#prints how many seconds will be slept. then sleeps
def sleepy(secs):
    printn(f"Sleeping {secs} secs...")
    time.sleep(secs)

#sends transaction from given address with given dataInput, sends type2 EIP-1559 transaction.
def sendTx(address, dataInput="", value=0):
    w3 = Web3(Web3.HTTPProvider(RPC_URL))
    w3.middleware_onion.inject(geth_poa_middleware, layer=0)
    account = w3.eth.account.from_key(PRIVATE_KEYS[address])
    nonce = w3.eth.getTransactionCount(account.address)
    rawTransaction = {
            "chainId" : hex(CHAIN_ID),
            "from": address,
            "maxFeePerGas": GAS_PRICE_LIMIT,
            "maxPriorityFeePerGas":MAX_PRIORITY_FEE_PER_GAS,
            "gas": GAS_LIMIT, 
            "to": CONTRACT_ADDRESS,
            "value": value,
            "data" : dataInput,
            "nonce" : nonce,
            "type":2,
        } 
    printn("Sending EIP-1559 tx...")
    try:
        gas_estimate = w3.eth.estimate_gas(rawTransaction) #checks if the contract will throw error.
    except ContractLogicError as e:
        printn(f"Tx is expected to be fail. Not sending...\n{e}")
        return
    signedTxn = account.sign_transaction(rawTransaction) 
    w3.eth.send_raw_transaction(signedTxn.rawTransaction) 
    printn("EIP-1559 tx sent...")
    sleepy(10)

def getTeamFactions():
    factions = list()
    for address in PRIVATE_KEYS.keys():
        teamsUrl = f"https://idle-game-api.crabada.com/public/idle/teams?user_address={address}"
        teams = requests.get(teamsUrl, headers=HEADERS, timeout=10).json()["result"]["data"]
        if teams is None:
            return False
        for team in teams:
            faction = team["faction"]
            battlePoint = team["battle_point"]
            info = (faction, battlePoint)
            if info not in factions and battlePoint > 500:
                factions.append(info)
    return factions    

#gets teams data of the address
def getTeamsData(address):
    teamsUrl = f"https://idle-game-api.crabada.com/public/idle/teams?user_address={address}&page=1&limit=10"
    printn("Getting team data...")
    teamsData = requests.get(teamsUrl,headers=HEADERS, timeout=10).json()["result"]["data"]
    return teamsData 

#checks if given factions and points are attackable
def isAttackable(attackFaction, defenseFaction, attackPoint, defensePoint):
    if attackFaction == "NO_FACTION":
        if defenseFaction == "NO_FACTION":
            if attackPoint > defensePoint:
                return True
            return False
        if attackPoint * 0.965 > defensePoint:
            return True
        return False
    if defenseFaction == "NO_FACTION":
        if defensePoint * 0.935 < attackPoint:
            return True
        return False
    if defenseFaction in ADVANTAGES[attackFaction]:
        if defensePoint*0.935 < attackPoint:
            return True
        return False
    if attackFaction in ADVANTAGES[defenseFaction]:
        if attackPoint*0.925 > defensePoint:
            return True
        return False
    if attackPoint > defensePoint:
        return True
    return False

#checks if the last x mines of given address are not reinforced. x can be configured from config.py
def checkAttackableMineHistory(address):
    mineHistoryUrl = f"https://idle-game-api.crabada.com/public/idle/mines?user_address={address}&page=1&status=close&limit={NON_REINFORCED_GAME_LIMIT}"
    mineHistory = requests.get(mineHistoryUrl, headers=HEADERS, timeout=10).json()["result"]["data"]
    
    for mine in mineHistory:
        round = mine["round"]
        if round != 0:
            return False
    return True

#creates a random address.
def randomAddressCreator():
    address = "0x"
    for i in range(10):
        num = randint(4096, 65535)
        address += hex(num)[2:]
    return address

#checks if mine is started more than 1 hour ago
def isSafe(mineStartTime):
    now = time.time()
    if now - mineStartTime > 3500:
        return True
    return False

#checks if mine is attacked
def isMineAttacked(mineId):
    mineUrl = f"https://idle-game-api.crabada.com/public/idle/mine/{mineId}"
    mine = requests.get(mineUrl, headers=HEADERS, timeout=10).json()["result"]
    attackTeamId = mine["attack_team_id"]
    mineStartTime = mine["start_time"]
    if isSafe(mineStartTime):
        return True
    if attackTeamId:
        return True
    return False

#checks if game is settled
def isSettled(gameId):
    mineUrl = f"https://idle-game-api.crabada.com/public/idle/mine/{str(gameId)}" 
    mine = requests.get(mineUrl, headers= HEADERS).json()
    process = mine["result"]["process"]
    lastProcessAction = process[-1]["action"]
    if lastProcessAction == "settle" or lastProcessAction == "create-game":
        return True
    return False

def writeMineToData(mineId, info, data):
    dataPath = os.path.dirname(os.path.realpath(__file__)) + f"/attackable{data}.json"
    with open(dataPath, "r") as file:
        try:
            attackable = json.load(file)
        except json.JSONDecodeError:
            attackable = {}
        if str(mineId) in attackable:
            printn(mineId, f"already in data. Found Attackable {data} Mines: {len(attackable)+1}")
            return
        with open(dataPath, "w") as file:
            printn(mineId, f"added to data. Found Attackable {data} Mines: {len(attackable)+1}")
            attackable[mineId] = info
            file.write(json.dumps(attackable))

#deletes mine from data
def delMineFromData(mineId, data):
    dataPath = os.path.dirname(os.path.realpath(__file__)) + f"/attackable{data}.json"
    with open(dataPath, "r") as file:
        try:
            foundMines = json.load(file)
        except json.JSONDecodeError:
            return
    if str(mineId) in foundMines:
        del foundMines[str(mineId)]
        printn(mineId, "deleted")
        with open(dataPath, "w") as file:
            file.write(json.dumps(foundMines))

def delSafeMines():
    for data in ["WithHistory", ""]:
        dataPath = os.path.dirname(os.path.realpath(__file__)) + f"/attackable{data}.json"
        with open(dataPath, "r") as file:
            try:
                foundMines = json.load(file)
            except json.JSONDecodeError:
                return
        for mine in foundMines.keys():
            if isSafe(foundMines[mine]["startTime"]):
                delMineFromData(mine, data)

#returns attack point and defense point of given game id
def getPoints(gameId):
    gameData = requests.get(f"https://idle-game-api.crabada.com/public/idle/mine/{gameId}", headers=HEADERS, timeout=10).json()["result"]
    attackTeamFaction, defenseTeamFaction, attackPoint, defensePoint, attackTeamMembers, defenseTeamMembers = gameData["attack_team_faction"], gameData["defense_team_faction"], gameData["attack_point"], gameData["defense_point"], gameData["attack_team_members"], gameData["defense_team_members"]
    defensePurePoint, attackPurePoint= 0,0
    for member in defenseTeamMembers:
        crabAttackPoint = member["hp"] + member["armor"] + member["damage"] 
        attackPurePoint += crabAttackPoint
    for member in attackTeamMembers:
        crabAttackPoint = member["hp"] + member["armor"] + member["damage"] 
        defensePurePoint += crabAttackPoint
    if defenseTeamFaction in ADVANTAGES[attackTeamFaction]:
        disadvantagePoint = int(defensePurePoint * 0.07)
        defensePoint -= disadvantagePoint
    if attackTeamFaction in ADVANTAGES[defenseTeamFaction]:
        disadvantagePoint = int(attackPurePoint * 0.07)
        attackPoint -= disadvantagePoint
    return (attackPoint, defensePoint)

#returns available team with 0 looting point. 
def getAvailableMineTeam(address):
    teams = getTeamsData(address)
    for team in teams:
        status, battlePoint, lootingPoint, teamId= team["status"], team["battle_point"], team["looting_point"], team["team_id"]
        if status == "AVAILABLE" and battlePoint > 500 and lootingPoint == 0:
            return teamId
    return None

def getTeamsInfo(address):
    availableTeamsUrl = f"https://idle-game-api.crabada.com/public/idle/teams?user_address={address}&is_team_available=1"
    teamsData = requests.get(availableTeamsUrl, headers=HEADERS, timeout=10).json()["result"]["data"]
    if teamsData is None:
        return False
    teamsInfo = dict()
    for team in teamsData :
        if team["looting_point"] > 0:
            teamId = team["team_id"]
            attackFaction, attackPoint = team["faction"], team["battle_point"]
            teamsInfo[teamId] = {"faction": attackFaction, "attackPoint": attackPoint}
    return teamsInfo

#starts game with given team id
def startGame(address, teamId):
    printn(f"Starting game with team {teamId}")
    dataInput = METHODS["startGame"] + zeroHex(teamId)
    sendTx(address=address, dataInput=dataInput)

#closes game if it's settled. if not, settles first.
def closeGame(address, gameId):
    printn(f"Closing game id {gameId}")
    if not isSettled(gameId):
        printn(f"game {gameId} is not settled.")
        settle(address=address, game=gameId)
    dataInput = METHODS["closeGame"] + zeroHex(gameId)
    sendTx(address=address, dataInput=dataInput)

#settles given team's current game
def settle(address, gameId):
    printn("Settling...") 
    dataInput = METHODS["settle"] + zeroHex(gameId)
    sendTx(address=address, dataInput=dataInput)

def sendAttackTx(address, game):
    gameId, teamId, expireTime, signature= int(game["game_id"]), int(game["team_id"]), int(game["expire_time"]), game["signature"]
    lastPart, signaturePart1, signaturePart2 = parseSignature(signature)
    dataInput = METHODS["attack"] + zeroHex(gameId) + zeroHex(teamId) + zeroHex(expireTime) + zeroHex(128) + zeroHex(65) + signaturePart1 + signaturePart2 + lastPart.ljust(64,"0")
    sendTx(address=address, dataInput=dataInput)

def getLatestGameAttack(address, teamId):
    teamsUrl = f"https://idle-game-api.crabada.com/public/idle/teams?user_address={address}&page=1&limit=10"
    teams = requests.get(teamsUrl, headers=HEADERS, timeout=10).json()["result"]["data"]
    for team in teams:
        if team["team_id"] == teamId:
            latestGameAttack = team["latest_game_attack"]
            sendAttackTx(address=address, game=latestGameAttack)

def parseSignature(signature):
    lastPart = signature[-2:]
    signature = signature[2:-2]
    signaturePart1 = signature[:64]
    signaturePart2 = signature[64:]
    return lastPart, signaturePart1, signaturePart2