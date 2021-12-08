# This files contains your custom actions which can be used to run
# custom Python code.
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions

from rasa_sdk.events import SlotSet
from typing import Any, Text, Dict, List
from rasa_sdk import Action, Tracker
from rasa_sdk.executor import CollectingDispatcher
from rasa_sdk.events import ReminderScheduled, ReminderCancelled
import requests
from twilio.rest import Client
from twilio.rest import Client
import os
import time
import datetime


# ===========================> Appointment and Reminder <================================ #
def message_sender(agent_number, agent_name, message):
    """ Sends call appointements and reminder alerts. """
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    print("agent_number :", agent_number)
    print("agent_name :", agent_name)
    message = client.messages.create(
        messaging_service_sid=os.getenv('MESSAGING_SERVICE_SID'),
        body=message,
        from_=os.getenv('TWILIO_SMS_FROM'),
        to=agent_number)
    print(message)


def call_appointment_alert(agent, lead):
    """ Alerts Human agent to call new lead immediately. """
    # agent details
    agent_name = agent["agent_name"]
    agent_number = agent["agent_number"]
    # lead details
    lead_name = lead["lead_name"]
    lead_number = lead["lead_number"]
    message = f"Hi {agent_name}, You have a call appointment with {lead_name}, here is the lead's phone number: {lead_number}"
    response = message_sender(agent_number, agent_name, message)
    result = response
    return result


def call_appointment_reminder(agent, lead, lead_message):
    """ Alerts Human agent about the new lead's call appointment and includes the leads original appointment message. """
    # agent details
    agent_name = agent["agent_name"]
    agent_number = agent["agent_number"]
    # lead details
    lead_name = lead["lead_name"]
    lead_number = lead["lead_number"]
    message = f"Hi {agent_name}, You a have call appointment with {lead_name}, here is the lead's phone number: {lead_number}, here is the appointment message: '{lead_message}'"
    response = message_sender(agent_number, agent_name, message)
    result = response
    return result


# ===================================> First SMS <================================ #
def first_message_sender(lead_number, lead_name):
    """ Sends first engagemt SMS to new Lead. """
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    print("new lead number: ", lead_number)
    print("new lead name: ", lead_name)
    #first_message = 'Hi John! Alex here with Social Security Disability Helpers. We just received your inquiry online. Would you prefer to chat via text message or should I give you a quick call so that I can assist you?'
    first_message = f'Hi {lead_name}! Alex here with Social Security Disability Helpers. We just received your inquiry online. Would you prefer to chat via text message or should I give you a quick call so that I can assist you?'
    message = client.messages.create(
        messaging_service_sid=os.getenv('MESSAGING_SERVICE_SID'),
        body=first_message,
        from_=os.getenv('TWILIO_SMS_FROM'),
        to=lead_number)
    print(message)
    return "message sent"


class FirstMessage(Action):
    """ Sends first engagemt SMS to new Lead. """
    def name(self) -> Text:
        return "first_SMS"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        lead_number = entities[0]["value"]
        print("new lead number: ", lead_number)
        lead_name = entities[1]["value"]
        print("new lead name: ", lead_name)
        first_message_sender(lead_number, lead_name)
        print("first engagement SMS sent!!!")
        try:
            lead_name_slot = tracker.get_slot('lead_name')
            lead_number_slot = tracker.get_slot('lead_number')
            print("lead_name_slot: ", lead_name_slot)
            print("lead_number_slot: ", lead_number_slot)
        except exception as e:
            print("slot get error: ", e)
        # Reminder for 30 minutes later if no response from the lead
        date = datetime.datetime.now() + datetime.timedelta(minutes=10)
        print("first SMS - current time: ", datetime.datetime.now())
        print("first SMS reminder - count down to: ", date)
        reminder = ReminderScheduled(
            "first_reminder",
            trigger_date_time=date,
            entities=entities,
            name="first_reminder",
            kill_on_user_message=True,
        )
        #dispatcher.utter_message("second trigger_SMS called")
        return [reminder]


