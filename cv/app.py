from flask import Flask, request ,render_template,redirect, url_for
#import response
import pickle
import tflearn 
import nltk
import numpy as np
import random
from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()
emotion_text = 'sad'
data = pickle.load( open( "training_data", "rb" ) )
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']


app = Flask(__name__) 
import json
with open('intents.json') as json_data:
    intents = json.load(json_data)

# load our saved model
net = tflearn.input_data(shape=[None, len(train_x[0])])
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, 8)
net = tflearn.fully_connected(net, len(train_y[0]), activation='softmax')
net = tflearn.regression(net)
model = tflearn.DNN(net, tensorboard_dir='tflearn_logs')
model.load('./model.tflearn')

context = {}


def clean_up_sentence(sentence):
    # tokenize the pattern
    sentence_words = nltk.word_tokenize(sentence)
    # stem each word
    sentence_words = [stemmer.stem(word.lower()) for word in sentence_words]
    return sentence_words

# return bag of words array: 0 or 1 for each word in the bag that exists in the sentence
def bow(sentence, words, show_details=False):
    # tokenize the pattern
    sentence_words = clean_up_sentence(sentence)
    # bag of words
    bag = [0]*len(words)  
    for s in sentence_words:
        for i,w in enumerate(words):
            if w == s: 
                bag[i] = 1
                if show_details:
                    print ("found in bag: %s" % w)

    return(np.array(bag))

    

def classify(sentence):
    ERROR_THRESHOLD = 0.25
    # generate probabilities from the model
    results = model.predict([bow(sentence, words)])[0]
    # filter out predictions below a threshold
    results = [[i,r] for i,r in enumerate(results) if r>ERROR_THRESHOLD]
    # sort by strength of probability
    results.sort(key=lambda x: x[1], reverse=True)
    return_list = []
    for r in results:
        return_list.append((classes[r[0]], r[1]))
    # return tuple of intent and probability
    return return_list


# create a data structure to hold user context

@app.route('/')
def home():
    return render_template("home.html")


@app.route('/read')

def read():
  f = open("emotion.txt","r")
  x = f.read(10)
  return x



@app.route('/response/<sentence>')

def response(sentence, userID='123', show_details=False):
    print(sentence)
   

    ERROR_THRESHOLD = 0.25
    results = classify(sentence)
    #redirect(url_for('classify',sentence = sentence))
    # if we have a classification then find the matching intent tag
    if results:
        # loop as long as there are matches to process
        while results:
            for i in intents['intents']:
                # find a tag matching the first result
                if i['tag'] == results[0][0]:
                    # set context for this intent if necessary
                    if 'context_set' in i:
                        if show_details: print ('context:', i['context_set'])
                        context[userID] = i['context_set']

                    # check if this intent is contextual and applies to this user's conversation
                    if not 'context_filter' in i or \
                        (userID in context and 'context_filter' in i and i['context_filter'] == context[userID]):
                        if show_details: print ('tag:', i['tag'])
                        # a random response from the intent
                        return random.choice(i['responses'])

            results.pop(0)




    
@app.route('/chatbot', methods=['GET', 'POST']) 
def chatbot():
    
      return'''
      <!DOCTYPE html> 
      <html lang="en" >
<head>
  <meta charset="UTF-8">
  <title>Chat Bot UI</title>
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <style>
  body {
  background:#eee;
  height:100%;
}
.mainHead {
  position:fixed;
  width:100%;
  height:100%;
}
.head {
  height:50px;
  background:#00303f;
  color:white;
  font-family:monospace;
  position:relative;
}
.head span {
  position:absolute;
  top:50%;
  left:50%;
  transform:translate(-50%,-50%);
  font-size:18px;
}
.chat {
  top:50px;
  position:relative;
  z-index:-1;
  bottom:40px;
  margin-bottom:100px;
}
.main {
  overflow-y:auto;
}
.send {
  width:100%;
  position:fixed;
  bottom:0px;
  margin-right:10px;
  background:white;
  display:inline-flex;
}
.send .txt1 {
  width:100%;
  padding:5px;
  margin:5px;
  color:#00303f;
  font-weight:bold;
}
.send .txt1:focus {
  border-color:#00303f;
}
.send .btn1 {
  color:silver;
  background:#00303f;
  width:70px;
  margin:5px;
  height:40px;
}
.txt {
  background:#c9e1be;
  padding:5px;
  position:relative;
  border-right: 2px solid #00303f;
}
.txt2 {
  background:#A1E7ED;
  padding:5px;
  position:relative;
  border-left: 2px solid #0c757e;
}
.txt-div {
  margin:5px;
  padding:5px;
  width:80%;
  float:right;
}

.txt-div2 {
  margin:5px;
  padding:5px;
  width:80%;
  float:left;
}
.time {
  font-size:12px;
  background:#c9e1be;
  padding:5px;
  border-right: 2px solid #00303f;
}
.time2 {
  font-size:12px;
  background:#A1E7ED;
  padding:5px;
  border-left: 2px solid #0c757e;
}
  </style>

  
</head>

<body>

  <div class="mainHead">
<div class="head">
  <span>Emotion Based Chatbot - Pally</span>
</div>
 </div> 
<div class="chat">
  <div class="main">
  </div>
</div>
<div class="send">
<form method="POST" action="#">
  <!--<input type="input" class="txt1 form-cotrol">-->
  <textarea class="form-control txt1" rows="3"></textarea>
  <input type="button" class="btn btn1" value="SEND" onclick="sender()">
  </form>
</div>
  <script src='https://cdnjs.cloudflare.com/ajax/libs/jquery/3.3.1/jquery.min.js'></script>
<script src='https://cdnjs.cloudflare.com/ajax/libs/twitter-bootstrap/4.2.1/js/bootstrap.min.js'></script>

 <script> 

 $('body').ready(function() {
  $.ajax({
            url: '/read',
            success: function(resp) {
             $.ajax({
            url: '/response/<sentence>'+resp,
            data: { param: resp},
            type: 'GET',
            success: function(r) {
               $('.main').append('<div class="txt-div2" ><div class="txt2 msg">'+r+'</div><div class="time2">'+new Date().toLocaleTimeString()+'</div></div>');
            },
            error: function(error) {
                console.log(error);
            }
        });
            },
            error: function(error) {
                console.log(error);
            }
        });
});

function sender() {
  var msg = $('.txt1').val();
  $('.main').append('<div class="txt-div" ><div class="txt msg">'+msg+'</div><div class="time">'+new Date().toLocaleTimeString()+'</div></div>');
  $('.txt1').val('');
  $.ajax({
            url: '/response/<sentence>'+msg,
            data: { param: msg},
            type: 'GET',
            success: function(response) {
               $('.main').append('<div class="txt-div2" ><div class="txt2 msg">'+response+'</div><div class="time2">'+new Date().toLocaleTimeString()+'</div></div>');
            },
            error: function(error) {
                console.log(error);
            }
        });
  
  $('.chat').scrollTop = $('.chat').scrollHeight;
}

function res(msg) {
  $('.main').append('<div class="txt-div2" ><div class="txt2 msg">'+msg+'</div><div class="time2">'+new Date().toLocaleTimeString()+'</div></div>');
}

//var chat = {"Hi":"Hi","Hi2":"Hi2","Hi3":"Hi3"}

    </script>
'''
'''
</body>

</html>
'''
      


if __name__ == '__main__':
    app.run(debug=True, port=5000)
