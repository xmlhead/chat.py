# chat.py
Very simple command line client for OpenAI API LLMs (ChatGPT 4)

Default config expected in a file called chat_config.json, example:
```
{ "url":"https://endpoint.com/chat/completions",
"api_key":"ENV_OPENAI_API_KEY",
"model": "anthropic-claude-3-5-sonnet",
"available_models": [
    "anthropic-claude-3-5-sonnet", 
    "anthropic-claude-3-haiku", 
    "llama3-70b", 
    "mistral-large"
    ],
"role":"user",
"temperature":"0.5" }

It is possible to store the API key in the config file but recommended to use an environment variable instead.
Set the `api_key` to `ENV_OPENAI_KEY` then and provide an environment variable called `OPENAI_API` with the key.
For windows open a command shell and type:
```
set OPENAI_API_KEY=bearer sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
python3 chat.py
```
to start chatting.

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

Note: API key can be set directly but it is recommended to keep the setting 
and provie an environment variable called  OPENAI_API_KEY for security reasons. 
