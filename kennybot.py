from doctest import master
import discord
from discord.ext import commands, tasks
import random
import requests
import time
import json
import datetime
import re
import sys
from riotwatcher import LolWatcher, ApiError

intents = discord.Intents.default()
intents.members = True
client = commands.Bot(command_prefix=".", intents=intents, help_command=None)
kenny_quotes = [
    "I love my son damon",
    "*Dabs*",
    "Hey guys im Kenny",
    "I like dirtbikes.",
    "They arent motorbikes! They are dirtbikes.",
]


@client.event
async def on_ready():
    test.start()
    print("Bot is ready.")


@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        await message.channel.send(
            f"Hello I am Kenny Bot type .help to see my list of commands."
        )
    elif message.type == discord.MessageType.new_member:
        print(message)
        role = discord.utils.get(message.author.guild.roles, name="cringelords")
        await message.author.add_roles(role)
    elif "gamon" in message.content.lower() or "gaymon" in message.content.lower():
        await message.channel.send(f"THAT IS VERY RUDE! HIS NAME IS DAMON!")
    else:
        for item in ["gamin' damon", "gaming damon", "gamin damon", "gaymen"]:
            if item in message.content.lower() and message.author != client.user:
                await message.channel.send(
                    f"Did someone say {item}? The best gamer ALIVE! thats my damon :sunglasses:"
                )
    await client.process_commands(message)


@tasks.loop(seconds=60)
async def test():
    f = open("userscores.json")
    scores = json.load(f)
    print(scores)
    await get_streamers()
    for guild in client.guilds:
        for channel in guild.channels:
            if channel.type == discord.ChannelType.voice:
                for member in channel.members:
                    if str(member.id) in scores.keys():
                        scores[str(member.id)] += 1
                    else:
                        scores[str(member.id)] = 1
    with open("userscores.json", "w") as f:
        json.dump(scores, f)
    f.close()


@client.command()
async def points(ctx):
    f = open("userscores.json")
    scores = json.load(f)
    if str(ctx.author.id) in scores.keys():
        personal_points = scores[str(ctx.author.id)]
        await ctx.send(f"You have {personal_points} points")
    else:
        await ctx.send(f"You have not joined a voice channel yet.")


@client.command()
async def help(ctx, command=None):
    embed = discord.Embed(colour=discord.Colour.blue())
    if command == None or command == "help":
        embed.set_author(name="Kenny Bot Help")
        embed.add_field(name=".help", value="This command!", inline=False)
        embed.add_field(
            name=".quote", value="Returns a quote that Kenny would say!", inline=False
        )
        embed.add_field(
            name=".points",
            value="Returns a value representing the amount of time you have been in a voice channel in this server!",
            inline=False,
        )
    elif command == "quote":
        embed.set_author(name=".quote help ")
        embed.add_field(
            name="USAGE:",
            value="simply type .quote and a quote will be sent.",
            inline=False,
        )
        embed.add_field(
            name="List of quotes:",
            value="- " + "\n - ".join(kenny_quotes),
            inline=False,
        )
    elif command == "points":
        embed.set_author(name=".points help ")
        embed.add_field(
            name="USAGE:",
            value="simply type .points you can see how many points you have.",
            inline=False,
        )
        embed.add_field(
            name="What are points? ",
            value="points simply represent how many minutes you have been in a voice channel in this discord for.",
            inline=False,
        )
        embed.add_field(
            name="What are points used for? ",
            value="points are used for nothing... yet.",
            inline=False,
        )
    await ctx.send(embed=embed)


@client.command()
async def quote(ctx):
    print("quote created")
    await ctx.send(random.choice(kenny_quotes))


@client.command()
async def leaderboard(ctx):
    f = open("userscores.json")
    scores = json.load(f)
    print(sorted(scores.items()))
    scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    embed = discord.Embed(colour=discord.Colour.blue())
    embed.set_author(name="Leaderboard:")
    for (key, value) in scores:
        user = client.get_user(int(key))
        if user != None:
            embed.add_field(
                name=str(client.get_user(int(key)).name), value=value, inline=False
            )
    await ctx.send(embed=embed)
    f.close()


@client.command()
async def addstream(ctx, streamer_name):
    f = open("streamers.json")
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
                await ctx.send(
                    f"Streamer: {streamer_name} already in your notifications"
                )
                f.close()
                return
    if streamer_found == 0:
        streamers_data[streamer_name] = [str(ctx.author.id)]
    with open("streamers.json", "w") as f:
        json.dump(streamers_data, f)
    f.close()

    await ctx.send(f"Streamer: {streamer_name} added to your notifications")


@client.command()
async def liststream(ctx):
    f = open("streamers.json")
    streamers_data = json.load(f)
    embed = discord.Embed(colour=discord.Colour.blue())
    embed.set_author(name="List of Streamers in Your Notifications:")
    amount = 1
    for streamer in streamers_data:
        for user in streamers_data[streamer]:
            print(user == ctx.author.id, user, ctx.author.id)
            if int(user) == ctx.author.id:
                embed.add_field(name=amount, value=str(streamer), inline=False)
                amount += 1
    await ctx.send(embed=embed)
    f.close()


@client.command()
async def remstream(ctx, streamer_name):
    f = open("streamers.json")
    streamers_data = json.load(f)
    streamer_found = 0
    for streamer in streamers_data:
        if streamer == streamer_name:
            streamer_found = 1
            streamers_data[streamer].remove(str(ctx.author.id))
    if streamer_found == 0:
        streamers_data[streamer_name] = [str(ctx.author.id)]
    with open("streamers.json", "w") as f:
        json.dump(streamers_data, f)
    f.close()

    await ctx.send(f"Streamer: {streamer_name} deleted from your notifications")


