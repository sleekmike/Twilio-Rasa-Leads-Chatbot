<<<<<<< HEAD
# Twilio-Rasa-Leads-Chatbot
A simple chatbot built with Rasa and Twilio for engaging and following up leads using SMS or text message.
=======
MIT License	
	
	Copyright (c) 2021 
	
	Permission is hereby granted, free of charge, to any person obtaining a copy
	of this software and associated documentation files (the "Software"), to deal
	in the Software without restriction, including without limitation the rights
	to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
	copies of the Software, and to permit persons to whom the Software is
	furnished to do so, subject to the following conditions:
	
	The above copyright notice and this permission notice shall be included in all
	copies or substantial portions of the Software.
	
	THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
	IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
	FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
	AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
	LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
	OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
	SOFTWARE.

# Tech Stack

#### The Tech Stack used when developing this ChatBot include: Tensorflow, NLP, RASA, Twilio API(python) and MongoDB(for data storage)

# Installation
#### Install Python3.7 or later for this project.

## RASA Installation (Install this exact version of RASA to avoid dependency issues)

`pip3 install --no-cache-dir rasa==2.8.2`
`pip3 install rasa-x==0.42.0 --extra-index-url https://pypi.rasa.com/simple`

## Mongo Database Installation
Follow the article below for installing MongoDB:

https://www.digitalocean.com/community/tutorials/how-to-install-mongodb-on-ubuntu-18-04-source
/usr/bin/mongod --config /etc/mongod.conf
`sudo systemctl start mongod.service`
`sudo systemctl status mongod`
`sudo systemctl enable mongod`

# Ngrok (Optional)
If can use Ngrok to forward and receive requests on to RASA server unning locally on your machine or server. Rmember to update the Ngrok URL or Link on Twilio's website.
`snap install ngrok`
`./ngrok authtoken < "Your Token Here" >`


# Running The ChatBot

## Running RASA, Twilio and MongoDB Integration

## Change Directory to Project Directory and Activate Virtual Environment
`cd chatbot`
`source chatbot/bin/activate`
`cd oncoreleads`

## Start Mongo DataBase
`sudo systemctl start mongod.service`
`sudo systemctl status mongod`

## Set Environment Variables (Twilio API Details and Phone Number)
`export TWILIO_ACCOUNT_SID="<Twilio SID>"`
`export TWILIO_AUTH_TOKEN="<Twilio TOKEN>"`
`export TWILIO_SMS_FROM="<Twilio Phone Number>"`
`export MESSAGING_SERVICE_SID="<Message Service Sid>"`

## run RASA server
`rasa run -m models --enable-api --credentials credentials.yml --endpoints endpoints.yml --cors "*"`

## run RASA Actions Server API
`rasa run actions`

## Send SMS To a New Lead
#### use the "sender.py" script to send message to a new lead.
`python3 sender.py`

# Usefull RASA and Twilio Links
https://rasa.com/docs
https://rasa.com/blog/connecting-a-rasa-assistant-to-twilio/
https://rasa.com/docs/rasa/connectors/twilio


#### The files below are used for training the ChatBot, programming it's logic and customizing its responses. 
- domain.yml
- config.yml 
- data/nlu.yml
- data/rules.yml
- data/stories.yml
- actions/actions.py
  
#### The files below are used for configuring Twilio API, MongoDB and Other Third Party APIs and Integrations
- credentials.yml
- endpoints.yml

## Training the ChatBot's Model
Train a model in this repository with `rasa train`  


## Run RASA X for Interactive Development and Testing.

- Call `rasa shell` to start interacting with the chatbot (alternatively, you can [use Rasa X](https://rasa.com/docs/rasa-x/) and interact with the bot via a developer GUI)  

Our trained model is included in the `models` directory. 
# Enjoy!
>>>>>>> initial commit