# ===========================> First SMS Follow up <================================ #
def first_SMS_follow_up(lead, msg):
    """ Sends first SMS follow up messages to new Lead. """
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    # follow up messages for first engagement SMS based on time.
    messages = {
        "first_message":
        "Just a quick follow up here. Are you still interested in speaking with an attorney?",
        "next_morning":
        "Would you prefer to chat via text message or should I give you a quick call about your social security disability issue?",
        "afternoon":
        "I’d love to learn a little more about your SSD issue. Are you still interested in speaking with an attorney?",
        "two_days":
        "Hi[first name]! I don’t mean pester you so this will be my last text. Did you still want to chat with an attorney about seeing if you qualify for SSD benefits?"
    }
    if msg in messages.keys():
        the_msg = messages[msg]
    # sending SMS via Twilio
    message = client.messages.create(
        messaging_service_sid=os.getenv('MESSAGING_SERVICE_SID'),
        body=the_msg,
        from_=os.getenv('TWILIO_SMS_FROM'),
        to=lead)


class FirstMessageFollowUp(Action):
    """ Triggered by a reminder event if the lead has not responded to first SMS in 30 min"""
    def name(self) -> Text:
        return "first_SMS_follow_up"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message["entities"]
        #dispatcher.utter_message(f"Your entities: {entities}")
        print("full entities: ", entities)
        lead = entities[0]["value"]
        print("new lead: ", lead)
        #follow_up_msg = entities[1]["value"]
        first_SMS_follow_up(lead=lead, msg="first_message")
        print("first follow up SMS sent!!!")
        try:
            lead_name_slot = tracker.get_slot('lead_name')
            lead_number_slot = tracker.get_slot('lead_number')
            print("lead_name_slot: ", lead_name_slot)
            print("lead_number_slot: ", lead_number_slot)
        except exception as e:
            print("slot get error: ", e)
        # Reminder for next morning, if no response from the lead
        date = datetime.datetime.now() + datetime.timedelta(minutes=30)
        print("next morning SMS reminder current time: ",
              datetime.datetime.now())
        print("next morning reminder - count down to: ", date)
        reminder = ReminderScheduled(
            "next_morning_reminder",
            trigger_date_time=date,
            entities=entities,
            name="next_morning",
            kill_on_user_message=True,
        )

        return [reminder]


class SecondMessageFollowUp(Action):
    """ Triggered by a reminder event if the lead has not responded to first SMS in 1 day"""
    def name(self) -> Text:
        return "second_SMS_follow_up"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        lead = entities[0]["value"]
        print("new lead: ", lead)

        first_SMS_follow_up(lead=lead, msg="next_morning")
        print("Second follow up SMS sent!!!")
        try:
            lead_name_slot = tracker.get_slot('lead_name')
            lead_number_slot = tracker.get_slot('lead_number')
            print("lead_name_slot: ", lead_name_slot)
            print("lead_number_slot: ", lead_number_slot)
        except exception as e:
            print("slot get error: ", e)
        # Reminder for next morning, if no response from the lead
        date = datetime.datetime.now() + datetime.timedelta(minutes=10)

        print("next morning(second) SMS reminder current time: ",
              datetime.datetime.now())
        print("afternoon reminder(third) - count down to: ", date)
        reminder = ReminderScheduled(
            "afternoon_reminder",
            trigger_date_time=date,
            entities=entities,
            name="afternoon_reminder",
            kill_on_user_message=True,
        )

        return [reminder]


class ThirdMessageFollowUp(Action):
    """ Triggered by a reminder event if the lead has not responded to first SMS in 1 day """
    def name(self) -> Text:
        return "third_SMS_follow_up"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        lead = entities[0]["value"]
        print("new lead: ", lead)

        first_SMS_follow_up(lead=lead, msg="afternoon")
        print("third follow up SMS sent!!!")

        # Reminder for next morning, if no response from the lead
        date = datetime.datetime.now() + datetime.timedelta(minutes=10)

        print("afternoon SMS reminder(third) current time: ",
              datetime.datetime.now())
        print("two days - count down to: ", date)
        reminder = ReminderScheduled(
            "two_days_reminder",
            trigger_date_time=date,
            entities=entities,
            name="two_days_reminder",
            kill_on_user_message=True,
        )
        return [reminder]


