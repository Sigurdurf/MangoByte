import discord
from discord.ext import commands
from .utils.settings import *
import asyncio
import string
from gtts import gTTS
from ctypes.util import find_library

discord.opus.load_opus(find_library('opus'))

async def playaudio(bot, ctx, mp3name, volume=0.6):
	bot.get_cog("Audio").try_talking(mp3name, volume)

# tts an audio clip from a word
def make_temp_mp3(word):
	tts = gTTS(text=word, lang='en')
	tts.save(settings.resourcedir + "temp/temp.mp3")

# gets a list of all the mp3s in the root resource directory
def get_playlist():
	clips = []
	for file in os.listdir(settings.resourcedir):
		if file.endswith(".mp3"):
			clips.append(os.path.splitext(file)[0])
	return clips

class Audio:
	"""Commands used to play audio
	"""

	def __init__(self, bot):
		self.bot = bot
		self.voice = None
		self.player = None
		self.voice_channel = None


	# whether or not the bot is currently talking
	def is_talking(self):
		return (self.player is not None) and (not self.player.is_done())

	# try to say an mp3, and if we arent in a voice channel, join the default one
	async def try_talking(self, mp3name, volume=0.6):
		if(self.voice is None):
			print("tried to talk while not in voice channel")
			await self.bot.say("not in voice channel m8")
			return

		if self.is_talking():
			# we have a player and its playing something
			print("interruption")
			try:
				await self.bot.say("I'm already talking, don't interrupt. rude.")
			except Exception as e:
				print("couldnt report interruption")
			finally:
				return

		try:
			self.player = self.voice.create_ffmpeg_player(mp3name)
			self.player.volume = volume
			self.player.start()
			print("playing: " + mp3name)
		except Exception as e:
			print(str(e))
			await self.bot.say("thats not valid input, silly.")

	@commands.command(pass_context=True)
	async def play(self, ctx, clip : str):
		"""Plays an audio clip

		example:
		?play hello

		for a complete list of the available clips, try ?playlist"""
		if clip in get_playlist():
			await self.try_talking(settings.resourcedir +  clip + '.mp3')
		else:
			await self.bot.say("'" + clip + "' is not a valid clip. try ?playlist.")

	@commands.command(pass_context=True)
	async def playlist(self, ctx):
		"""Lists the audio clips available for the play command"""
		clips = get_playlist()
		message = "```"
		for clip in clips:
			message += clip + "\n"
		message += "```"
		await self.bot.say(message)

	@commands.command(pass_context=True)
	async def playurl(self, ctx, mp3url : str):
		"""Plays an mp3 file at a url

		Make sure to use http, not https.
		One way to use this is to go to:
		http://dotabase.me/responses/
		Once there, find a good audio clip, right click on it, select copy url address, and do the thing."""
		await self.try_talking(mp3url)

	#function called when this event occurs
	async def on_voice_state_update(self, before, after):
		if self.voice_channel is None or after.voice_channel is None or before.voice_channel == after.voice_channel:
			# if the bot or the member are not in a voice channel, don't worry about checking that theyre equal
			return
		if after.voice_channel.id == self.voice_channel.id and before.voice_channel != after.voice_channel:
			print(after.name + " joined the channel")

			await asyncio.sleep(3)
			await self.try_talking(settings.resourcedir + 'helloits.mp3')
			tts = gTTS(text=after.name, lang='en-au')
			tts.save(settings.resourcedir + "temp/temp.mp3")
			while self.is_talking():
				await asyncio.sleep(0.1)

			await self.try_talking(settings.resourcedir + "temp/temp.mp3")


def setup(bot):
	n = Audio(bot)
	bot.add_listener(n.on_voice_state_update, "on_voice_state_update")
	bot.add_cog(n)
