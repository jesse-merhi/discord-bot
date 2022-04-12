import requests

url = 'https://id.twitch.tv/oauth2/token'
myobj = {
    'client_id': 'wcj55ij8oorl3islaexzvquzwhd5it',
    'client_secret': '9kugeh6m5tubziqtjfquptez5amoc9',
    'grant_type': 'client_credentials',
}

x = requests.post(url, data = myobj)

print(x.text)

url = 'https://api.twitch.tv/helix/streams?user_login=wombabe'
header = {
    'Authorization' : 'Bearer ' + x.json()['access_token'],
    'Client-Id': 'wcj55ij8oorl3islaexzvquzwhd5it'
}

print(header)

x = requests.get(url, headers = header)

print(x.text)