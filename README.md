# Hrum-Bot
Hrum Bot that mines hrum cookies <br>
Link: https://t.me/hrummebot/game?startapp=ref761561340

# Requirements
**Python 3.10 is required**

# Installing
Clone the repository
```shell
git clone git@github.com:Cherimolah/Hrum-Bot.git
cd Hrum-Bot
```
Copy the `.env` file and edit it. Use API_ID and API HASH from here https://my.telegram.org/apps
```shell
cp .env-sample .env
nano .env
```

| Setting                 | Description                                                                                           |
|-------------------------|-------------------------------------------------------------------------------------------------------|
| API_ID                  | api_id your app                                                                                       |
| API_HASH                | api_hash your app                                                                                     |
 | ENTRY_TIMEOUT           | Time (seconds) that bot will reentry in account and looking for more cookies<br/>Default: [3600,7200] |
| AUTO_CLAIM_DAILY_REWARD | Auto claim daily reward. True/False. Default True                                                     |
| AUTO_CLAIM_RIDDLE       | True/False, default True                                                                              |

Create the virtual environment
```shell
python -m venv venv
venv\Scripts\activate # For Windows
source venv/bin/activate # For Linux
pip install -r requirements.txt
```

# Run the bot

```shell
python main.py
```
You can use the `-a` or `-action` to choose the option
```shell
python main.py -a 2 # Run all sessions
```

# How to use query
Open and auth in telegram web on your PC. Press F12 to open the developer console. Find the "iframe" tag and copy from 
url between #tgWebAppData= and &tgWebAppVersion= <br>
Then create a session choosing query data
![](https://github.com/Cherimolah/Hrum-Bot/blob/master/query_data.gif)
