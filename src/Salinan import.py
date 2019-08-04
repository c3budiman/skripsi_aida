import tweepy
from tweepy import OAuthHandler
import json
import pandas as pd

CONSUMER_KEY = "ZU9m0tAFvhHfh8LySOeUDxFCD"
CONSUMER_SECRET = "4i4rulXgdA7WXuhoj6moIQtz95S3DwkGiXzyVBCagM8quNzrmF"
ACCESS_TOKEN = "113829125-VEhtcBGMoi8ZUItOjihIDbDuFePLtrTSRYlIzRs0"
ACCESS_TOKEN_SECRET = "jCIx2GPXqzdemZlja5OvVLDIq5ircLUKw4An1eDHHPM0b"

auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

tweet_fulltext = []
searchquery = 'mrt bersih'
for tweets in tweepy.Cursor(api.search, q=searchquery, count=5000, lang='id', tweet_mode='extended').items():
  if tweets.full_text not in tweet_fulltext:
    tweet_fulltext.append(tweets.full_text) #yang ini masukin tweetsnya ke array tweet_fulltext

df = pd.DataFrame()
df['tweets'] = tweet_fulltext
print(df.shape)
df

df.to_csv('mrtbersih.csv')
