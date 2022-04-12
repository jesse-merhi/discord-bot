import discord
from discord.ext import commands

client = commands.Bot(command_prefix = ".")


@client.event
async def on_ready():
    print('Bot is ready.')

@client.event
async def on_member_join(member):
    role = discord.utils.get(member.guild.roles, name="Minions")
    await member.add_roles(role)

@client.event
async def on_member_leave(member):
    print(f'{member} has left the server')

@client.event
async def on_message(message):
    if client.user.mentioned_in(message):
        await message.channel.send(f"Talk to Jesse to ask questions.")
    elif message.type == discord.MessageType.new_member:
        print(message)
        role = discord.utils.get(message.author.guild.roles, name="Minions")
        await message.author.add_roles(role)
    await client.process_commands(message)
@client.command()
async def prune(ctx, amount):
    print("Pruned")
    
    if int(amount) >= 20:
        await ctx.send(f"Wow dude you are so cool and funny, cant believe how epic you are.")
        return
    await ctx.channel.purge(limit = int(amount) + 1)
    if amount == 0:
        await ctx.send(f"No messages removed.")
    elif amount == 1:
        await ctx.send(f"{amount} message removed.")
    else:
        await ctx.send(f"{amount} messages removed.")
        time.sleep(2)
        await ctx.channel.purge(limit = 1)



client.run('Nzk2ODk5NzMzMjg0OTc4Njg5.X_eotg.wOlbdvaC_GWxD7NeQuuNWDtJeUA')   