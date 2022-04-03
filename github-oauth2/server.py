import requests
from flask import Flask, request

from setting import *

app = Flask(__name__)

URL = "https://github.com/login/oauth/authorize?client_id={client_id}&scope={scope}&redirect_uri={redirect_uri}"


@app.route('/')
def index():
    url = URL.format(client_id=client_id, scope=scope, redirect_uri=redirect_uri)
    html = f'''
    <h1>Hello World!</h1>
    <a href="{url}">
    <button>Login with Github</button>
    </a>
    '''
    return html


@app.route('/callback')
def callback():
    code = request.args.get('code')
    url = "https://github.com/login/oauth/access_token"
    response = requests.post(url, data={
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "redirect_uri": "http://49.232.185.170:8080/callback"
    }, headers={
        "Accept": "application/json"
    })
    print(response.text)
    access_token = response.json()['access_token']
    url = "https://api.github.com/user?access_token=" + access_token
    headers = {
        "Authorization": "token " + access_token
    }
    response = requests.get(url, headers=headers)
    print(response.text)

    return response.text


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=8080, debug=True)
