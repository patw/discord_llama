# Discord Llama

Build discord bots that respond with a locally running llama.cpp server.  This allows you to run your own models, on CPU or GPU
as long as you have the hardware resources. Bots can be given identies and respond to trigger words.  They can take advantage
of the discord channel history to act conversational.

## Local Installation

```
pip install -r requirements.txt
```

## Downloading an LLM model

We highly recommend OpenHermes 2.5 Mistral-7b fine tune for this task, as it's currently the best (Nov 2023) that
we've tested personally.  You can find different quantized versions of the model here:

https://huggingface.co/TheBloke/OpenHermes-2.5-Mistral-7B-GGUF/tree/main

I'd suggest the Q6 quant for GPU and Q4_K_M for CPU

## Running a model on llama.cpp in API mode

### Windows

Go to the llama.cpp releases and download either the win-avx2 package for CPU or the cublas for nvidia cards:

https://github.com/ggerganov/llama.cpp/releases

Extract the files out and run the following for nvidia GPUs:
```
server.exe -m <model>.gguf -t 4 -c 2048 -ngl 33 --host 0.0.0.0 --port 8086
```

For CPU only:
```
server.exe -m <model>.gguf -c 2048 --host 0.0.0.0 --port 8086
```

Replace <model> with whatever model you downloaded and put into the llama.cpp directory

### Linux, MacOS or WSL2
 
Follow the install instructions for llama.cpp at https://github.com/ggerganov/llama.cpp

Git clone, compile and run the following for GPU:
```
./server -m models/<model>.gguf -t 4 -c 2048 -ngl 33 --host 0.0.0.0 --port 8086
```

For CPU only:
```
./server -m models/<model>.gguf -c 2048 --host 0.0.0.0 --port 8086
```

Replace <model> with whatever model you downloaded and put into the llama.cpp/models directory

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
* llama_endpoint - Usually localhost, but if you have a dedicated machine to run it on change URL to that one
* prompt_format - For instruct tuned models, the format provided is ChatML format which works fine with OpenHermes
* stop_tokens - Stopping token for generation, should match the model's prompt format

#### wizard.json
* discord_token - The discord token for the bot, you can make one following this:  https://discordpy.readthedocs.io/en/stable/discord.html#discord-intro
* identity - This is where your bot's personality comes from you can get very creative with prompt engineering here and make the bot anything you want
* triggers - These are words the bot will respond to if they show up in any conversation.
* trigger_level - This is how often the bot will respond to triggers 1.0 = 100%, 0.25 = 25%.  Anything > 0.5 is annoying
* temperature - This is the LLM temperature which you can think of as the creativity.  0.7 is good for chatbots.
* tokens - This is the number of words it can output.  You don't want it writing 10 page novels in discord, so keep it low
* history_lines - This is how much history it can see when answering questions.  Too much and it can get confused.
* question_prompt - This is the prompt it processes when @ msged a question
* trigger_prompt - This is the prompt it processes when it's commenting on a trigger word.


### Running multiple bots

Each bot needs it's own Discord application and key generated.  Once you do that, create multiple bot identity json files like the 
sample wizard.json.  Create multiple .sh or .bat files to start each one up.

### Known issues

* The bot will use your discord account name, not the alias you've set for the server.  I tried to get this working with display_name but it doesn't seem possible to get that in the history object.