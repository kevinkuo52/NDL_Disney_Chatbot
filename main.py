import os
import time
import re
from slackclient import SlackClient
import credentials
import json
import random
import tf_idf


# instantiate Slack client
slack_client = SlackClient(credentials.SLACK_TOKEN)
# starterbot's user ID in Slack: value is assigned after the bot starts up
starterbot_id = None
#test1
# constants
RTM_READ_DELAY = 1 # 1 second delay between reading from RTM
MENTION_REGEX = "^<@(|[WU].+?)>(.*)"

def reset_bot_state():
    with open("bot_state.json", "r") as jsonFile:
        bot_state = json.load(jsonFile)
        bot_state["character_choice"] = ""
        bot_state["next_response"] = ""
        bot_state["next_response_Flag"] = "False"
    with open("bot_state.json", "w") as jsonFile:
        json.dump(bot_state, jsonFile)


reset_bot_state()

def parse_bot_commands(slack_events):
    """
        Parses a list of events coming from the Slack RTM API to find bot commands.
        If a bot command is found, this function returns a tuple of command and channel.
        If its not found, then this function returns None, None.
    """
    for event in slack_events:
        if event["type"] == "message" and not "subtype" in event:
            user_id, message = parse_direct_mention(event["text"])
            if user_id == starterbot_id:
                return message, event["channel"]
            elif event["text"][0:3].lower() == "bot":
                return event["text"][4:], event["channel"]
    return None, None

def parse_direct_mention(message_text):
    """
        Finds a direct mention (a mention that is at the beginning) in message text
        and returns the user ID which was mentioned. If there is no direct mention, returns None
    """
    matches = re.search(MENTION_REGEX, message_text)
    # the first group contains the username, the second group contains the remaining message
    return (matches.group(1), matches.group(2).strip()) if matches else (None, None)

def handle_command(command, channel):
    """
        Executes bot command if the command is known
    """
    command = command.lower()


    simba_default = ["I won’t tell you~~","why are you asking?", "I am going to be king, so I am cool!", "what do you mean?",\
    "You said… what? Whoaaa!","sing with me Hakuna Matata~~~","I can’t wait to be king!!"]
    scar_default = ["Ha Ha Ha Ha you tried", "smiles sinisterly", "Everyone is so stupid", "Ridiculous", "I don’t care about anyone"]
    with open("bot_state.json", "r") as jsonFile:
        bot_state = json.load(jsonFile)
    response = None
    default_response = None

    if command == "be simba":
        bot_state["character_choice"] = "simba"
        response = "Simba here! What’s your name??"
        bot_state["next_response_Flag"] = "False"
    elif command == "be scar":
        bot_state["character_choice"] = "scar"
        response = " I am Scar, the one who should be king of Pride Rock! And you are?"
        bot_state["next_response_Flag"] = "False"
    elif bot_state["character_choice"] == "":
        response = "Please pick a character first. I can be Simba or Scar! \n Type: \"be simba\" " \
                   "or \"be scar\" without the quotation marks"
    elif bot_state["next_response_Flag"] == "True":
        response = bot_state["next_response"]
        bot_state["next_response_Flag"] = "False"
    else:
        if bot_state["character_choice"] == "simba":
            response = retrieve_simba_response(command)
        else:
            response = retrieve_scar_response(command)
    if response is None:
        response = tf_idf.previous_chats(command)
        if response == "":
            response = None
        elif response == "live_chat":
            response = None
        #resub <character_name> token with current personality name
        elif "<character_name>" in response:
            response = response.split("<character_name>")
            rebuild = ""
            for parts in response[:-1]:
                rebuild += parts + bot_state["character_choice"]
            response = rebuild + response[-1]

    if bot_state["character_choice"] == "simba":
        default_response = random.choice(simba_default)
    else:
        default_response = random.choice(scar_default)
    response = response or default_response
    if "<random>" in response:
        response = random.choice(response.split("<random>"))
    if "<next_response>" in response:
        response, bot_state["next_response"] = response.split("<next_response>")
        bot_state["next_response_Flag"] = "True"
    if bot_state["character_choice"] == "simba":
        response = "Simba: "+ response
    elif bot_state["character_choice"] == "scar":
        response = "Scar: "+ response

    with open("bot_state.json", "w") as jsonFile:
        json.dump(bot_state, jsonFile)

    # Sends the response back to the channel
    slack_client.api_call(
        "chat.postMessage",
        channel=channel,
        text=response
    )


def get_response(user_input, corpus):
    for key in corpus.keys():
        keywords = key.split('<s>')
        keymach = 0
        for keyword in keywords:
            if " " in keyword and keyword.lower() in user_input.lower():
                keymach += 1
            elif keyword.lower() in user_input.lower().split(" "):
                keymach += 1
            else:
                break
        if keymach == len(keywords):
            return corpus[key]
    return None


def retrieve_simba_response(user_input):
    with open("simba_corpus.json", "r") as jsonFile:
        corpus = json.load(jsonFile)
    return get_response(user_input, corpus)


def retrieve_scar_response(user_input):
    with open("scar_corpus.json", "r") as jsonFile:
        corpus = json.load(jsonFile)
    return get_response(user_input, corpus)

if __name__ == "__main__":
    if slack_client.rtm_connect(with_team_state=False):
        print("Starter Bot connected and running!")
        # Read bot's user ID by calling Web API method `auth.test`
        starterbot_id = slack_client.api_call("auth.test")["user_id"]
        while True:
            command, channel = parse_bot_commands(slack_client.rtm_read())
            if command:
                handle_command(command, channel)
            time.sleep(RTM_READ_DELAY)
    else:
        print("Connection failed. Exception traceback printed above.")