class FourthMessageFollowUp(Action):
    """ Triggered by a reminder event if the lead has not responded to first SMS in 2days. """
    def name(self) -> Text:
        return "fourth_SMS_follow_up"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message["entities"]
        #dispatcher.utter_message(f"Your entities: {entities}")
        print("full entities: ", entities)
        lead = entities[0]["value"]
        print("new lead: ", lead)

        first_SMS_follow_up(lead=lead, msg="two_days")
        print("Fourth follow up SMS sent!!!")

        # Reminder for next morning, if no response from the lead
        date = datetime.datetime.now() + datetime.timedelta(minutes=10)

        print("fourth SMS current time (2 days): ", datetime.datetime.now())

        return []


# ===========================> Other SMS Follow up <================================ #
def other_SMS_follow_up(lead, msg):
    """ Triggered by a reminder event if the lead does not respond during the conversation conversation """
    # oncoreleads
    account_sid = os.getenv('TWILIO_ACCOUNT_SID')
    auth_token = os.getenv('TWILIO_AUTH_TOKEN')
    client = Client(account_sid, auth_token)
    # follow up messages for other SMS based on time.
    messages = {"one": "Are you still there?", "two": "Still interested?"}
    if msg in messages.keys():
        the_msg = messages[msg]
    # sending SMS via Twilio
    message = client.messages.create(
        messaging_service_sid=os.getenv('MESSAGING_SERVICE_SID'),
        body=the_msg,
        from_=os.getenv('TWILIO_SMS_FROM'),
        to=lead)
    print(message)


class OtherMessageFollowUp(Action):
    """ Triggered by a reminder event if the lead does not respond during the conversation conversation """
    def name(self) -> Text:
        return "other_SMS_follow_up"

    def run(self, dispatcher: CollectingDispatcher, tracker: Tracker,
            domain: Dict[Text, Any]) -> List[Dict[Text, Any]]:
        entities = tracker.latest_message["entities"]
        #dispatcher.utter_message(f"Your entities: {entities}")
        print(" OtherMessageFollowUp entities: ", entities)
        #"one": "Are you still there?",
        msg = "Still interested?"
        dispatcher.utter_message(text=msg)

        return []


# ===========================> Second SMS (Text Route/Option)<================================ #
class SecondMessageTrigger(Action):
    """ Sends attorney enquiry."""
    def name(self) -> Text:
        return "delay_second_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # This adds some delay to bots response
        cpm = 200
        # Second_SMS
        SMS = 'No problem, texting works. Are you currently working with an attorney to help you?'
        period = 60 * len(SMS) / cpm
        print("second_SMS typing time: ", period)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        date = datetime.datetime.now() + datetime.timedelta(seconds=period)
        print("second trigger_SMS - count down to: ", date)
        # user message
        user_message = tracker.latest_message['text']
        print("user_message: ", user_message)
        user_intent = tracker.latest_message['intent'].get('name')
        print("user_intent: ", user_intent)
        # DELAY
        reminder = ReminderScheduled(
            "second_trigger",
            trigger_date_time=date,
            entities=entities,
            name="second_trigger",
            kill_on_user_message=False,
        )
        return [reminder]


class SecondBotReponse(Action):
    """ has from an attorney ."""
    def name(self) -> Text:
        return "second_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        conversation_id = tracker.sender_id
        print("conversation_id: ", conversation_id)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        user_intent = tracker.latest_message['intent'].get('name')
        print("second user_intent: ", user_intent)
        dates = datetime.datetime.now()
        print("second response time: ", dates)
        SMS = 'No problem, texting works. Are you currently working with an attorney to help you?'
        dispatcher.utter_message(f"{SMS}")
        # Stall out Reminder
        date = datetime.datetime.now() + datetime.timedelta(minutes=10)
        print("Stall out Reminder current time: ", datetime.datetime.now())
        print("Stall out Reminder down to: ", date)

        try:
            lead_name_slot = tracker.get_slot('lead_name')
            lead_number_slot = tracker.get_slot('lead_number')
            print("lead_name_slot: ", lead_name_slot)
            print("lead_number_slot: ", lead_number_slot)
        except exception as e:
            print("slot get error: ", e)

        reminder = ReminderScheduled(
            "stall_out_reminder",
            trigger_date_time=date,
            entities=entities,
            name="stall_out_reminder",
            kill_on_user_message=True,
        )
        return [reminder]


