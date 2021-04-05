
import discord
from discord.ext import commands
import os
import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL
from discord.ext import commands, tasks
################################
import discord
import os
import requests
import json
from replit import db
from keep_alive import keep_alive
from discord.ext import commands, tasks
#from discord.utils import get
#from discord import FFmpegPCMAudio
import youtube_dl
#from youtube_dl import YoutubeDL
#from discord.utils import get
#from os import system
import discord.client
#import urllib.parse,urllib.request,re
#from bs4 import BeautifulSoup
#from threading import Thread



client=commands.Bot(command_prefix='.')
status="~Daksh"

@client.event
async def on_ready():
  print("Ready Daksh. Hey ",client.user)
  await client.change_presence(activity=discord.Game(status))

def clss():
    os.system('cls' if os.name=='nt' else 'clear')
client=commands.Bot(command_prefix=';')
@client.event
async def on_ready():
  print("Ready Daksh. Hey ",client.user)

@tasks.loop(seconds=1)
async def loopp(ctxs,players):
  for ctx in ctxs.values():
    connected_id=ctx.guild.voice_client.channel.id
    channel=discord.utils.get(ctx.guild.channels, id=connected_id)
    #channel=client.get_channel(connected_id)
    if not channel is None:
      members=channel.voice_states.keys()
      #print(len(members))
      if(len(members)<=1):
        vc=ctx.voice_client
        if not vc or not vc.is_playing():
          return
        elif vc.is_paused():
          return
        if(players[ctx.guild.id].auto_pause==0):
          vc.pause()
          print("pause")
      else:
        vc=ctx.voice_client
        if not vc or not vc.is_connected():
            return
        elif not vc.is_paused():
            return
        if(players[ctx.guild.id].auto_pause==0):
          vc.resume()
          print("resunme")


ytdlopts={
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts={
    'before_options': '-nostdin',
    'options': '-vn'
}

ytdl=YoutubeDL(ytdlopts)
class VoiceConnectionError(commands.CommandError):
    """Class for connection error"""
class InvalidVoiceChannel(VoiceConnectionError):
    """CLass for invalid channel"""

class YTDLSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester=requester
        self.title=data.get('title')
        self.web_url=data.get('webpage_url')
    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop=loop or asyncio.get_event_loop()
        to_run=partial(ytdl.extract_info, url=search, download=download)
        data=await loop.run_in_executor(None, to_run)
        if 'entries' in data:
            data=data['entries'][0]
        await ctx.send(f'[Added {data["title"]}]', delete_after=20)
        if download:
            source=ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}
        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)
    @classmethod
    async def regather_stream(cls, data, *, loop):
        loop=loop or asyncio.get_event_loop()
        requester=data['requester']
        to_run=partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data=await loop.run_in_executor(None, to_run)
        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:
    __slots__=('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume','auto_pause')
    def __init__(self, ctx):
        self.bot=ctx.bot
        self._guild=ctx.guild
        self._channel=ctx.channel
        self._cog=ctx.cog
        self.queue=asyncio.Queue()
        self.next=asyncio.Event()
        self.auto_pause=0
        self.np=None  # Now playing message
        self.volume=1
        self.current=None
        ctx.bot.loop.create_task(self.player_loop(ctx))
    
    async def remove(self,ctx,search):
      index=int(search)
      temp_queue=asyncio.Queue()
      i=1
      while not self.queue.empty():
        tempp=await self.queue.get()
        if(i==index):
          i=i+1
        else:
          await temp_queue.put(tempp)
        i=i+1
      self.queue=temp_queue

    async def show_playlist(self,ctx,source):
      temp_queue=asyncio.Queue()
      i=1
      await self._channel.send("Next Songs")
      while not self.queue.empty():
        tempp=await self.queue.get()
        await self._channel.send(f'{i}. {tempp["title"]}')
        await temp_queue.put(tempp)
        i=i+1
      self.queue=temp_queue

      await ctx.channel.send(self.np) 

    async def show_playlist_alt(self,ctx):
      temp_queue=asyncio.Queue()
      i=1
      source=await self.queue.get()
      await temp_queue.put(source)
      await self._channel.send("Next Songs")
      while not self.queue.empty():
        
        tempp=await self.queue.get()
        await self._channel.send(f'{i}. {tempp["title"]}')
        await temp_queue.put(tempp)
        i=i+1
      self.queue=temp_queue
      self.np=await ctx.channel.send(f'**Now Playing:** {source["title"]} requested by **`{source["requester"]}`**\n{source["webpage_url"]}')


        
    async def player_loop(self,ctx):
      await self.bot.wait_until_ready()
      while not self.bot.is_closed():
        self.next.clear()
        clss()
        try:
            async with timeout(999999999):  
                source=await self.queue.get()
                self.np=str(f'**Now Playing:** {source["title"]} requested by **`{source["requester"]}`**\n{source["webpage_url"]}')
        except Exception as ee:
            yy=4
        if not isinstance(source, YTDLSource):
            try:
                source=await YTDLSource.regather_stream(source, loop=self.bot.loop)
                #clss()
            except Exception as e:
                await self._channel.send(f'There was an error processing your song.')
                
                continue
        try:
          source.volume=self.volume
          self.current=source
          self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))
          

          await self.next.wait()
          source.cleanup()
          self.current=None
        except Exception as ee:
          print(ee)
    def destroy(self, guild):
        return self.bot.loop.create_task(self._cog.cleanup(guild)) #difficulttt

