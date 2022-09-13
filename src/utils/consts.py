START_LOOTING_URL = "https://idle.crabada.com/mine/start-looting"
METAMASK_HOME_URL = "chrome-extension://nkbihfbeogaeaoehlefnkodbefgpgknn/home.html"
HEADERS = {
    'authority': 'idle-game-api.crabada.com',
    'accept': 'application/json, text/plain, /',
    'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    'cache-control': 'no-cache',
    'origin': 'https://idle.crabada.com',
    'pragma': 'no-cache',
    'referer': 'https://idle.crabada.com/',
    'sec-fetch-dest': 'empty',
    'sec-fetch-mode': 'cors',
    'sec-fetch-site': 'same-site',
    'sec-gpc': '1',
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.79 Safari/537.36',
}

MINE_XPATHS = [
        ("//*[@id='rc-tabs-0-panel-2']/div[1]/div[1]","/div/div[2]/div[1]/h5"),
        ("//*[@id='rc-tabs-0-panel-2']/div[1]/div[2]","/div/div[2]/div[1]/h5"),
        ("//*[@id='rc-tabs-0-panel-2']/div[2]/div[1]","/div/div[2]/div[1]/h5"),
        ("//*[@id='rc-tabs-0-panel-2']/div[2]/div[2]","/div/div[2]/div[1]/h5"),
        ("//*[@id='rc-tabs-0-panel-2']/div[3]/div[1]","/div/div[2]/div[1]/h5"),
        ("//*[@id='rc-tabs-0-panel-2']/div[3]/div[2]","/div/div[2]/div[1]/h5"),
        ("//*[@id='rc-tabs-0-panel-2']/div[4]/div[1]","/div/div[2]/div[1]/h5"),
        ("//*[@id='rc-tabs-0-panel-2']/div[4]/div[2]","/div/div[2]/div[1]/h5"),
    ]


ADVANTAGES = {
    "LUX":["FAERIE","ORE"],
    "FAERIE":["ORE","ABYSS"],
    "ORE":["ABYSS","TRENCH"],
    "ABYSS":["TRENCH","MACHINE"],
    "TRENCH":["MACHINE","LUX"],
    "MACHINE":["LUX","FAERIE"],
    "NO_FACTION":[],
}

METHODS = {
    "attack":"0x77728f25",
    "settle":"0x312d7bbc",
    "startGame":"0xe5ed1d59",
    "reinforceDefense":"0x08873bfb",
    "closeGame":"0x2d6ef310",
    "reinforceAttack":"0x3dc8d5ce",
    }