# ===========================> Third SMS (Text Route/Option)<================================ #
class ThirdMessageTrigger(Action):
    """ Treatment from doctor enquiry ."""
    def name(self) -> Text:
        return "delay_third_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # This adds some delay to bots response
        cpm = 200
        # third_SMS
        SMS = 'Got it! Just one more question. Are you currently receiving treatment from a Doctor?'
        period = 60 * len(SMS) / cpm
        print("third_SMS typing time: ", period)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        date = datetime.datetime.now() + datetime.timedelta(seconds=period)
        print("third trigger_SMS - count down to: ", date)
        # user message
        user_message = tracker.latest_message['text']
        print("user_message: ", user_message)
        user_intent = tracker.latest_message['intent'].get('name')
        print("user_intent: ", user_intent)
        # setting reminder
        reminder = ReminderScheduled(
            "third_trigger",
            trigger_date_time=date,
            entities=entities,
            name="third_trigger",
            kill_on_user_message=False,
        )
        return [reminder]


class ThirdBotReponse(Action):
    """ Treatment from doctor enquiry ."""
    def name(self) -> Text:
        return "third_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        #name = next(tracker.get_slot("PERSON"), "someone")
        conversation_id = tracker.sender_id
        print("conversation_id: ", conversation_id)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        user_intent = tracker.latest_message['intent'].get('name')
        print("third user_intent: ", user_intent)
        dates = datetime.datetime.now()
        print("third response time: ", dates)
        #SMS = 'Got it! Just one more question. Are you currently receiving treatment from a Doctor?'
        SMS = 'Got it! Just one more question. Are you currently receiving treatment from a Doctor?'
        dispatcher.utter_message(f"{SMS}")
        # Stall out Reminder
        date = datetime.datetime.now() + datetime.timedelta(minutes=10)

        print("Stall out Reminder current time: ", datetime.datetime.now())
        print("Stall out Reminder down to: ", date)
        reminder = ReminderScheduled(
            "stall_out_reminder",
            trigger_date_time=date,
            entities=entities,
            name="stall_out_reminder",
            kill_on_user_message=True,
        )
        #dispatcher.utter_message("second trigger_SMS called")
        return [reminder]


# ===========================> Fourth SMS (Text Route/Option)<================================ #
class FourthMessageTrigger(Action):
    """ stops conversation ."""
    def name(self) -> Text:
        return "delay_fourth_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # This adds some delay to bots response
        cpm = 200
        # Second_SMS
        SMS = 'I am sorry but we can only help people who are not working with an attorney already. I wish you the best of luck.'
        period = 60 * len(SMS) / cpm
        print("forth_SMS typing time: ", period)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        date = datetime.datetime.now() + datetime.timedelta(seconds=period)
        print("forth_SMS trigger_SMS - count down to: ", date)
        # user message
        user_message = tracker.latest_message['text']
        print("user_message: ", user_message)
        user_intent = tracker.latest_message['intent'].get('name')
        print("user_intent: ", user_intent)
        # setting reminder
        reminder = ReminderScheduled(
            "fourth_trigger",
            trigger_date_time=date,
            entities=entities,
            name="fourth_trigger",
            kill_on_user_message=False,
        )

        return [reminder]


class FourthBotReponse(Action):
    """ stops conversation ."""
    def name(self) -> Text:
        return "fourth_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        #name = next(tracker.get_slot("PERSON"), "someone")
        conversation_id = tracker.sender_id
        print("conversation_id: ", conversation_id)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        user_intent = tracker.latest_message['intent'].get('name')
        print("fourth user_intent: ", user_intent)
        dates = datetime.datetime.now()
        print("fourth response time: ", dates)
        SMS = 'I am sorry but we can only help people who are not working with an attorney already. I wish you the best of luck.'
        dispatcher.utter_message(f"{SMS}")

        return []


