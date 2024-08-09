# chat.py
Very simple command line client for OpenAI API LLMs (ChatGPT 4)

Default config expected in a file called chat_config.json, example:
```
{ "url":"https://api.openai.com/v1/chat/completions",
"api_key":"ENV_OPENAI_API_KEY",
"model": "gpt-3.5-turbo",
"available_models": [
    "gpt-4o-mini","gpt-3.5-turbo"
    ],
"role":"user",
"temperature":"0.5" }
```
It is possible to store the API key directly in the config file but for security it is recommended to use an environment variable instead.
Set the `api_key` in the config file to value `ENV_OPENAI_API_KEY` then and provide an environment variable called `OPENAI_API_KEY` with the key.
To start chatting  in windows open a command shell and type:
```
set OPENAI_API_KEY=bearer sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
python3 chat.py
```


User Commands:
 - `!exit`:      Exit chat
 - `!debug`:     Print last response json from LLM
 - `!models`:    Show available models
 - `!T=X`:       Set temperature to X
 - `!model=m`:   Set model to m (m Integer, see !models command)
 - `!list_configs`: List config files (json) in current folder
 - `!load_config` <filename>:    Load configfile
 - `!save_config` <filename>:    Save current config 
 - `!help`:      Print this text

