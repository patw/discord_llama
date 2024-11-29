# Discord Llama

Build discord bots that respond with a locally running llama.cpp server or ollama server.  This allows you to run your own models, on CPU or GPU as long as you have the hardware resources. Bots can be given identies and respond to trigger words.  They can take advantage of the discord channel history to act conversational.

It should also work on any service that has an OpenAI compatible API by changing the model.json to have a valid key and endpoint URL. 

## Local Installation

```
pip install -r requirements.txt
```

## Downloading an LLM model

Consult with the llama.cpp or ollama projects for current instructions on how to run in server mode.

## Running discord bot

* Copy the model and wizard sample files to .json files
* Paste your discord token into the wizard.json file, you can create a discord bot application here: https://discord.com/developers/applications
* Join your bot to the server with the proper chat permissions
* Run the following:

```
python discord_llama.py model.json wizard.json
```

### Configuration Parameters

#### model.json
* base_url - This is the url for your ollama or llama.cpp server running the model
* api_key - This can be anything for local models, as it won't validate. Use a proper API key for other services.
* model - Model name, used only for running on hosted services.  For llama.cpp or ollama just use anything

#### wizard.json
* discord_token - The discord token for the bot, you can make one following this:  https://discordpy.readthedocs.io/en/stable/discord.html#discord-intro
* identity - This is where your bot's personality comes from you can get very creative with prompt engineering here and make the bot anything you want
* triggers - These are words the bot will respond to if they show up in any conversation.
* trigger_level - This is how often the bot will respond to triggers 1.0 = 100%, 0.25 = 25%.  Anything > 0.5 is annoying
* temperature - This is the LLM temperature which you can think of as the creativity.  0.7 is good for chatbots.
* history_lines - This is how much history it can see when answering questions.  Too much and it can get confused.
* question_prompt - This is the prompt it processes when @ msged a question
* trigger_prompt - This is the prompt it processes when it's commenting on a trigger word.


### Running multiple bots

Each bot needs it's own Discord application and key generated.  Once you do that, create multiple bot identity json files like the 
sample wizard.json.  Create multiple .sh or .bat files to start each one up.

### Known issues

* The bot will use your discord account name, not the alias you've set for the server.  I tried to get this working with display_name but it doesn't seem possible to get that in the history object.