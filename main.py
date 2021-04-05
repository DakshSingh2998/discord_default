import discord
import os
from replit import db
from keep_alive import keep_alive
from discord.ext import commands, tasks




client=commands.Bot(command_prefix='.')
status="Playing alongside ~Daksh"

@client.event
async def on_ready():
  print("Ready Daksh. Hey ",client.user)
  await client.change_presence(activity=discord.Game(status))

client.load_extension('music')

keep_alive()
client.run(os.getenv('TOKEN'))