# ===========================> Fifth SMS (Text Route/Option)<================================ #
class FifthMessageTrigger(Action):
    """  Call enquiry"""
    def name(self) -> Text:
        return "delay_fifth_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # This adds some delay to bots response
        cpm = 200
        # fifth_SMS
        SMS = 'Great. I have a few questions to see if you qualify for SSD benefits. Is now a good time for a call?'
        period = 60 * len(SMS) / cpm
        print("fifth second_SMS typing time: ", period)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        date = datetime.datetime.now() + datetime.timedelta(seconds=period)
        print("fifth trigger_SMS - count down to: ", date)
        # user message
        user_message = tracker.latest_message['text']
        print("user_message: ", user_message)
        user_intent = tracker.latest_message['intent'].get('name')
        print("user_intent: ", user_intent)

        reminder = ReminderScheduled(
            "fifth_trigger",
            trigger_date_time=date,
            entities=entities,
            name="fifth_trigger",
            kill_on_user_message=False,
        )
        return [reminder]


class FifthBotReponse(Action):
    """  Call enquiry"""
    def name(self) -> Text:
        return "fifth_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        #name = next(tracker.get_slot("PERSON"), "someone")
        conversation_id = tracker.sender_id
        print("conversation_id: ", conversation_id)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        user_intent = tracker.latest_message['intent'].get('name')
        print("fifth user_intent: ", user_intent)
        dates = datetime.datetime.now()
        print("fifth response time: ", dates)
        SMS = 'Great. I have a few questions to see if you qualify for SSD benefits. Is now a good time for a call?'
        dispatcher.utter_message(f"{SMS}")
        # Stall out Reminder
        date = datetime.datetime.now() + datetime.timedelta(minutes=10)
        print("Stall out Reminder current time: ", datetime.datetime.now())
        print("Stall out Reminder down to: ", date)
        reminder = ReminderScheduled(
            "stall_out_reminder",
            trigger_date_time=date,
            entities=entities,
            name="stall_out_reminder",
            kill_on_user_message=True,
        )
        return [reminder]


# ===========================> Sixth SMS (Text Route/Option) <================================ #
class SixthMessageTrigger(Action):
    """ Stops Conversation (lead has doctor) """
    def name(self) -> Text:
        return "delay_sixth_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # This adds some delay to bots response
        cpm = 200
        # Sixth_SMS
        SMS = 'I am sorry but we can only help people who are currently receiving treatment from a doctor. I wish you the best of luck.'
        period = 60 * len(SMS) / cpm
        print("sixth SMS typing time: ", period)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        date = datetime.datetime.now() + datetime.timedelta(seconds=period)
        print("sixth trigger_SMS - count down to: ", date)
        # user message
        user_message = tracker.latest_message['text']
        print("user_message: ", user_message)
        user_intent = tracker.latest_message['intent'].get('name')
        print("user_intent: ", user_intent)

        reminder = ReminderScheduled(
            "sixth_trigger",
            trigger_date_time=date,
            entities=entities,
            name="sixth_trigger",
            kill_on_user_message=False,
        )
        return [reminder]


class SixthBotReponse(Action):
    """ Stops Conversation (lead has doctor) """
    def name(self) -> Text:
        return "sixth_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        #name = next(tracker.get_slot("PERSON"), "someone")
        conversation_id = tracker.sender_id
        print("conversation_id: ", conversation_id)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        user_intent = tracker.latest_message['intent'].get('name')
        print("sixth user_intent: ", user_intent)
        dates = datetime.datetime.now()
        print("sixth response time: ", dates)

        SMS = 'I am sorry but we can only help people who are currently receiving treatment from a doctor. I wish you the best of luck.'
        dispatcher.utter_message(f"{SMS}")

        return []


