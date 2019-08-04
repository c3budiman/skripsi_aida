from tweepy.streaming import StreamListener
from tweepy import OAuthHandler
from tweepy import Stream
import tweepy
import re
import string
from textblob import TextBlob
import preprocessor as p
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
import json
import pandas as pd
import pyrebase

from Sastrawi.Stemmer.StemmerFactory import StemmerFactory
from Sastrawi.StopWordRemover.StopWordRemoverFactory import StopWordRemoverFactory
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.naive_bayes import MultinomialNB, BernoulliNB
from tqdm import tqdm_notebook as tqdm


import akun_twitter
import firebase_kred

# # # # TWITTER STREAMER # # # #
class TwitterStreamer():
    """
    Class Buat Stream Dan Fetch Twit secara Real Time
    """
    def __init__(self):
        pass

    def stream_tweets(self, fetched_tweets_filename, hash_tag_list):
        # Yang disini buat authentikasi dan konek ke stream api twitter via http
        listener = StdOutListener(fetched_tweets_filename)
        auth = OAuthHandler(akun_twitter.CONSUMER_KEY, akun_twitter.CONSUMER_SECRET)
        auth.set_access_token(akun_twitter.ACCESS_TOKEN, akun_twitter.ACCESS_TOKEN_SECRET)
        stream = Stream(auth, listener)

        # This line filter Twitter Streams to capture data by the keywords:
        stream.filter(track=hash_tag_list)


# # # # TWITTER STREAM LISTENER # # # #
class StdOutListener(StreamListener):
    """
    Ini buat listen, twitter -> proses sentimen -> save ke Firebase
    """
    def __init__(self, fetched_tweets_filename):
        self.fetched_tweets_filename = fetched_tweets_filename

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
        #menginisialisasi kata positive
        positive = pd.read_csv('../bahan/positive.txt', header=None)
        positive = positive[0].values.tolist()
        positive = '|'.join(positive)

        #menginisialisasi kata negative
        negative = pd.read_csv('../bahan/negative.txt', header=None)
        negative = negative[0].values.tolist()
        negative = '|'.join(negative)

        #hitung nilai dari readable negative dan positive nya
        lower_positive_count = len(re.findall(positive, tweet.lower()))
        lower_negative_count = len(re.findall(negative, tweet.lower()))
        len_count   = len(tweet.split())

        #handling supaya pembagian nya ga nol
        positive    = self.pembagian_nol(lower_positive_count,len_count)
        negative    = self.pembagian_nol(lower_negative_count,len_count)

        #print nilai nya ke stdout dlu :
        print("Positive value : ", positive)
        print("Negative Value : ", negative)

        #return hasil dari analisa sentimen :
        if positive == 0 or positive >= 1:
            return 'Positive'
        elif positive == negative:
            return 'Netral'
        else:
            return 'Negative'

    def on_data(self, data):
        try:
            #flow data twit ada disini :
            #json_acceptable_string = data.replace("'", "\"")
            d = json.loads(data)

            #jangan ada retweet :
            if not d['retweeted'] and 'RT @' not in d['text']:
                #save ke firebase :
                firebase = pyrebase.initialize_app(firebase_kred.config)
                db = firebase.database()
                db.child('MRT').push(d)

                #bersihin tweet dan stem :
                stem_kata = self.clean_text(self.clean_tweet(d['text']))
                #hitung sentimen
                sentimen = self.analyze_sentiment(stem_kata)

                #print twit yg dah di bersihin ke console :
                print(stem_kata)
                #print sentimen :
                print('Sentimen : ',sentimen)

            return True
        except BaseException as e:
            print("Error on_data %s" % str(e))
        return True


    def on_error(self, status):
        print(status)


if __name__ == '__main__':

    # Authenticate using config.py and connect to Twitter Streaming API.
    hash_tag_list = ["mrt jakarta","mrtjakarta","@mrtjakarta"]
    fetched_tweets_filename = "hasil/tweets.txt"

    twitter_streamer = TwitterStreamer()
    twitter_streamer.stream_tweets(fetched_tweets_filename, hash_tag_list)
