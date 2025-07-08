import os
import json
import uuid
from flask import Flask, request, jsonify, session, render_template_string
import requests

# Load config
try:
    with open(os.environ.get("CHAT_PY_DEFAULT_CONF", "chat_config.json")) as f:
        config = json.load(f)
except IOError as e:
    print(f"Error loading configfile: {e}")
    exit(1)

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-me")

# Store contexts per user session
contexts = {}


def send_payload(content, cfg, ctx):
    if cfg["api_key"] == "ENV_OPENAI_API_KEY":
        api_key = os.environ.get("OPENAI_API_KEY", "")
    else:
        api_key = cfg["api_key"]

    ctx.append({
        "role": cfg["role"],
        "content": content,
        "temperature": cfg["temperature"],
    })

    if len(ctx) > 2 * cfg["context_length"]:
        ctx = ctx[2:]

    headers = {
        "Content-Type": "application/json",
        "Authorization": api_key,
    }
    payload = {
        "model": cfg["model"],
        "messages": ctx,
    }

    response = requests.post(cfg["url"], headers=headers, json=payload)
    return response.json(), ctx


def process_response(response, ctx):
    try:
        message_content = response['choices'][0]['message']['content']
        ctx.append({
            "role": response['choices'][0]['message']['role'],
            "content": message_content,
        })
    except KeyError as e:
        message_content = f"Unexpected response structure: {e}"
    return message_content, ctx


@app.before_request
def ensure_user():
    session.permanent = True
    if 'user_id' not in session:
        session['user_id'] = str(uuid.uuid4())


@app.route('/')
def index():
    html = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Chat.py Web</title>
<style>
body { font-family: Arial, sans-serif; margin: 40px; }
#chat { border: 1px solid #ccc; padding: 10px; height: 300px; overflow-y: scroll; }
.user { color: blue; margin-top: 10px; }
.bot { color: green; margin-bottom: 10px; }
</style>
</head>
<body>
<div id="chat"></div>
<input id="msg" type="text" style="width:80%" />
<button onclick="send()">Send</button>
<script>
async function send() {
  const input = document.getElementById('msg');
  const text = input.value;
  if(!text) return;
  const chat = document.getElementById('chat');
  chat.innerHTML += '<div class="user">'+text+'</div>';
  input.value='';
  const res = await fetch('/chat', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({message:text})
  });
  const data = await res.json();
  chat.innerHTML += '<div class="bot">'+data.reply+'</div>';
  chat.scrollTop = chat.scrollHeight;
}
</script>
</body>
</html>'''
    return render_template_string(html)


@app.route('/chat', methods=['POST'])
def chat_route():
    user_id = session['user_id']
    msg = request.json.get('message', '')
    ctx = contexts.get(user_id, [])
    response_json, ctx = send_payload(msg, config, ctx)
    reply, ctx = process_response(response_json, ctx)
    contexts[user_id] = ctx
    return jsonify({'reply': reply})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
