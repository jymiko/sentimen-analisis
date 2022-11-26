import os

import pandas as pd
import re
import string

from dataclasses import dataclass, field
from django.conf import settings

from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
from nltk.tokenize import word_tokenize

from scipy.sparse import hstack
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.model_selection import train_test_split
from sklearn.naive_bayes import MultinomialNB
from sqlalchemy import create_engine

from typing import Any


@dataclass
class SentimentAnalyst:
    tweet_id: str
    text: str

    stemmer: PorterStemmer = field(default_factory=PorterStemmer)

    stop_words: Any = field(init=False)
    uri: str = field(init=False)

    vectorizer: Any = field(init=False)

    def __post_init__(self):
        self.stop_words = set(stopwords.words("indonesian"))
        self.uri = f'postgresql://admin:CBVF9baxjSFCA-Iv-Z5-jU04PwLCjS@us-west2.92047fa5-31a1-4c42-904a-77f39c60810d.gcp.ybdb.io:5433/sentiment?sslmode=verify-full&sslrootcert={os.path.join(settings.BASE_DIR, "sentimentanalysisapi/root.crt")}'

    def build_tweetsentiment_df(self):

        df = pd.read_csv(
            f"{settings.BASE_DIR}/fixtures.csv",
            usecols=['text', 'point']
        )

        return self.update_df(df)

    def update_df(self, df, change_through=False):
        f1 = []
        f2 = []
        f3 = []
        f4 = []

        for txt in df.text:
            f1.append(len(txt))
            f2.append(len(txt.split()))
            f3.append(sum([word in self.stop_words for word in txt.split()]))
            f4.append(sum([word in string.punctuation for word in word_tokenize(txt)]))

        if change_through:
            df["len"] = f1
            df["num_char"] = f2
        else:
            df["len"] = f1
            df["num_words"] = f2
            df["num_stopwords"] = f3
            df["num_pun"] = f4

        return df

    def update_text(self, text):
        f1 = [len(txt) for txt in text]
        f2 = [len(txt.split()) for txt in text]

        return f1, f2

    def preprocess(self, phrase):
        # removing the spaces
        corpus = []
        for text in phrase:
            text = re.compile("\\#").sub(
                "", re.compile("RT @").sub("@", text.lower(), count=1).strip()
            )
            text = re.sub("@[^\\s]+", "", text)
            text = " ".join([self.stemmer.stem(i) for i in text.split()])
            corpus.append(text)
        return corpus

    def get_hstack(self, v, i_iloc_values):
        return hstack([v, i_iloc_values])

    def get_train_feat(self, df):
        X = df.drop(columns="point")
        y = df.point
        x_train, x_val, y_train, _ = train_test_split(
            X, y, stratify=y,
            test_size=0.33, random_state=42
        )

        train_text = self.preprocess(x_train.text)
        val_text = self.preprocess(x_val.text)

        x_train["f1"], x_train["f2"] = self.update_text(train_text)
        x_val["f1"], x_val["f2"] = self.update_text(val_text)

        self.vectorizer = TfidfVectorizer(
            stop_words=self.stop_words, ngram_range=(1, 3), max_features=20000
        )
        self.vectorizer.fit(train_text)

        res = self.get_hstack(self.vectorizer.transform(train_text), x_train.iloc[:, [-6, -5, -2, -1]].values)

        return res, y_train

    def get_train_data(self):
        test_data = self.update_df(
            pd.DataFrame([{"text": self.text, "point": 0}]), change_through=True
        )
        test_text = self.preprocess(test_data.text)
        test_data["f1"], test_data["f2"] = self.update_text(test_text)

        return test_data, test_text

    def perform_analysis(self):
        df = self.build_tweetsentiment_df()

        train_feat, y_train = self.get_train_feat(df)

        test_data, test_text = self.get_train_data()

        model_nb = MultinomialNB()
        model_nb.fit(train_feat, y_train)

        point = pd.DataFrame(
            [
                {
                    "text": test_data.text,
                    "point": model_nb.predict(
                        self.get_hstack(
                            self.vectorizer.transform(test_text), test_data.iloc[:, -4:].values
                        )
                    ),
                }
            ]
        ).point.iloc[0][0]

        return point
