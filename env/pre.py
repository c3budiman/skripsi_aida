import os
import pandas as pd
import tweepy
import re
import string
from textblob import TextBlob
import preprocessor as p
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize

CONSUMER_KEY = "ZU9m0tAFvhHfh8LySOeUDxFCD"
CONSUMER_SECRET = "4i4rulXgdA7WXuhoj6moIQtz95S3DwkGiXzyVBCagM8quNzrmF"
ACCESS_TOKEN = "113829125-VEhtcBGMoi8ZUItOjihIDbDuFePLtrTSRYlIzRs0"
ACCESS_TOKEN_SECRET = "jCIx2GPXqzdemZlja5OvVLDIq5ircLUKw4An1eDHHPM0b"

# auth = OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
# auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
# api = tweepy.API(auth, wait_on_rate_limit=True)

auth = tweepy.OAuthHandler(CONSUMER_KEY, CONSUMER_SECRET)
auth.set_access_token(ACCESS_TOKEN, ACCESS_TOKEN_SECRET)
api = tweepy.API(auth, wait_on_rate_limit=True)

mrt_bersih = "data/mrt_bersih.csv"
mrt_kotor = "data/mrt_kotor.csv"
mrt = "data/mrt.csv"

#columns of the csv file
COLS = ['id', 'created_at', 'source', 'original_text','clean_text', 'sentiment','polarity','subjectivity', 'lang',
        'favorite_count', 'retweet_count', 'original_author', 'possibly_sensitive', 'hashtags',
        'user_mentions', 'place', 'place_coord_boundaries']

#set two date variables for date range
start_date = '2018-10-01'
end_date = '2019-10-31'

# Happy Emoticons
emoticons_happy = set([
    ':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}',
    ':^)', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D',
    '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*', '>:P', ':-P', ':P', 'X-P',
    'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)',
    '<3'
    ])

# Sad Emoticons
emoticons_sad = set([
    ':L', ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<',
    ':-[', ':-<', '=\\', '=/', '>:(', ':(', '>.<', ":'-(", ":'(", ':\\', ':-c',
    ':c', ':{', '>:\\', ';('
    ])

#Emoji patterns
emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)

#combine sad and happy emoticons
emoticons = emoticons_happy.union(emoticons_sad)


#mrhod clean_tweets()
def clean_tweets(tweet):
    stop_words = set(stopwords.words('indonesian'))
    word_tokens = word_tokenize(tweet)

    #after tweepy preprocessing the colon left remain after removing mentions
    #or RT sign in the beginning of the tweet
    tweet = re.sub(r':', '', tweet)
    tweet = re.sub(r'‚Ä¶', '', tweet)
    #replace consecutive non-ASCII characters with a space
    tweet = re.sub(r'[^\x00-\x7F]+',' ', tweet)


    #remove emojis from tweet
    tweet = emoji_pattern.sub(r'', tweet)

    #filter using NLTK library append it to a string
    filtered_tweet = [w for w in word_tokens if not w in stop_words]
    filtered_tweet = []

    #looping through conditions
    for w in word_tokens:
        #check tokens against stop words , emoticons and punctuations
        if w not in stop_words and w not in emoticons and w not in string.punctuation:
            filtered_tweet.append(w)
    return ' '.join(filtered_tweet)
    #print(word_tokens)
    #print(filtered_sentence)

#method write_tweets()
def write_tweets(keyword, file):
    # If the file exists, then read the existing data from the CSV file.
    if os.path.exists(file):
        df = pd.read_csv(file, header=0)
    else:
        df = pd.DataFrame(columns=COLS)
    #page attribute in tweepy.cursor and iteration
    tweet_fulltext = []
    for tweets in tweepy.Cursor(api.search, q=keyword, count=5000, lang='id', tweet_mode='extended').items():
      if tweets.full_text not in tweet_fulltext:
        bersihin = p.clean(tweets.full_text)
        lebih_bersih = clean_tweets(bersihin)
        tweet_fulltext.append(lebih_bersih) #yang ini masukin tweetsnya ke array tweet_fulltext

    df = pd.DataFrame()
    df['tweets'] = tweet_fulltext
    print(df.shape)
    df

    df.to_csv(file)

#declare keywords as a query for three categories
query_bersih = 'mrt bersih'
query_kotor = 'mrt kotor'
query_netral = 'mrt'

#call main method passing keywords and file path
write_tweets(query_bersih, mrt_bersih)
write_tweets(query_kotor, mrt_kotor)
write_tweets(query_netral, mrt)
