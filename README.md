# Crabada Selenium Bot
This is an older version of Crabada Bot I used to use. It was from the times when attack missions required captcha solution.
This bot can handle multiple accounts, solves captchas and attack, even though there is no captchas anymore, it can still work but other bot is way more faster.
It includes miner and looter too, so it's fully automatized.
## Set Up
### Chrome Profile
- Chrome profile should be put into src/chromeProfiles/Default folder.
- It can be found by going 'chrome://version' page in Google Chrome, it is next to Profile path. 
- It should be something like '/Users/hidayetozsoy/Library/Application Support/Google/Chrome/Default',
  - You should copy all the files under '/Users/hidayetozsoy/Library/Application Support/Google/Chrome/', it will include Default folder.
- Paste these files to project under src/chromeProfiles/Default folder.
### Private Keys and Addresses
- Private keys should be put into **config.py** under src/utils directory.
- Addresses should be into **config.py** too, but they must be in the same order with order in Metamask extension.
- You can find more detailed info about getting addresses and private keys at:
  - https://github.com/hidayetozsoy/crabadaBot/blob/main/README.md 
### Run Program 
- You can run program with command:
  - `python3 main.py` 
  
