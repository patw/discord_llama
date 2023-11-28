import discord
import requests
import re
import random
import json
import sys

# Make sure we're starting with a model.json and an identity.json
if len(sys.argv) != 3:
        print("Usage: python discord_llama.py model.json wizard.json")
        print("Make sure you have the llama.cpp server running already and your model.json points to it.")
        print("You must also have a pre-configured bot in discord applications:")
        print("https://discord.com/developers/applications")
        sys.exit(1)

# Load the llm config from the json file provided on command line
model_file = sys.argv[1]
with open(model_file, 'r') as file:
    model = json.load(file)

# Load the identity from the json file provided on command line
bot_file = sys.argv[2]
with open(bot_file, 'r') as file:
    bot = json.load(file)

# Configure discord intent for chatting
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Removes discord IDs from strings
def remove_id(text):
    return re.sub(r'<@\d+>', '', text)

# Removes extra formatting from LLM output like \n and double spaces
def remove_extra_formatting(text):
    cleaned_text = text.replace("\n", " ") # remove newline
    cleaned_text = cleaned_text.replace("\t", " ") # remove tabs
    cleaned_text = cleaned_text.replace("  ", " ") # remove double spaces
    return cleaned_text

def format_prompt(prompt, user, question, history):
    formatted_prompt = prompt.replace("{%U}", user)
    formatted_prompt = formatted_prompt.replace("{%Q}", question)
    formatted_prompt = formatted_prompt.replace("{%H}", history)
    return formatted_prompt

# Get completion from LLM, uses a REST API call into llama.cpp running in server mode,
# This must be configured and running beforehand. Example startup with GPU accel:
# ./server -m openhermes-2.5-mistral-7b.Q6_K.gguf -t 4 -c 8192 -ngl 33 --host 0.0.0.0 --port 8086
# Point your URL to this one.
def llm_response(question):

    # Format the prompt with the proper ChatML format and control tokens
    # And inject the system prompt for the bot identity
    formatted_prompt = model["prompt_format"].replace("{%S}", bot["identity"])

    # This is the data that goes to the API call with some cleanup on the question
    formatted_prompt = formatted_prompt.replace("{%P}", remove_id(question))
    api_data = {
        "prompt": formatted_prompt,
        "n_predict": bot["tokens"],
        "temperature": bot["temperature"],
        "stop": model["stop_tokens"]
    }
    
    try:
        response = requests.post(model["llama_endpoint"], headers={"Content-Type": "application/json"}, json=api_data)
        json_output = response.json()
        output = json_output['content']
    except:
        output = "My AI model is not responding try again in a moment 🔥🐳"

    # remove annoying formatting in output
    return remove_extra_formatting(output)

@client.event
async def on_ready():
    print(f'Bot logged in as {client.user}')

@client.event
async def on_message(message):

    # Never reply to yourself
    if message.author == client.user:
        return
    
    # Grab the channel history so we can add it as context for replies, makes a nice blob of data
    history_text = ""
    channel_history = [user async for user in message.channel.history(limit=bot["history_lines"] + 1)]
    for history in channel_history:
        if remove_id(history.content) != remove_id(message.content):
            history_text = history_text + history.author.name + ": " + remove_id(history.content) + "\n"

    # Bots answer questions when messaged directly, if we do this, don't bother with triggers
    direct_msg = False
    if client.user.mentioned_in(message):
        prompt = format_prompt(bot["question_prompt"], message.author.name, remove_id(message.content), history_text)
        direct_msg = True
        print(prompt)
        await message.channel.send(llm_response(prompt))
    
    # Figure out if someone said something we should respond to, besides @message these are configured in the identity.json
    comment_on_it = False
    for word in bot["triggers"]:
        if word in message.content:
            comment_on_it = True

    # Bots can respond to trigger words at randomn, this is configured in the identity.json (eg. 0.25 = 25%)
    # But they should not respond if it was a direct message with the triggers in it
    if comment_on_it and random.random() <= float(bot["trigger_level"]) and direct_msg == False:
        prompt = format_prompt(bot["trigger_prompt"], message.author.name, remove_id(message.content), history_text)
        print(prompt)
        await message.channel.send(llm_response(prompt))

# Run the main loop
client.run(bot["discord_token"])