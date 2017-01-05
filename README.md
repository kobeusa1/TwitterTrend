# TwittTrends
1. Set up Elasticsearch and create index twittmap with properties: text, user, geo and time. 

2. deploy web applicatin in Elasticbean

3. create twitterdata streaming queue in aws sqs application and send twitter to sqs specific queue, here we named it as "TwitterMap"

4. Create topic named "SentimentTwitterMap" in sns and set subscription endpoint as deployment in Elasticbean.  

5. Use AlchemyAPI to analyzed each tweet fetched from streaming queue and add the sentiment data to tweet data. 