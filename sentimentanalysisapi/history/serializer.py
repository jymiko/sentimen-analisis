from rest_framework import serializers
from .models import History, Sentiment

class SentimenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sentiment
        fields = ('positif', 'negatif', 'netral')

class HistorySerializer(serializers.ModelSerializer):
    history_sentimen = SentimenSerializer(many=True, default=None)
    # tweet_id = serializers.CharField(max_length=255, write_only=True)

    class Meta:
        model = History
        fields = ('user_id','tweet_id','tweet_text','history_sentimen','created_at')

    def create(self, validated_data):
        print(validated_data, 'data validated')
        sentimens_data = validated_data.pop('history_sentimen')
        histories_data = History.objects.create(**validated_data)
        for sentimen_data in sentimens_data:
            Sentiment.objects.create(history=histories_data, **sentimen_data)
        return histories_data

    def update(self, instance, validated_data):
        sentimens_data = validated_data.pop('history_sentimen')
        sentimens = (instance.history_sentimen).all()
        sentimens = list(sentimens)

        # instance.tweet_id = validated_data.get()
        # instance.tweet_text = validated_data.get('positif', instance.tweet_text)
        # instance.created_at = validated_data.get('negatif', instance.created_at)
        # instance.save()

        for sentimen_data in sentimens_data:
            sentimen = sentimens.pop(0)
            sentimen.positif = sentimen_data.get('positif', sentimen.positif)
            sentimen.negatif = sentimen_data.get('negatif', sentimen.negatif)
            sentimen.netral = sentimen_data.get('netral', sentimen.netral)
            sentimen.save()
        return instance

