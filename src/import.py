import os
import pandas as pd
import tweepy
import re
import string
from textblob import TextBlob
import preprocessor as p
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import pyrebase
import firebase_admin
from firebase_admin import credentials

cred = credentials.Certificate("firebase.json")
firebase_admin.initialize_app(cred)

config = {
  "apiKey": "AIzaSyCQqJ5DsQ7l7S5yP9cY2mIVsZTRtGKUzUE",
  "authDomain": "webhostc3budiman.firebaseapp.com",
  "databaseURL": "https://webhostc3budiman.firebaseio.com",
  "serviceAccount": "firebase.json",
  "storageBucket": "webhostc3budiman.appspot.com"
}

firebase = pyrebase.initialize_app(config)
db = firebase.database()

tweets = db.child("tweets").get()
print(tweets.val())

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

mrt_bersih = "hasil/mrt_bersih.csv"
mrt_kotor = "hasil/mrt_kotor.csv"
mrt = "hasil/mrt.csv"

#Kolom csv nya :
COLS = ['id', 'created_at', 'source', 'original_text','clean_text', 'sentiment','polarity','subjectivity', 'lang',
        'favorite_count', 'retweet_count', 'original_author', 'possibly_sensitive', 'hashtags',
        'user_mentions', 'place', 'place_coord_boundaries']

# Emotikon senang :
emoticons_happy = set([
    ':-)', ':)', ';)', ':o)', ':]', ':3', ':c)', ':>', '=]', '8)', '=)', ':}',
    ':^)', ':-D', ':D', '8-D', '8D', 'x-D', 'xD', 'X-D', 'XD', '=-D', '=D',
    '=-3', '=3', ':-))', ":'-)", ":')", ':*', ':^*', '>:P', ':-P', ':P', 'X-P',
    'x-p', 'xp', 'XP', ':-p', ':p', '=p', ':-b', ':b', '>:)', '>;)', '>:-)',
    '<3'
    ])

# Emotikon sedih
emoticons_sad = set([
    ':L', ':-/', '>:/', ':S', '>:[', ':@', ':-(', ':[', ':-||', '=L', ':<',
    ':-[', ':-<', '=\\', '=/', '>:(', ':(', '>.<', ":'-(", ":'(", ':\\', ':-c',
    ':c', ':{', '>:\\', ';('
    ])

# Emoji :
emoji_pattern = re.compile("["
                           u"\U0001F600-\U0001F64F"  # emoticons
                           u"\U0001F300-\U0001F5FF"  # symbols & pictographs
                           u"\U0001F680-\U0001F6FF"  # transport & map symbols
                           u"\U0001F1E0-\U0001F1FF"  # flags (iOS)
                           u"\U00002702-\U000027B0"
                           u"\U000024C2-\U0001F251"
                           "]+", flags=re.UNICODE)

#semua emoticon dan emoji :
emoticons = emoticons_happy.union(emoticons_sad)


#Buat clean tweet nya :
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
    for page in tweepy.Cursor(api.search, q=keyword,
                              count=5000, lang='id', tweet_mode='extended').pages(50):
        for status in page:
            new_entry = []
            status = status._json
            #print(status)

            #when run the code, below code replaces the retweet amount and
            #no of favorires that are changed since last download.
            if status['created_at'] in df['created_at'].values:
                i = df.loc[df['created_at'] == status['created_at']].index[0]
                if status['favorite_count'] != df.at[i, 'favorite_count'] or \
                   status['retweet_count'] != df.at[i, 'retweet_count']:
                    df.at[i, 'favorite_count'] = status['favorite_count']
                    df.at[i, 'retweet_count'] = status['retweet_count']
                continue

            #data = {"name": "Mortimer 'Morty' Smith"}
            db.child("tweets").push(status)
            #tweepy preprocessing called for basic preprocessing
            # clean_text = p.clean(status['text'])
            #
            # #call clean_tweet method for extra preprocessing
            # filtered_tweet=clean_tweets(clean_text)
            #
            # #pass textBlob method for sentiment calculations
            # blob = TextBlob(filtered_tweet)
            # Sentiment = blob.sentiment
            #
            # #seperate polarity and subjectivity in to two variables
            # polarity = Sentiment.polarity
            # subjectivity = Sentiment.subjectivity
            #
            # #new entry append
            # new_entry += [status['id'], status['created_at'],
            #               status['source'], status['text'],filtered_tweet, Sentiment,polarity,subjectivity, status['lang'],
            #               status['favorite_count'], status['retweet_count']]
            #
            # #to append original author of the tweet
            # new_entry.append(status['user']['screen_name'])
            #
            # try:
            #     is_sensitive = status['possibly_sensitive']
            # except KeyError:
            #     is_sensitive = None
            # new_entry.append(is_sensitive)
            #
            # # hashtagas and mentiones are saved using comma separted
            # hashtags = ", ".join([hashtag_item['text'] for hashtag_item in status['entities']['hashtags']])
            # new_entry.append(hashtags)
            # mentions = ", ".join([mention['screen_name'] for mention in status['entities']['user_mentions']])
            # new_entry.append(mentions)
            #
            # #get location of the tweet if possible
            # try:
            #     location = status['user']['location']
            # except TypeError:
            #     location = ''
            # new_entry.append(location)
            #
            # try:
            #     coordinates = [coord for loc in status['place']['bounding_box']['coordinates'] for coord in loc]
            # except TypeError:
            #     coordinates = None
            # new_entry.append(coordinates)
            #
            # single_tweet_df = pd.DataFrame([new_entry], columns=COLS)
            # df = df.append(single_tweet_df, ignore_index=True)
            # csvFile = open(file, 'a' ,encoding='utf-8')
            # df.to_csv(csvFile, mode='a', columns=COLS, index=False, encoding="utf-8")

#declare keywords as a query for three categories
query_bersih = '#mrtbersih'
query_kotor = '#mrtkotor'
query_netral = '#mrt'

#call main method passing keywords and file path
#write_tweets(query_bersih, mrt_bersih)
#write_tweets(query_kotor, mrt_kotor)
#write_tweets(query_netral, mrt)
