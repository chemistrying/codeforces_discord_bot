from discord.ext import commands
import discord
import logging
import codeforces
import time
import asyncio


logger = logging.getLogger("discord")
logger.setLevel(logging.DEBUG)
handler = logging.FileHandler(filename="discord.log", encoding="utf-8", mode="w")
handler.setFormatter(logging.Formatter("%(asctime)s:%(levelname)s:%(name)s: %(message)s"))
logger.addHandler(handler)

# client = discord.Client()

help_command = commands.DefaultHelpCommand(
    no_category = 'Commands'
)
description = "Hello you can check codeforces stuff using this bot. My prefix is semicolon(;)."
bot = commands.Bot(
    command_prefix = commands.when_mentioned_or(';'),
    description = description,
    help_command = help_command
)

@bot.command()
async def ping(ctx):
    embedVar = discord.Embed(title="PING", description="PONG", color=0xffffff)
    embedVar.add_field(name="pong", value="ping", inline=False)
    embedVar.add_field(name="ping", value="pong", inline=False)
    # componentVar = discord.compo
    await ctx.send("pong", embed=embedVar)
    pass 

@bot.command()
@commands.has_role("Admin")
async def update(ctx):
    await ctx.send("Start updating...")
    codeforces.update()
    await ctx.send("Update finished!")
    pass

@bot.command()
async def courage(ctx):
    await ctx.send("Alright lemme give you some courage <3")
    pass

@bot.command()
@commands.has_role("Trainer")
async def contribution(ctx):
    with open("contribution.png", "rb") as f:
        picture = discord.File(f)
        await ctx.send("Best way to get contribution: ", file=picture)
    pass

@bot.command()
async def check(ctx, *args):
    if len(args) == 0:
        await ctx.send("Handle is required in order to check any users' information.")
    else:
        errorcode = codeforces.check(args[0], args[1::] if len(args) > 1 else [])
        if errorcode[0] == 1:
            await ctx.send("User information was not found. Please check if you have typed the handle correctly or create a new one.")
        else:
            # print(errorcode[1])
            await ctx.send('\n'.join(errorcode[1]))
    pass

@bot.command()
async def info(ctx, args):
    errorcode = codeforces.info(args)
    if errorcode[0] == 1:
        await ctx.send("Problem ID was not valid. Please check if you have typed correctly, or update the problemset by running `;update`.")
    else:
        await ctx.send('\n'.join(errorcode[1]) + "\nhttps://codeforces.com/problemset/problem/" + args[:len(args) - 1] + '/' + args[len(args) - 1])
    pass

@bot.command()
async def contests(ctx):
    errorcode = codeforces.contests()
    if errorcode[1] == []:
        await ctx.send("No contests available.")
    else:
        await ctx.send('\n\n'.join(sorted(errorcode[1])))
    pass

@bot.command()
async def isSolved(ctx, *args):
    if len(args) == 2:
        errorcode = codeforces.isSolved(args)
        if errorcode[0] == 1:
            await ctx.send("User has not found. Please check if you have typed the username correctly.")
        else:
            if errorcode[1]:
                await ctx.send(args[0] + " has solved " + args[1] + '.')
            else:
                await ctx.send(args[0] + " has not solved " + args[1] + '.')
    else:
        await ctx.send("You must provide the handle name and problem name in order to use this command.")
    pass


async def background_task_reminder_execute(id, minutes):
    await bot.wait_until_ready()
    channel = bot.get_channel(618777394534285314)
    await channel.send("Codeforces Contest " + id + " is going to start in " + minutes + " minutes!\nhttps://codeforces.com/contests/" + id)
    await bot.wait_until_ready()
    channel = bot.get_channel(947821744092217374)
    await channel.send("Codeforces Contest " + id + " is going to start in " + minutes + " minutes!\nhttps://codeforces.com/contests/" + id)
    pass


async def background_task():
    while True:
        upcomingContests = codeforces.background_task_contests()
        await asyncio.sleep((upcomingContests[0][0] - 1800) - time.time())
        await background_task_reminder_execute(upcomingContests[0][1], "30")
        await asyncio.sleep((upcomingContests[0][0] - 600) - time.time())
        await background_task_reminder_execute(upcomingContests[0][1], "10")
        await asyncio.sleep((upcomingContests[0][0]) - time.time())

# async def background_task_2():
#     while True:
#         # print("Hello World!")
#         await bot.wait_until_ready()
#         channel = bot.get_channel(618777394534285314)
#         await channel.send("Hello World")

if __name__ == "__main__":
    with open("token.txt") as f:
        token = f.read()
    print("Start running...")
    bot.loop.create_task(background_task())
    # bot.loop.create_task(background_task_2())
    bot.run(token)