async def get_streamers():
    f = open("streamers.json")
    streamers = json.load(f)
    print(streamers)
    for (streamer, users) in streamers.items():
        print(streamer, users)
        for user in users:
            if user != None:
                await check_live(streamer, user)


async def check_live(streamer, user):
    url = "https://id.twitch.tv/oauth2/token"
    myobj = {
        "client_id": "wcj55ij8oorl3islaexzvquzwhd5it",
        "client_secret": "9kugeh6m5tubziqtjfquptez5amoc9",
        "grant_type": "client_credentials",
    }

    x = requests.post(url, data=myobj)
    if x.ok:
        url = f"https://api.twitch.tv/helix/streams?user_login={streamer}"
        header = {
            "Authorization": "Bearer " + x.json()["access_token"],
            "Client-Id": "wcj55ij8oorl3islaexzvquzwhd5it",
        }
    else:
        return
    x = requests.get(url, headers=header)
    if x.ok:
        if x.json()["data"] != []:
            twitch_time = x.json()["data"][0]["started_at"]
            start_time = datetime.datetime.strptime(twitch_time, "%Y-%m-%dT%H:%M:%SZ")
            if start_time + datetime.timedelta(minutes=2) > datetime.datetime.utcnow():
                await client.get_user(int(user)).send(
                    f"Hi {client.get_user(int(user)).name}! {streamer} Just went live at https://www.twitch.tv/{streamer}"
                )


@client.command()
async def mastery(ctx, *args):
    names = args[1:]
    names = list(set([x for x in names if names.count(x) >= 1]))
    if not re.search("[0-9]+", args[0]):
        await ctx.send(
            "Incorrect command syntax: .mastery {number of champs displayed} {account names}"
        )
        return
    if len(args) < 2:
        await ctx.send(
            "Incorrect command syntax: .mastery {number of champs displayed} {account names}"
        )
        return
    if len(args) > 11:
        await ctx.send("Incorrect usage: Account limit is 10")
        return
    if int(float(args[0])) > 25:
        await ctx.send("Incorrect usage: Max list is only 25 champions")
        return

    print(names)
    # golbal variables
    api_key = "RGAPI-f9b46e05-9dba-4190-a7f7-e7aa077575cb"
    watcher = LolWatcher(api_key)
    my_region = "oc1"
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
    print(sorted(collective.items(), key=lambda item: item[1], reverse=True))
    collective = sorted(collective.items(), key=lambda item: item[1], reverse=True)
    version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    currversion = version.json()[0]
    champs = requests.get(
        f"http://ddragon.leagueoflegends.com/cdn/{currversion}/data/en_US/champion.json"
    )
    embed = discord.Embed(colour=discord.Colour.blue())
    await message1.edit(content="Assigning Mastery Ids")
    author = str(" + ".join(str(i) for i in names))
    embed.set_author(name=f"Summoner {author} Mastery:")
    max = args[0]
    if len(collective) < 25:
        max = len(collective)
    for i in range(0, int(float(max))):
        for champ in champs.json()["data"]:
            if champs.json()["data"][champ]["key"] == str(collective[i][0]):
                embed.add_field(
                    name=champs.json()["data"][champ]["name"],
                    value=str(collective[i][1]),
                    inline=False,
                )
    print(champs)
    await message1.delete()
    await ctx.send(embed=embed)


def printMastery(args):
    names = args[1:]
    names = list(set([x for x in names if names.count(x) >= 1]))
    if not re.search("[0-9]+", args[0]):
        print(
            "Incorrect command syntax: .mastery {number of champs displayed} {account names}"
        )
        return
    if len(args) < 2:
        print(
            "Incorrect command syntax: .mastery {number of champs displayed} {account names}"
        )
        return
    if len(args) > 11:
        print("Incorrect usage: Account limit is 10")
        return
    if int(float(args[0])) > 25:
        print("Incorrect usage: Max list is only 25 champions")
        return

    print(names)
    # global variables
    api_key = "RGAPI-637e1ddd-b443-435d-a16e-e83c697e59f2"
    watcher = LolWatcher(api_key)
    my_region = "oc1"
    collective = {}
    for name in names:
        try:
            sum = watcher.summoner.by_name(my_region, name)
        except ApiError as err:
            print(err)
            return
        me = watcher.champion_mastery.by_summoner(my_region, sum["id"])
        for champion in me:
            dictionary = {}
            if str(champion["championId"]) in collective:
                collective[str(champion["championId"])] += champion["championPoints"]
            else:
                collective[str(champion["championId"])] = champion["championPoints"]
    collective = sorted(collective.items(), key=lambda item: item[1], reverse=True)
    version = requests.get("https://ddragon.leagueoflegends.com/api/versions.json")
    currversion = version.json()[0]
    champs = requests.get(
        f"http://ddragon.leagueoflegends.com/cdn/{currversion}/data/en_US/champion.json"
    )
    author = str(" + ".join(str(i) for i in names))
    max = args[0]
    if len(collective) < 25:
        max = len(collective)
    for i in range(0, int(float(max))):
        for champ in champs.json()["data"]:
            if champs.json()["data"][champ]["key"] == str(collective[i][0]):
                print(champs.json()["data"][champ]["name"], str(collective[i][1]))


# client.run("Nzk4NDQ5MzUzMjI4MDI1ODY2.X_1L6A.IYUwSsiQAOQnfapLtUe6mzpF4oM")
printMastery(sys.argv[1:])
