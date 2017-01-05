import json
import tweepy
from tweepy import StreamListener
from elasticsearch import Elasticsearch
import certifi
import optparse
import boto3
from dateutil import parser
#Variables that contains the user credentials to access Twitter API
access_token = ""
access_token_secret = ""
consumer_key = ""
consumer_secret = ""

sqs = boto3.resource('sqs')
queue = sqs.create_queue(QueueName='TwitterMap')
queue = sqs.get_queue_by_name(QueueName='TwitterMap')

#This is a basic listener that just prints received tweets to stdout.
class StdOutListener(tweepy.StreamListener):
    def __init__(self):
        super(StdOutListener, self).__init__()

    def on_data(self, data):
        tweet = json.loads(data)
        try: 
            if tweet.get('lang') == 'en' and tweet['coordinates']:

                print tweet["coordinates"]
                coordinates = tweet['coordinates']['coordinates']
                timestamp = parser.parse(tweet['created_at'])
                timestamp = timestamp.strftime('%Y-%m-%dT%H:%M:%SZ')
                twitter = {"text" : tweet["text"], 
                            "user": tweet['user']["screen_name"],
                            "geo": {
                                "lat" : coordinates[1],
                                "lon" : coordinates[0]
                            },
                            "time" : timestamp
                        }

                data = json.dumps(twitter, ensure_ascii=False)
                queue.send_message(MessageBody= data)
                print data
                # es.index(index = 'twittmap', doc_type='tweets',id = tweet['id'], body=twitter)
                # f.write(twitter)

        except Exception as e:
            print e

    def on_error(self, status):
        print status

    
if __name__ == '__main__':
    with open('tweetstream.log', 'a') as f:
        # es = Elasticsearch(hosts = [endpoint], port = 443, use_ssl = True, verify_certs = True, ca_certs = certifi.where())
    #This handles Twitter authetification and the connection to Twitter Streaming API
        l = StdOutListener()
        auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
        auth.set_access_token(access_token, access_token_secret)
        stream = tweepy.Stream(auth, l)
    
        #This line filter Twitter Streams to capture data by the keywords: 
        stream.filter(track=['Hillary', 'Trump', 'car', 'cat', 'dog', 'apple', 'NBA', 'Boston', 'basketball', 'football', 'trip' 'ice cream'])

    



















