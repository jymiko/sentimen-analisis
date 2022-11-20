import tweepy

from django.conf import settings


client = tweepy.Client(
    settings.BEARER_TOKEN,
    settings.API_KEY,
    settings.API_SECRET,
    settings.ACCESS_TOKEN,
    settings.ACCESS_SECRET
)


def get_tweet_info(tweet_id):
    try:
        tweet_info = client.get_tweet(
            id=tweet_id,
            expansions=[
                "author_id",
                "in_reply_to_user_id",
                "referenced_tweets.id",
                "attachments.media_keys"
            ],
            tweet_fields=[
                "author_id",
                "conversation_id",
                "created_at",
                "in_reply_to_user_id",
                "referenced_tweets",
                "attachments"
            ]
        )

        media = None
        if tweet_info.includes and tweet_info.includes.get("media"):
            media = [
                {"media_key": x.media_key, "type": x.type}
                for x in tweet_info.includes.get("media")
            ]

        return {
            "tweet_id": tweet_id,
            "text": tweet_info.data.text,
            "created_at": tweet_info.data.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            "media": media
        }
    except Exception as err:
        return {
            "message": err.response.reason,
            "status": err.response.status_code
        }
