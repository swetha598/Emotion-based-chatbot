# restore all of our data structures
import pickle
import tflearn 
import nltk
import random
from Tkinter import *
import ttk
import tkMessageBox

import numpy as np
from threading import Thread


from nltk.stem.lancaster import LancasterStemmer
stemmer = LancasterStemmer()


#emotion_text = 'sad'

#from video_emotion_color_demo import emotion_text

print emotion_text

data = pickle.load( open( "training_data", "rb" ) )
words = data['words']
classes = data['classes']
train_x = data['train_x']
train_y = data['train_y']

# import our chat-bot intents file
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

    ERROR_THRESHOLD = 0.25

def classify(sentence):
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

def response(sentence, userID='123', show_details=False):
    results = classify(sentence)
    # if we have a classification then find the matching intent tag
    if results:
        # loop as long as there are matches to process
        while results:
            for i in intents['intents']:
                # find a tag matching the first result
                if i['tag'] == results[0][0]:
                    # a random response from the intent
                    return random.choice(i['responses'])

            results.pop(0)


# create a data structure to hold user context
context = {}

ERROR_THRESHOLD = 0.25
def classify(sentence):
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

def response(sentence, userID='123', show_details=False):
    results = classify(sentence)
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



############
def receive():
    """Handles receiving of messages."""
    global counter
    global emotion_text
    if counter == 1:
    	msg_list.insert(END, 'PAL: '+ response(emotion_text))
        msg_list.itemconfig(END, {'bg':'#c2c3a8'})
        counter +=1 
        return 
    i=1
    while i==1 and counter != 1:
        try:
            #msg = client_socket.recv(BUFSIZ).decode("utf8")
            msg_list.insert(END,'ME : '+ sending)
            msg_list.itemconfig(END, {'bg':'#FFC300'})
            msg_list.insert(END, 'PAL: '+ response(sending))
            msg_list.itemconfig(END, {'bg':'#c2c3a8'})
            
            i+=1
        except OSError:  # Possibly client has left the chat.
            break


###########
def send(event=None):  # event is passed by binders.
    """Handles sending of messages."""
    #send_button.configure(bg="orange")
    send_button.config(relief=SUNKEN)
    msg = my_msg.get()
    global sending 
    sending= msg
    receive()
    #msg_list.insert(0, msg)
    my_msg.set("")  # Clears input field.
    #client_socket.send(bytes(msg, "utf8"))
    if msg == "quit":
        #client_socket.close()
        top.quit()



#######
def on_closing(event=None):
    """This function is to be called when the window is closed."""
    my_msg.set("quit")
    send()

'''def bubble():
    xval = random.randint(5,765)
    yval = random.randint(5,615)
    canvas.create_oval(xval,yval,xval+30,yval+30, fill="#00ffff",outline="#00bfff",width=5)
    canvas.create_text(xval+15,yval+15,text="mytext")
    canvas.update()'''

#root.title("Math Bubbles")
#Button(root, text="Quit", width=8, command=quit).pack()
#Button(root, text="Start", width=8, command=bubble).pack()
#canvas = Canvas(root, width=800, height=650, bg = '#afeeee')
#canvas.pack()
#root.mainloop()

counter = 1
top = Tk()
top.title("Chatter")
sending = ''
messages_frame = Frame(top)
my_msg = StringVar() # For the messages to be sent.
my_msg.set("Type your message here")
scrollbar = Scrollbar(messages_frame)  # To navigate through past messages.
# Following will contain the messages.
msg_list = Listbox(messages_frame, background="#ffffff",height=15, width=50, yscrollcommand=scrollbar.set)
scrollbar.pack(side=RIGHT, fill=Y)
msg_list.pack(side=LEFT, fill=BOTH)
msg_list.pack()
messages_frame.pack()


receive_thread = Thread(target=receive)
receive_thread.start()

entry_field = Entry(top, text=my_msg)
#msg_list.insert(tkinter.END,entry_field)
entry_field.bind("<Return>", send)
entry_field.pack(padx=20, pady=20)
#canvas = Canvas(root, width=800, height=650, bg = '#afeeee')
#canvas.pack()
img = PhotoImage(file = "send22.gif")
send_button = Button(top, text='Send', bg = "orange", command=send)
tmi = img.subsample(3,3)
send_button.config(image = tmi, compound =  LEFT)
#send_button.pack(padx=20, pady=30,side=RIGHT)
send_button.place(x = 335, y = 260) 

top.protocol("WM_DELETE_WINDOW", on_closing)

mainloop()  # Starts GUI execution.