class Music(commands.Cog):
    __slots__=('bot', 'players','ctxs')
    def __init__(self, bot):
        self.bot=bot
        self.players={}  ### global only one
        self.ctxs={}
    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
        except Exception as ee:
            pass
        try:
            del self.players[guild.id]
            del self.ctxs[guild.id]
        except Exception as ee:
            pass
    async def __local_check(self, ctx):   ####   not used
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True
    async def __error(self, ctx, error):  #### not used
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except Exception as ee:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')
        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)
    def get_player(self, ctx):
      try:
          player=self.players[ctx.guild.id]
          ctx_t=self.ctxs[ctx.guild.id]
      except KeyError:
          player=MusicPlayer(ctx)
          self.ctxs[ctx.guild.id]=ctx
          self.players[ctx.guild.id]=player
          try:
            loopp.start(self.ctxs,self.players)
          except:
            yy=5
      return player
    @commands.command(name='connect', aliases=['join'])  ### aliiase ka ni pata
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        if not channel:
            try:
                channel=ctx.author.voice.channel
            except Exception as ee:
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')
        vc=ctx.voice_client
        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')
        await ctx.send(f'Connected to: **{channel}**', delete_after=20)
    @commands.command(name='play', aliases=['sing','p'])
    async def play_(self, ctx, *, search: str):
      self.ctxs[ctx.guild.id]=ctx
      await ctx.trigger_typing()
      vc=ctx.voice_client
      if not vc:
          await ctx.invoke(self.connect_)
      player=self.get_player(ctx)
      source=await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)
      
      await player.queue.put(source)
      self.players[ctx.guild.id]=player
      await self.players[ctx.guild.id].show_playlist(ctx,source)
    @commands.command(name='pause')
    async def pause_(self, ctx):
        vc=ctx.voice_client
        if not vc or not vc.is_playing():
            return await ctx.send('I am not currently playing anything!', delete_after=20)
        elif vc.is_paused():
            return
        self.players[ctx.guild.id].auto_pause=1
        vc.pause()
        await ctx.send(f'**`{ctx.author}`**: Paused the song!')
    @commands.command(name='resume')
    async def resume_(self, ctx):
        vc=ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)
        elif not vc.is_paused():
            return
        self.players[ctx.guild.id].auto_pause=0
        vc.resume()
        await ctx.send(f'**`{ctx.author}`**: Resumed the song!')
    @commands.command(name='skip')
    async def skip_(self, ctx):
        if self.players[ctx.guild.id].queue.empty():
          return
        self.ctxs[ctx.guild.id]=ctx
        vc=ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)
        if vc.is_paused():
            pass
        elif not vc.is_playing():
            return
        await self.players[ctx.guild.id].show_playlist_alt(ctx)
        vc.stop()


        #await self.now_playing(ctx)
        #await ctx.send(f'**`{ctx.author}`**: Skipped the song!')

    @commands.command(name='now_playing', aliases=['np', 'current', 'currentsong', 'playing'])
    async def now_playing(self, ctx):
      yy=5
      """"
        vc=ctx.voice_client
        await self.players[ctx.guild.id].show_playlist(ctx)
        if not vc or not vc.is_connected():
            return #await ctx.send('I am not currently connected to voice!', delete_after=20)
        try:
          await self.players[ctx.guild.id].np.delete()
        except:
          yy=5
        player=self.get_player(ctx)
        await ctx.send(f'{player.np}')
      """
    async def change_volume(self, ctx, *, vol: float):
        vc=ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=20)
        if not 0 < vol < 101:
            return await ctx.send('Please enter a value between 1 and 100.',delete_after=20)
        player=self.get_player(ctx)
        if vc.source:
            vc.source.volume=vol / 100
        player.volume=vol / 100
        await ctx.send(f'**`{ctx.author}`**: Set the volume to **{vol}%**')
    @commands.command(name='stop')
    async def stop_(self, ctx):
        vc=ctx.voice_client
        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently playing anything!', delete_after=20)
        await self.cleanup(ctx.guild)
    @commands.command(name='remove',aliases=['rem'])
    async def remove(self, ctx, *, search: str):
      await self.players[ctx.guild.id].remove(ctx,search)
      await self.now_playing(ctx)



def setup(bot):
    bot.add_cog(Music(bot))