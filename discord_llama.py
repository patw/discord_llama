import discord
import re
import random
import json
import sys

# Use local models with the OpenAI library and a custom baseurl
from openai import OpenAI

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
    llm_config = json.load(file)

# Load the identity from the json file provided on command line
bot_file = sys.argv[2]
with open(bot_file, 'r') as file:
    bot_config = json.load(file)

# Configure discord intent for chatting
intents = discord.Intents.default()
intents.message_content = True
client = discord.Client(intents=intents)

# Removes discord IDs from strings
def remove_id(text):
    return re.sub(r'<@\d+>', '', text)

# Remove any broadcasts
def filter_mentions(text):
    pattern = r'[@]?(\b(here|everyone|channel)\b)'
    filtered_text = re.sub(pattern, '', text)
    return filtered_text

def format_prompt(prompt, user, question, history):
    formatted_prompt = prompt.replace("{user}", user)
    formatted_prompt = formatted_prompt.replace("{question}", question)
    formatted_prompt = formatted_prompt.replace("{history}", history)
    return formatted_prompt

# Split messages into 2000 character chunks (discord's message limit)
def split_message(message):
    return [message[i:i+2000] for i in range(0, len(message), 2000)]

# Call llm using the llm configuration
def llm_local(prompt):
    client = OpenAI(api_key=llm_config["api_key"], base_url=llm_config["base_url"])
    messages=[{"role": "system", "content": bot_config["identity"]},{"role": "user", "content": prompt}]
    response = client.chat.completions.create(model=llm_config["model"], max_tokens=2000, temperature=bot_config["temperature"], messages=messages)
    return response.choices[0].message.content

@client.event
async def on_ready():
    print(f'Bot logged in as {client.user}')

@client.event
async def on_message(message):

    # Never reply to yourself
    if message.author == client.user:
        return
    
    # Grab the channel history so we can add it as context for replies, makes a nice blob of data
    history_list = []
    channel_history = [user async for user in message.channel.history(limit=bot_config["history_lines"] + 1)]
    for history in channel_history:
        if remove_id(history.content) != remove_id(message.content):
            history_list.append(history.author.name + ": " + remove_id(history.content))

    # Reverse the order of the history so it looks more like the chat log
    # Then join it into a single text blob
    history_list.reverse()
    history_text = '\n'.join(history_list)

    # Bots answer questions when messaged directly, if we do this, don't bother with triggers
    direct_msg = False
    if client.user.mentioned_in(message):
        prompt = format_prompt(bot_config["question_prompt"], message.author.name, remove_id(message.content), history_text)
        direct_msg = True
        bot_response = filter_mentions(llm_local(prompt))
        message_chunks = split_message(bot_response)
        for chunk in message_chunks:
            await message.channel.send(chunk)
    
    # Figure out if someone said something we should respond to, besides @message these are configured in the identity.json
    comment_on_it = False
    for word in bot_config["triggers"]:
        if word in message.content:
            comment_on_it = True

    # Bots can respond to trigger words at randomn, this is configured in the identity.json (eg. 0.25 = 25%)
    # But they should not respond if it was a direct message with the triggers in it
    if comment_on_it and random.random() <= float(bot_config["trigger_level"]) and direct_msg == False:
        prompt = format_prompt(bot_config["trigger_prompt"], message.author.name, remove_id(message.content), history_text)
        bot_response = filter_mentions(llm_local(prompt))
        message_chunks = split_message(bot_response)
        for chunk in message_chunks:
            await message.channel.send(chunk)

# Run the main loop
client.run(bot_config["discord_token"])