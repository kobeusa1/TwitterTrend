import boto3
import json
from alchemyapi import AlchemyAPI
from multiprocessing import Pool
import traceback
# Create the AlchemyAPI Object
alchemyapi = AlchemyAPI()
# Get the service resource
sns = boto3.resource('sns')
topic = sns.create_topic(Name='SentimentTwitterMap')
topic.subscribe(Protocol='http', Endpoint="http://twittsentiment.us-east-1.elasticbeanstalk.com")
sqs = boto3.resource('sqs')
# Get the queue
queue = sqs.get_queue_by_name(QueueName='TwitterMap')

def worker(_):
	# Process messages by printing out body and optional author name
	while True: 
		for message in queue.receive_messages(MaxNumberOfMessages=10, WaitTimeSeconds=20):
			try:
				tweets = json.loads(message.body)
				response = alchemyapi.sentiment('text', tweets['text'])
				print response
	            # response = alchemyapi.sentiment('text', tweets['text'])
				if response['status'] == 'OK':
					tweets['sentiment'] = response['docSentiment']['type']
					data = json.dumps(tweets, ensure_ascii=False)
					topic.publish(Message = data)
					print data
			except:
				traceback.print_exc()

if __name__ == "__main__":
    pool = Pool(3)
    pool.map(worker, range(3))