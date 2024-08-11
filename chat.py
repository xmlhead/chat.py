# Simple Chat Client for OpenAI API
import requests
import json
import os

_DEBUG=False

def send_payload(content):
    global config, context

    context.append({
                "role": config["role"],
                "content": content,
                "temperature": config["temperature"]
            })
    if len(context)-1>2*config["context_length"]:
        
        context=context[2:]
    headers = {
        "Content-Type": "application/json",
        "Authorization": config["api_key"],
    }
    payload = {
    
     "model": config["model"],
        "messages": context        
        
    }
    
    if _DEBUG:
        print(f"\033[31mSENT: {payload}\033[0m\n")
    
  
    response = requests.post(config["url"], headers=headers, json=payload)
   
    return response.json()

def process_response(response):
    global config, context
    try:
        message_content = response['choices'][0]['message']['content']
        print(message_content.replace("\\n", "\n"))
        context.append({"role":response['choices'][0]['message']['role'],"content":message_content})
        #print("---------------------------------------------------------------------------------------------------")
    except KeyError as e:
        print(f"Unexpected response structure: {e}")

helpstring = """

Very simple command line client for OpenAI API LLMs (like ChatGPT-4)
See https://github.com/xmlhead/chat.py for more info.

User Commands:
  !exit:      Exit chat
  !debug:     Print last response json from LLM
  !models:    Show available models
  !T=X:       Set temperature to X
  !model=m:   Set model to m (m Integer, see !models command)
  !context_length=n: Integer, number of previous messages put in the request for context
  !new_context: Start new dialog
  !list_configs: List config files (json) in current folder
  !load_config <filename>:    Load configfile
  !save_config <filename>:    Save current config 
  !print_config: Print current config
  !help:      Print this text

"""

def load_config(configfilename):
    global config
    try:
        with open(configfilename, 'r') as configfile:
            config = json.load(configfile)
            configfile.close()
            print(f"Loaded Configfile: {configfilename}.")
    except IOError as e:
        print(f"Error loading configfile: {e}")
        exit
    # read API KEY from ENV Variable if set
    if config["api_key"] == "ENV_OPENAI_API_KEY":
        config["api_key"] = os.environ["OPENAI_API_KEY"]
    print("OpenAI Chat Client, type !help for help.")
    
def save_config(configfilename):
    global config
    try:
        with open(configfilename, 'w') as configfile:
            json.dump(config, configfile, indent=2)
            configfile.close()
            print(f"Saved Configfile: {configfilename}.")
    except IOError as e:
            print(f"Error saving configfile: {e}")
            exit


def main():
    global config, context
    load_config('chat_config.json')
    
    response=''
    context=[]
    while True:
        print("---"+config["model"]+"----T="+config["temperature"]+"----------------------------------------------------------")
        user_input = input(">")
        if user_input.startswith("!"):
            if user_input == "!exit": 
                print("Exiting chat...")
                break
            elif user_input == "!debug":
                if response!='':
                    print(f"\033[31mRECIEVED: {json.dumps(response, indent=4)}\033[0m\n")
                else:
                    print("Send message to LLM first.")    
                    
            elif user_input=="!models":
                print("Available models:")
                for m in range(len(config["available_models"])):
                    print(m+1,config["available_models"][m])
            elif user_input.startswith("!T="):
                config["temperature"]=user_input.replace("!T=","")
                print("Set temperature to ",config["temperature"]+".")
            elif user_input.startswith("!model="):
               m= int(user_input.replace("!model=",""))-1
               if m>=0 and m< len(config["available_models"]):
                    config["model"]=config["available_models"][m]
                    print("Set model to ",config["model"]+".")    
               else:
                    print("Model number must be between 1 and", str(len(config["available_models"]))+".")
            elif user_input.startswith("!context_length="):
               n= int(user_input.replace("!context_length=",""))
               if n>0  and n < config["max_context_length"]:
                    config["context_length"]=n
                    print("Set context length to ",str(config["context_length"])+".")   
                    print("New context started.")
                    context=[]
               else:
                    print("Context length must be between 1 and", str(config["max_context_length"])+".")
            elif user_input=="!new_context":
                    print("New context started.")
                    context=[]
            elif user_input=="!help":
                print(helpstring)
            elif user_input.startswith("!load_config"):
                configfilename=user_input.split(" ")[1]
                load_config(configfilename)
                pass
            elif user_input.startswith("!save_config"):
                configfilename=user_input.split(" ")[1]
                save_config(configfilename)
            elif user_input == "!print_config":    
                print(json.dumps(config, indent=2))
            elif user_input=="!list_configs":
                 for f in os.listdir():
                    if f.endswith('.json'):
                        print(f)
            else:
                print(f"Unknown command: {user_input}\n Type !help for help")
        else:
            response = send_payload(user_input)
            process_response(response)

if __name__ == "__main__":
    main()
