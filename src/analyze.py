from tweepy import API
from tweepy import Cursor
from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream

from textblob import TextBlob

import akun_twitter

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import re


# # # # TWITTER CLIENT # # # #
class TwitterClient():
    def __init__(self, twitter_user=None):
        self.auth = TwitterAuthenticator().authenticate_twitter_app()
        self.twitter_client = API(self.auth)

        self.twitter_user = twitter_user

    def get_twitter_client_api(self):
        return self.twitter_client

    def get_user_timeline_tweets(self, num_tweets):
        tweets = []
        for tweet in Cursor(self.twitter_client.user_timeline, id=self.twitter_user).items(num_tweets):
            tweets.append(tweet)
        return tweets

    def get_friend_list(self, num_friends):
        friend_list = []
        for friend in Cursor(self.twitter_client.friends, id=self.twitter_user).items(num_friends):
            friend_list.append(friend)
        return friend_list

    def get_home_timeline_tweets(self, num_tweets):
        home_timeline_tweets = []
        for tweet in Cursor(self.twitter_client.home_timeline, id=self.twitter_user).items(num_tweets):
            home_timeline_tweets.append(tweet)
        return home_timeline_tweets


# # # # TWITTER AUTHENTICATER # # # #
class TwitterAuthenticator():

    def authenticate_twitter_app(self):
        auth = OAuthHandler(akun_twitter.CONSUMER_KEY, akun_twitter.CONSUMER_SECRET)
        auth.set_access_token(akun_twitter.ACCESS_TOKEN, akun_twitter.ACCESS_TOKEN_SECRET)
        return auth

# # # # TWITTER STREAMER # # # #
class TwitterStreamer():
    """
    Class for streaming and processing live tweets.
    """
    def __init__(self):
        self.twitter_autenticator = TwitterAuthenticator()

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # This handles Twitter authetification and the connection to Twitter Streaming API
        listener = TwitterListener(fetched_tweets_filename)
        auth = self.twitter_autenticator.authenticate_twitter_app()
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords:
        stream.filter(track=hash_tag_list)


# # # # TWITTER STREAM LISTENER # # # #
class TwitterListener(StreamListener):
    """
    This is a basic listener that just prints received tweets to stdout.
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

    def on_data(self, data):
        try:
            print(data)
            with open(self.fetched_tweets_filename, 'a') as tf:
                tf.write(data)
            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True

    def on_error(self, status):
        if status == 420:
            # Returning False on_data method in case rate limit occurs.
            return False
        print(status)


class TweetAnalyzer():
    """
    Functionality for analyzing and categorizing content from tweets.
    """

    def clean_tweet(self, tweet):
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", tweet).split())

    def pembagian_nol(self, n, d):
        return n / d if d else 0

    def clean_text(self, data):
      stopword = StopWordRemoverFactory().create_stop_word_remover()
      stemmer = StemmerFactory().create_stemmer()

      data = re.sub('[^a-zA-Z]',' ', str(data).lower())
      data = re.sub('\byok\b |\byuk\b', 'ayo', data)
      data = re.sub('\bmager\b', 'males', data)
      data = re.sub('\bmalas\b', 'males', data)
      data = re.sub('\bmls\b', 'males', data)
      data = re.sub('\bkuy\b', 'yuk', data)
      data = re.sub('\borg\b', 'orang', data)
      data = re.sub('\bjg\b', 'juga', data)
      data = re.sub('\budh\b', 'sudah', data)
      data = re.sub('\bmangat\b', 'semangat', data)
      data = re.sub('\bcemungut\b', 'semangat', data)
      data = re.sub('\bgas\b', 'yuk', data)
      data = re.sub('\benakeun\b', 'enak', data)
      data = re.sub('\bnaek\b', 'naik', data)
      data = re.sub('\bmmg\b', 'memang', data)
      data = re.sub('\bga\b', 'engga', data)
      data = re.sub('\bengga\b', 'tidak', data)
      data = re.sub('\bttg\b', 'tentang', data)
      data = re.sub('\brush hour\b', 'jam sibuk', data)
      data = re.sub('\bku\b', 'aku', data)
      data = re.sub('\bgak\b', 'tidak', data)
      data = re.sub('\bdgn\b', 'dengan', data)
      data = re.sub('\bbailk\b', 'pulang', data)
      data = re.sub('\bgatau\b', 'tidak tahu', data)
      data = re.sub('\bbat\b', 'banget', data)
      data = re.sub('\bampe\b', 'sampai', data)
      data = re.sub('\blg\b', 'sedang', data)
      data = re.sub('\banjay\b', 'asik', data)
      data = re.sub('\banjg\b', 'anjing', data)
      data = re.sub('\banjiing\b', 'anjing', data)
      data = re.sub('\bantum\b', 'kamu', data)
      data = re.sub('\basiq\b |\basyique\b |\basik\b', 'asyik', data)
      data = re.sub('\bbgt\b |\bbanget\b |\bbanged\b', 'sangat', data)
      data = re.sub('\bribet\b', 'repot', data)

      data = data.split()
      data = ' '.join(data)

      #setelah ngeganti baru ilangin stopword dan imbuhan kata dibawah ini
      #sastrawi remove stopwords
      data = stopword.remove(data) #stopword nya udah di di provide sastrawi
      #sastrawi stemming
      data = stemmer.stem(data)

      return data

    def analyze_sentiment(self, tweet):
        # load positive word
        positive = pd.read_csv('../bahan/positive.txt', header=None)
        positive = positive[0].values.tolist()
        positive = '|'.join(positive)
        # load negative word
        negative = pd.read_csv('../bahan/negative.txt', header=None)
        negative = negative[0].values.tolist()
        negative = '|'.join(negative)

        lower_positive_count = len(re.findall(positive, self.clean_text(tweet).lower()))
        lower_negative_count = len(re.findall(negative, self.clean_text(tweet).lower()))
        len_count   = len(tweet.split())

        positive    = self.pembagian_nol(lower_positive_count,len_count)
        negative    = self.pembagian_nol(lower_negative_count,len_count)

        if positive == 0 or positive >= 1:
            return 'Positive'
        elif positive == negative:
            return 'Netral'
        else:
            return 'Negative'

    def tweets_to_data_frame(self, tweets):
        df = pd.DataFrame(data=[tweet.text for tweet in tweets], columns=['tweets'])

        df['id'] = np.array([tweet.id for tweet in tweets])
        df['len'] = np.array([len(tweet.text) for tweet in tweets])
        df['date'] = np.array([tweet.created_at for tweet in tweets])
        df['source'] = np.array([tweet.source for tweet in tweets])
        df['likes'] = np.array([tweet.favorite_count for tweet in tweets])
        df['retweets'] = np.array([tweet.retweet_count for tweet in tweets])

        return df


if __name__ == '__main__':

    twitter_client = TwitterClient()
    tweet_analyzer = TweetAnalyzer()

    api = twitter_client.get_twitter_client_api()

    for page in api.user_timeline(screen_name="mrtjakarta", count=200):
        print(page)
        for status in page:
            tweets = status._json
            df = tweet_analyzer.tweets_to_data_frame(tweets)
            df['sentiment'] = np.array([tweet_analyzer.analyze_sentiment(tweet) for tweet in df['tweets']])
            df.to_csv('hasil/mrt.csv')

    print(df.head(10))