# ===========================> Seventh SMS (Text Route/Option)<================================ #
class SeventhMessageTrigger(Action):
    """Schedules a call and alerts human agent """
    def name(self) -> Text:
        return "delay_seventh_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # This adds some delay to bots response
        cpm = 200
        # Seventh_SMS
        SMS = 'Ok great! We will give you a call within a few minutes.'
        period = 60 * len(SMS) / cpm
        print("seventh_SMS typing time: ", period)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        date = datetime.datetime.now() + datetime.timedelta(seconds=period)
        print("seventh trigger_SMS - count down to: ", date)

        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        try:
            lead_name_slot = tracker.get_slot('lead_name')
            lead_number_slot = tracker.get_slot('lead_number')
            print("lead_name_slot: ", lead_name_slot)
            print("lead_number_slot: ", lead_number_slot)
        except exception as e:
            print("slot get error: ", e)
        # user message
        user_message = tracker.latest_message['text']
        print("user_message: ", user_message)
        user_intent = tracker.latest_message['intent'].get('name')
        print("user_intent: ", user_intent)

        reminder = ReminderScheduled(
            "seventh_trigger",
            trigger_date_time=date,
            entities=entities,
            name="seventh_trigger",
            kill_on_user_message=False,
        )

        return [reminder]


class SeventhBotReponse(Action):
    """ Schedules a call and alerts human agent """
    def name(self) -> Text:
        return "seventh_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        #name = next(tracker.get_slot("PERSON"), "someone")
        conversation_id = tracker.sender_id
        print("conversation_id: ", conversation_id)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        user_intent = tracker.latest_message['intent'].get('name')
        print("seventh user_intent: ", user_intent)
        dates = datetime.datetime.now()
        print("seventh response time: ", dates)
        SMS = 'Ok great! We will give you a call within a few minutes.'
        dispatcher.utter_message(f"{SMS}")
        # getting lead details from slots
        try:
            lead_name_slot = tracker.get_slot('lead_name')
            lead_number_slot = tracker.get_slot('lead_number')
            print("lead_name_slot: ", lead_name_slot)
            print("lead_number_slot: ", lead_number_slot)
            #print("full trackerstore: ", tracker.latest_message)
        except exception as e:
            print("slot get error: ", e)
        # sending a human agent an SMS alert for immediate call
        try:
            agent = {"agent_name": " ", "agent_number": " "}
            lead = {
                "lead_name": lead_name_slot,
                "lead_number": lead_number_slot
            }
            result = call_appointment_alert(agent, lead)
            print("call_appointment_alert response: ", result)
        except Exception as e:
            print("call_appointment_alert, error: ", e)
        else:
            print("call appointment alert successful!!!")

        return []


# ===========================> Eighth SMS (Text Route/Option)<================================ #
class EighthMessageTrigger(Action):
    """Schedules a reminder, supplied with the last message's entities."""
    def name(self) -> Text:
        return "delay_eighth_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # This adds some delay to bots response
        cpm = 200
        # Second_SMS
        SMS = 'I understand. When is a good time for us to call you about your case?'
        period = 60 * len(SMS) / cpm
        print("eighth_SMS typing time: ", period)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        date = datetime.datetime.now() + datetime.timedelta(seconds=period)
        print("eighth trigger_SMS - count down to: ", date)

        # user message
        user_message = tracker.latest_message['text']
        print("user_message: ", user_message)
        user_intent = tracker.latest_message['intent'].get('name')
        print("user_intent: ", user_intent)
        #
        reminder = ReminderScheduled(
            "eighth_trigger",
            trigger_date_time=date,
            entities=entities,
            name="eighth_trigger",
            kill_on_user_message=False,
        )
        return [reminder]


class EighthBotReponse(Action):
    """Reminds the user to call someone."""
    def name(self) -> Text:
        return "eighth_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        #name = next(tracker.get_slot("PERSON"), "someone")
        conversation_id = tracker.sender_id
        print("conversation_id: ", conversation_id)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        user_intent = tracker.latest_message['intent'].get('name')
        print("eighth user_intent: ", user_intent)
        dates = datetime.datetime.now()
        print("eighth response time: ", dates)
        SMS = 'I understand. When is a good time for us to call you about your case?'
        dispatcher.utter_message(f"{SMS}")

        return []


