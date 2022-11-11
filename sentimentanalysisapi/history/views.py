from django.shortcuts import render
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.response import Response
from .serializer import HistorySerializer
from .models import History
from rest_framework import permissions
from .permissions import IsOwner
import twitter
import tweepy
import pymysql
import pandas as pd
import warnings
from sklearn.naive_bayes import MultinomialNB
from sklearn.metrics import accuracy_score
import re
from sklearn.feature_extraction.text import TfidfVectorizer,CountVectorizer
from sklearn.model_selection import train_test_split
from nltk.tokenize import word_tokenize
from nltk.stem import PorterStemmer
from nltk.corpus import stopwords
from scipy.sparse import hstack
import string
from django.http import JsonResponse

stem=PorterStemmer()
stop_words=set(stopwords.words('indonesian'))
warnings.filterwarnings("ignore")

consumer_key = "UG00VDN2k1tCUNrtJ2XSgnCvu"
consumer_secret = "WOHrgBIKoCUGWruEP6d0gjmI0dZcmNuQryOhsn3TUmUtluOl3H"
access_token = "1427526512928968708-TBRVt2HlvOziTccV2w3VYNPR7bMBa8"
access_secret = "pSi3GwB6cQHIpqju08sChWcXe41HBPpa83EF2CyP8betZ"
bearer_token="AAAAAAAAAAAAAAAAAAAAADn0fgEAAAAAEuV2B0xQzLWbmkeAuKpv%2FGBPtLc%3DHmeBCwQ2dbglhLniSp0MLUu2Uk4lL1DwFrypQREsnYuAPj6kLf"

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_secret)
api = tweepy.API(auth, wait_on_rate_limit=True)
filterKey = " -filter:retweets"

