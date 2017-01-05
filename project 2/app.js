var express = require('express');
var app = express();
var http = require('http').Server(app);
var io = require('socket.io')(http);
var es = require('elasticsearch');
http.listen(8081, function(){
  console.log('listening on *:8888');
});
var bodyParser = require('body-parser');
var request = require("request");
app.use(express.static('public'));
app.use(bodyParser.json({type: 'text/plain'}));
var database = new es.Client({
    host: 'search-twittmap-6kcrspxukie6wotjhqthjgon4u.us-east-1.es.amazonaws.com:80'
});
app.get('/', function(req, res){
  res.sendfile('app.html');
});
app.post('/', function (req, res) {
	//socket.emit('testInput',req);
    res.status(200).end();
    var Responsetype = req.get('x-amz-sns-message-type');
    if (Responsetype === 'SubscriptionConfirmation') {
        var url = req.body.SubscribeURL;
        request(url, function (error, response, body) {
            console.log(body);
        });
    }
    else if (Responsetype === 'Notification') {
        var id = req.body.MessageId;
        var message = req.body.Message;
        database.index({
            index: 'twittmap',
            type: 'tweets',
            id: id,
            body: message
        });
        io.emit('newcoming', {
            tweet: JSON.parse(message)
        });
    }
});

io.on('connection', function(socket){
	socket.emit('First message', {message: 'Connected!', id: socket.id});
	socket.on('transferData', function(data) {
		var key = data.key;	
		console.log(key);
		database.search({
			  q: key,
			  size : 100
			}).then(function(body) {
			  var hits = body.hits.hits;
			  console.log(hits);
			  socket.emit('informationTransmission', {data: hits});

			}, function (error) {
			  console.trace(error.message);
			});
	 });

	 socket.on('serachRegion', function(data){
	 	console.log("received command");
	 	console.log(data.la);
	 	console.log(data.len);
	 	var lat = data.la;
	 	var lon = data.len;
		database.search({
			"index" : "twittmap",
			"tpye" : "tweets",
			"size" : "100",
			"body" : {
			    "query": {
			    "filtered": {
			      "query": {
			        "match_all": {}
			      },
			      "filter": {
			      	"geo_distance" : {
			      		"distance" : "200km",
			      		"tweets.geo" : {
			      			"lat" : data.la,
			      			"lon" : data.len
			      		}
			                    
			      	}
			      }
			    }
			  }
			}

			}).then(function (resp) {
			    var hits = resp.hits.hits;
			    console.log(hits.length);
			    socket.emit('getResponse', {data: hits});
			   

			}).catch(function (error) {
			    console.log("Error on geo_distance (coordiates)");
			    console.log(error);
			});
		}); 

	
});

