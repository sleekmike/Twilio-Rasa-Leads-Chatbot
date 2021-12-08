from twilio.rest import Client
import requests
import os

# ===========================> Getting Environments Variables <================================
twilio_account_sid = os.getenv('TWILIO_ACCOUNT_SID')
twilio_auth_token = os.getenv('TWILIO_AUTH_TOKEN')
twilio_number = os.getenv('TWILIO_SMS_FROM')
messaging_service_sid = os.getenv('MESSAGING_SERVICE_SID')

print("twilio_account_sid: ", twilio_account_sid)
print("twilio_auth_token: ", twilio_auth_token)
print("twilio_number: ", twilio_number)
print("messaging_service_sid: ", messaging_service_sid)


# ===========================> First Engagement <================================ #
def first_engagement(lead):
    """ Sends first engagement message to the new lead. """
    # lead details
    lead_name = lead["lead_name"]
    number = lead["number"]
    #url = "localhost:5005"
    #linker = '165.232.137.196:5005'
    linker = '<YOU DOMAIN NAME HERE>:5005'
    #linker = 'b68a-165-232-137-196.ngrok.io'
    url = f"http://{linker}/conversations/{number}/trigger_intent?output_channel=latest"
    # lead payload
    payload = {
        "name": "send_first_SMS",
        "entities": {
            "lead_number": number,
            "lead_name": lead_name
        },
    }
    # sending SMS request
    headers = {"Content-Type": "application/json"}
    response = requests.request("POST", url, headers=headers, json=payload)
    # result1 = response.json
    result = response
    return result


# New Leads (ADD Lead Details Here)
mike1 = {"number": "+2348035469768", "lead_name": "mike"}
david = {"number": "+19167671669", "lead_name": "david pane"}
abram = {"number": "+19163060375", "lead_name": "Abram Flipper"}
mike2 = {"number": "+19162510635", "lead_name": "Mike miles"}
mike3 = {"number": "+2348133120975", "lead_name": "mike jones"}
shailendra = {"number": "+19165181950", "lead_name": "shailendra gupta"}

#result = first_engagement(mike3)
result = first_engagement(david)
print("result:", result)