class HistoryList(ListCreateAPIView):
    serializer_class = HistorySerializer
    queryset = History.objects.all()
    permission_classes = (permissions.IsAuthenticated,IsOwner,)
    #

    def create(self, request, *args, **kwargs):
        def buildDataFrame():
            con = pymysql.connect(host='127.0.0.1', user='root', password='Malang2019.')
            sql = 'Select * From sentiment.crawl_crawl'
            df = pd.read_sql(sql, con)
            df = df.drop('id', 1)
            df = df.drop('created_at', 1)
            df = df.drop('tweet_id', 1)
            return df

        def buildTestSetDataFrame(search_keyword):
            try:
                tweets_fetched = tweepy.Cursor(api.search, q=search_keyword+filterKey, lang="in", tweet_mode="extend").items(100)

                for status in tweets_fetched:
                    print(status, 'status')
                    if (not status.retweeted) and ('RT @' not in status.text):
                        data = [{"text": status.text, "sentiment": None}]
                        df = pd.DataFrame(data)
                        print('df'+ df)
                return df
            except:
                print("Unfortunately, something went wrong..")
                return None

        def getTweetText(search_keyword):
            tweets_fetch =api.get_status(search_keyword)
            return tweets_fetch.text

        tweet_id = request.data['tweet_id']
        trainData = buildDataFrame()
        testData = buildTestSetDataFrame(tweet_id)
        tweetText = getTweetText(tweet_id)
        temp = trainData.tweet_text.value_counts()

        # # descriptive Analysis of the SentenceId
        def Feature_engineering_1(text_data):
            f1 = [len(text) for text in text_data]
            f2 = [len(text.split()) for text in text_data]
            f3 = []
            for text in text_data:
                words = [word in stop_words for word in text.split()]
                f3.append(sum(words))
            f4 = []
            for text in text_data:
                words = [word in string.punctuation for word in word_tokenize(text)]
                f4.append(sum(words))
            return f1, f2, f3, f4

        def Feature_engineering_2(text_data):
            f1 = [len(text) for text in text_data]
            f2 = [len(text.split()) for text in text_data]

            return f1, f2

        f1, f2, f3, f4 = Feature_engineering_1(trainData.tweet_text)

        trainData["len"] = f1
        trainData["num_words"] = f2
        trainData["num_stopwords"] = f3
        trainData["num_pun"] = f4

        def Preprocess(phrase):
            # removing the spaces
            corpus = []
            for text in phrase:
                text = text.lower()
                # text = text.strip()
                #  text=re.sub(r"n,t"," not",text)
                text = re.compile('\#').sub('', re.compile('rt @').sub('@', text, count=1).strip())
                text = re.sub('@[^\s]+', '', text)
                text = " ".join([stem.stem(i) for i in text.split()])
                print(text, 'textdata')
                corpus.append(text)
            return corpus

        X = trainData.drop(columns="sentiment")
        y = trainData.sentiment

        x_train, x_val, y_train, y_val = train_test_split(X, y, stratify=y)
        print("The shape of the Training set :", x_train.shape, y_train.shape)
        print("The shape of the Validation set :", x_val.shape, y_val.shape)

        train_text = Preprocess(x_train.tweet_text)
        val_text = Preprocess(x_val.tweet_text)

        f1, f2 = Feature_engineering_2(train_text)
        f11, f22 = Feature_engineering_2(val_text)
        x_train["f1"] = f1
        x_train["f2"] = f2
        x_val['f1'] = f11
        x_val['f2'] = f22

        print(x_train)

        vectorizer = TfidfVectorizer(stop_words=None, ngram_range=(1, 3), max_features=20000)
        vectorizer.fit(train_text)

        train_feat = vectorizer.transform(train_text)
        val_feat = vectorizer.transform(val_text)

        train_feat = hstack([train_feat, x_train.iloc[:, [-6, -5, -2, -1]].values])
        val_feat = hstack([val_feat, x_val.iloc[:, [-6, -5, -2, -1]].values])

        model_nb = MultinomialNB()
        model_nb.fit(train_feat, y_train)
        y_val_pre = model_nb.predict(val_feat)
        y_train_pre = model_nb.predict(train_feat)

        print("The accuracy of Training Data :", accuracy_score(y_train, y_train_pre))
        print("The accuracy of Testing Data :", accuracy_score(y_val, y_val_pre))

        # feature engineerin before preprocess
        f1, f2, f3, f4 = Feature_engineering_1(testData.text)
        testData["len"] = f1
        testData["num_char"] = f2
        # feature engineering after Preprocess
        test_text = Preprocess(testData.text)
        print(test_text)
        f1, f2 = Feature_engineering_2(test_text)
        testData["f1"] = f1
        testData['f2'] = f2

        test_feat = vectorizer.transform(test_text)
        test_feat = hstack([test_feat, testData.iloc[:, -4:].values])

        y_test_pre = model_nb.predict(test_feat)
        sumission = pd.DataFrame()
        sumission["text"] = testData.text
        sumission["sentiment"] = y_test_pre

        print(sumission.head())
        positif = sumission.loc[sumission.sentiment == 'positif', 'sentiment'].count()
        negatif = sumission.loc[sumission.sentiment == 'negatif', 'sentiment'].count()
        netral = sumission.loc[sumission.sentiment == 'netral', 'sentiment'].count()

        datahistory = {
                "tweet_id": request.data['tweet_id'],
                "tweet_text": tweetText,
                "history_sentimen": [
                    {
                        "positif": positif,
                        "negatif": negatif,
                        "netral": netral
                    }
                ]
            }

        print(datahistory)

        serializer = self.serializer_class(data=datahistory)
        serializer.is_valid(raise_exception=True)
        # #save ke database
        serializer.save(user=self.request.user)
        user_data = serializer.data
        print(user_data)
        #
        return JsonResponse(datahistory, safe=False)

class HistoryDetailsAPIView(ListCreateAPIView):

    serializer_class = HistorySerializer
    queryset = History.objects.all()
    permission_classes = (permissions.IsAuthenticated,)
    lookup_field = "user_id"
    # swagger_schema = None #menyembunyikan schema method di swagger ui

    def get_queryset(self):
        print(self.request)
        return self.queryset.filter(user=self.request.user)