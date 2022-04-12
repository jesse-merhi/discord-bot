import discord
from discord.ext import commands, tasks
import random
import time
import json
import requests
import re
import datetime
import pandas as pd
import requests
from riotwatcher import LolWatcher, ApiError
intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix = ".", intents=intents)

@client.event
async def on_ready():
    test.start()
    print('Bot is ready.')

@tasks.loop(seconds= 60)
async def test():
    f = open('userscores.json')
    scores = json.load(f)
    await get_streamers()
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.type == discord.ChannelType.voice:
                for member in channel.members:
                    if str(member.id) in scores.keys():
                        scores[str(member.id)] += 1
                    else:
                        scores[str(member.id)] = 1
    with open('userscores.json', 'w') as f:
        json.dump(scores, f)           
    f.close()
    
@tasks.loop(seconds= 120)
async def streamtimes():
    await get_streamers() 


@client.command()
async def points(ctx):
    f = open('userscores.json')
    scores = json.load(f)
    if str(ctx.author.id) in scores.keys():
        personal_points = scores[str(ctx.author.id)]
        await ctx.send(f"You have {personal_points} points")
    else:
        await ctx.send(f"You have not joined a voice channel yet.")

@client.command()
async def addstream(ctx, streamer_name):
    f = open('streamers.json')
    streamers_data = json.load(f)
    streamer_found = 0
    for streamer in streamers_data:
        if streamer == streamer_name:
            streamer_found = 1
            user_found = 0
            for user in streamers_data[streamer]:
                if user == str(ctx.author.id):
                    user_found = 1
            if user_found == 0:
                streamers_data[streamer].append(str(ctx.author.id))
            else:
                await ctx.send(f"Streamer: {streamer_name} already in your notifications")
                f.close()
                return
    if streamer_found == 0:
        streamers_data[streamer_name] = [str(ctx.author.id)]
    with open('streamers.json', 'w') as f:
        json.dump(streamers_data, f)           
    f.close()

    await ctx.send(f"Streamer: {streamer_name} added to your notifications")

@client.command()
async def liststream(ctx):
    f = open('streamers.json')
    streamers_data = json.load(f)
    embed = discord.Embed(
        colour = discord.Colour.blue()
    )
    embed.set_author(name='List of Streamers in Your Notifications:')
    amount = 1
    for streamer in streamers_data:
        for user in streamers_data[streamer]:
            print(user == ctx.author.id,user,ctx.author.id)
            if int(user) == ctx.author.id:
                embed.add_field(name = amount,value = str(streamer), inline = False)
                amount+=1
    await ctx.send(embed = embed)
    f.close()

@client.command()
async def remstream(ctx, streamer_name):
    f = open('streamers.json')
    streamers_data = json.load(f)
    streamer_found = 0
    for streamer in streamers_data:
        if streamer == streamer_name:
            streamer_found = 1
            streamers_data[streamer].remove(str(ctx.author.id))
    if streamer_found == 0:
        streamers_data[streamer_name] = [str(ctx.author.id)]
    with open('streamers.json', 'w') as f:
        json.dump(streamers_data, f)           
    f.close()

    await ctx.send(f"Streamer: {streamer_name} deleted from your notifications")
async def get_streamers():
    f = open('streamers.json')
    streamers = json.load(f)
    print(streamers)
    for (streamer,users) in streamers.items():
        print(streamer,users)
        for user in users:
            if user != None:
                await check_live(streamer, user)