# ===========================> CALL APPOINTMENT <================================ #
class CallScheduler(Action):
    """ Setting a Call Appointment with the agent"""
    def name(self) -> Text:
        return "action_call_schedule"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        conversation_id = tracker.sender_id
        print("conversation_id: ", conversation_id)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        user_intent = tracker.latest_message['intent'].get('name')
        print("call AP user_intent: ", user_intent)
        SMS = 'Ok great! We will give you a call'
        dispatcher.utter_message(f"{SMS}")

        try:
            lead_name_slot = tracker.get_slot('lead_name')
            lead_number_slot = tracker.get_slot('lead_number')
        except exception as e:
            print("slot get error: ", e)
        # sending a human agent an SMS alert for immediate call
        try:
            agent = {
                "agent_name": "John Anderson",
                "agent_number": "+19167671669"
            }
            lead = {
                "lead_name": lead_name_slot,
                "lead_number": lead_number_slot
            }
            #result = call_appointment_alert(agent, lead)
            lead_message = tracker.latest_message.get('text')
            print("lead_message(appointement): ", lead_message)
            result = call_appointment_reminder(agent, lead, lead_message)
            print("call_appointment_reminder: ", result)
        except Exception as e:
            print("call_appointment_alert, error: ", e)
        else:
            print("call appointment alert successful!!!")

        return []


# ===========================> CALL (Call Route/Option)<================================ #
class CallMessageTrigger(Action):
    """ Leads chooses call option"""
    def name(self) -> Text:
        return "delay_call_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        # This adds some delay to bots response
        cpm = 200
        SMS = 'Ok great! We will give you a call'
        period = 60 * len(SMS) / cpm
        print("call_SMS typing time: ", period)
        date = datetime.datetime.now() + datetime.timedelta(seconds=period)
        print("call trigger_SMS - count down to: ", date)
        entities = tracker.latest_message["entities"]
        print("full entities: ", entities)
        try:
            lead_name_slot = tracker.get_slot('lead_name')
            lead_number_slot = tracker.get_slot('lead_number')
            print("lead_name_slot: ", lead_name_slot)
            print("lead_number_slot: ", lead_number_slot)
        except exception as e:
            print("slot get error: ", e)
        # user message
        user_message = tracker.latest_message['text']
        print("user_message: ", user_message)
        user_intent = tracker.latest_message['intent'].get('name')
        print("user_intent: ", user_intent)

        reminder = ReminderScheduled(
            "call_trigger",
            trigger_date_time=date,
            entities=entities,
            name="call_trigger",
            kill_on_user_message=False,
        )
        return [reminder]


class CallReponse(Action):
    """Reminds the user to call someone."""
    def name(self) -> Text:
        return "call_SMS"

    async def run(
        self,
        dispatcher: CollectingDispatcher,
        tracker: Tracker,
        domain: Dict[Text, Any],
    ) -> List[Dict[Text, Any]]:
        conversation_id = tracker.sender_id
        print("conversation_id: ", conversation_id)
        user_intent = tracker.latest_message['intent'].get('name')
        print("call user_intent: ", user_intent)
        dates = datetime.datetime.now()
        print("call response time: ", dates)
        SMS = 'Ok great! We will give you a call'
        dispatcher.utter_message(f"{SMS}")
        # getting lead details from slots
        try:
            lead_name_slot = tracker.get_slot('lead_name')
            lead_number_slot = tracker.get_slot('lead_number')
            print("lead_name_slot: ", lead_name_slot)
            print("lead_number_slot: ", lead_number_slot)
        except exception as e:
            print("slot get error: ", e)
        # sending a human agent an SMS alert for immediate call
        try:
            agent = {"agent_name": "", "agent_number": ""}
            lead = {
                "lead_name": lead_name_slot,
                "lead_number": lead_number_slot
            }
            result = call_appointment_alert(agent, lead)
            print("call_appointment_alert response: ", result)
        except Exception as e:
            print("call_appointment_alert, error: ", e)
        else:
            print("call appointment alert successful!!!")

        return []