async def check_live(streamer,user):
    url = 'https://id.twitch.tv/oauth2/token'
    myobj = {
        'client_id': 'wcj55ij8oorl3islaexzvquzwhd5it',
        'client_secret': '9kugeh6m5tubziqtjfquptez5amoc9',
        'grant_type': 'client_credentials',
    }

    x = requests.post(url, data = myobj)

    url = f'https://api.twitch.tv/helix/streams?user_login={streamer}'
    header = {
        'Authorization' : 'Bearer ' + x.json()['access_token'],
        'Client-Id': 'wcj55ij8oorl3islaexzvquzwhd5it'
    }

    x = requests.get(url, headers = header)
    if x.json()["data"] != []:
        twitch_time = x.json()["data"][0]["started_at"]
        start_time = datetime.datetime.strptime(twitch_time, '%Y-%m-%dT%H:%M:%SZ')
        if start_time + datetime.timedelta(minutes = 202) > datetime.datetime.utcnow():
            await client.get_user(int(user)).send(f'Hi {client.get_user(int(user)).name}! {streamer} Just went live at https://www.twitch.tv/{streamer}')


@client.command()
async def leaderboard(ctx):
    f = open('userscores.json')
    scores = json.load(f)
    print(sorted(scores.items()))
    scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    embed = discord.Embed(
        colour = discord.Colour.blue()
    )
    embed.set_author(name='Leaderboard:')
    for (key,value) in scores:
        user = client.get_user(int(key))
        if user != None:
            embed.add_field(name = str(client.get_user(int(key)).name), value = value, inline = False)
    await ctx.send(embed =embed)
    f.close()


@client.command()
async def mastery(ctx, *args):
    names = args[1:]
    names = list(set([x for x in names if names.count(x) >= 1]))
    if not re.search("[0-9]+", args[0]):
        await ctx.send("Incorrect command syntax: .mastery {number of champs displayed} {account names}")
        return
    if len(args) < 2:
        await ctx.send("Incorrect command syntax: .mastery {number of champs displayed} {account names}")
        return
    if len(args) > 11:
        await ctx.send("Incorrect usage: Account limit is 10")
        return
    if int(float(args[0])) > 25:
        await ctx.send("Incorrect usage: Max list is only 25 champions")
        return
    
    print(names)
    # golbal variables
    api_key = 'RGAPI-f9b46e05-9dba-4190-a7f7-e7aa077575cb'
    watcher = LolWatcher(api_key)
    my_region = 'oc1'
    collective = {}
    message1 = await ctx.send(f"Collecting Data...")
    for name in names:
        try:
            sum = watcher.summoner.by_name(my_region, name)
        except ApiError as err:
            await message1.delete()
            await ctx.send(f"Summoner with name {name} not found, please try again.")
            return
        me = watcher.champion_mastery.by_summoner(my_region, sum["id"])
        newmsg = f"Collecting Data on {name}"
        await message1.edit(content=newmsg)
        for champion in me:
            dictionary = {}
            if str(champion["championId"]) in collective:
                collective[str(champion["championId"])] += champion["championPoints"]
            else:
                collective[str(champion["championId"])] = champion["championPoints"]
    print(sorted(collective.items(), key=lambda item: item[1], reverse = True))
    collective = sorted(collective.items(), key=lambda item: item[1], reverse = True)
    version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    currversion = version.json()[0]
    champs = requests.get(f'http://ddragon.leagueoflegends.com/cdn/{currversion}/data/en_US/champion.json')
    embed = discord.Embed(
    colour = discord.Colour.blue()
    )
    await message1.edit(content="Assigning Mastery Ids")
    author = str(" + ".join(str(i) for i in names))
    embed.set_author(name=f'Summoner {author} Mastery:')
    max = args[0]
    if len(collective) < 25:
        max = len(collective)
    for i in range(0,int(float(max))):
        for champ in champs.json()["data"]:
            if champs.json()["data"][champ]["key"] == str(collective[i][0]):
                embed.add_field(name = champs.json()["data"][champ]["name"], value = str(collective[i][1]), inline = False)
    
    await message1.delete()
    await ctx.send(embed =embed)
client.run('ODAzMjIzNDUxMDc3NzA1NzQ4.YA6qIQ.fwEKRRqf_t2yL-P4VKntSHNVbxY')   