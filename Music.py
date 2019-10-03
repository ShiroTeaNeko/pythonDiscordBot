import asyncio
import discord
from discord.ext import commands

if not discord.opus.is_loaded():
    # the 'opus' library here is opus.dll on windows
    # or libopus.so on linux in the current directory
    # you should replace this with the location the
    # opus library is located in and with the proper filename.
    # note that on windows this DLL is automatically provided for you
    discord.opus.load_opus('opus')


def __init__(self, bot):
    self.bot = bot


class VoiceEntry:
    def __init__(self, message, player):
        self.requester = message.author
        self.channel = message.channel
        self.player = player

    def __str__(self):
        fmt = ' {0.title} mis en ligne par {0.uploader} et demandé par {1.display_name}'
        duration = self.player.duration
        if duration:
            fmt = fmt + ' [longueur: {0[0]}m {0[1]}s]'.format(divmod(duration, 60))
        return fmt.format(self.player, self.requester)


class VoiceState:
    def __init__(self, bot):
        self.current = None
        self.voice = None
        self.bot = bot
        self.play_next_song = asyncio.Event()
        self.songs = asyncio.Queue()
        self.skip_votes = set()  # a set of user_ids that voted
        self.audio_player = self.bot.loop.create_task(self.audio_player_task())

    def is_playing(self):
        if self.voice is None or self.current is None:
            return False

        player = self.current.player
        return not player.is_done()

    @property
    def player(self):
        return self.current.player

    def skip(self):
        self.skip_votes.clear()
        if self.is_playing():
            self.player.stop()

    def toggle_next(self):
        self.bot.loop.call_soon_threadsafe(self.play_next_song.set)

    async def audio_player_task(self):
        while True:
            self.play_next_song.clear()
            self.current = await self.songs.get()
            await self.bot.send_message(self.current.channel, '''Et c'est parti pour ''' + str(self.current))
            self.current.player.start()
            await self.play_next_song.wait()


class Music(commands.Cog):
    """Voice related commands.
    Works in multiple servers at once.
    """

    def __init__(self, bot):
        self.bot = bot
        self.voice_states = {}

    def get_voice_state(self, server):
        state = self.voice_states.get(server.id)
        if state is None:
            state = VoiceState(self.bot)
            self.voice_states[server.id] = state

        return state

    async def create_voice_client(self, channel):
        voice = await self.bot.join_voice_channel(channel)
        state = self.get_voice_state(channel.server)
        state.voice = voice

    def __unload(self):
        for state in self.voice_states.values():
            try:
                state.audio_player.cancel()
                if state.voice:
                    self.bot.loop.create_task(state.voice.disconnect())
            except:
                pass

    @commands.Cog.listener()
    async def join(self, ctx, *, channel: discord.channel):
        """Je vous rejoins faite moi de la place ☆⌒ヽ(*'､^*)chu"""
        try:
            await self.create_voice_client(channel)
        except discord.InvalidArgument:
            await self.bot.say('''ce n'est pas un channel sonore''')
        except discord.ClientException:
            await self.bot.say('Je suis deja là (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄)')
        else:
            await self.bot.say('Je suis prête à jouer du son sur le channel onii-chan')

    @commands.Cog.listener()
    async def summon(self, ctx):
        """Vous m'invoquez sur votre channel"""
        summoned_channel = ctx.message.author.voice_channel
        if summoned_channel is None:
            await self.bot.say('Are you sure your in a channel?')
            return False

        state = self.get_voice_state(ctx.message.server)
        if state.voice is None:
            state.voice = await self.bot.join_voice_channel(summoned_channel)
        else:
            await state.voice.move_to(summoned_channel)

        return True

    @commands.Cog.listener()
    async def play(self, ctx, *, song: str):
        """Joue de la musique 	♪ヽ(^^ヽ)♪.
        If there is a song currently in the queue, then it is
        queued until the next song is done playing.
        This command automatically searches as well from YouTube.
        The list of supported sites can be found here:
        https://rg3.github.io/youtube-dl/supportedsites.html
        """
        state = self.get_voice_state(ctx.message.server)
        opts = {
            'default_search': 'auto',
            'quiet': True,
        }

        if state.voice is None:
            success = await ctx.invoke(self.summon)
            await self.bot.say("Je charge votre son, soyez patient (─‿‿─)♡")
            if not success:
                return

        try:
            player = await state.voice.create_ytdl_player(song, ytdl_options=opts, after=state.toggle_next)
        except Exception as e:
            fmt = 'mince, une erreur: ```py\n{}: {}\n```'
            await self.bot.send_message(ctx.message.channel, fmt.format(type(e).__name__, e))
        else:
            player.volume = 0.6
            entry = VoiceEntry(ctx.message, player)
            await self.bot.say('Enqueued ' + str(entry))
            await state.songs.put(entry)

    @commands.Cog.listener()
    async def volume(self, ctx, value: int):
        """Je change le volume de la musique joué 	╮(￣ω￣;)╭"""

        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.volume = value / 100
            await self.bot.say('Set the volume to {:.0%}'.format(player.volume))

    @commands.Cog.listener()
    async def resume(self, ctx):
        """Je vous remet la musique que vous aviez stop (≧◡≦) ♡"""
        state = self.get_voice_state(ctx.message.server)
        if state.is_playing():
            player = state.player
            player.resume()

    @commands.Cog.listener()
    async def stop(self, ctx):
        """j'arrete de jouer du son et je vous laisse tranquille (⁄ ⁄>⁄ ▽ ⁄<⁄ ⁄).
        This also clears the queue.
        """
        server = ctx.message.server
        state = self.get_voice_state(server)

        if state.is_playing():
            player = state.player
            player.stop()

        try:
            state.audio_player.cancel()
            del self.voice_states[server.id]
            await state.voice.disconnect()
            await self.bot.say("La musique actuellement jouée est désormais en pause ")
        except:
            pass

    # @commands.command(pass_context=True, no_pm=True)
    # async def pause(self, ctx):
    # state = self.get_voice_state(ctx.message.server)
    # if state.is_playing():
    # player = state.player
    # player.

    @commands.Cog.listener()
    async def skip(self, ctx):
        """+1 vote pour passer la musique. Le requester peut passer directement
        3 skip votes are needed for the song to be skipped.
        """

        state = self.get_voice_state(ctx.message.server)
        if not state.is_playing():
            await self.bot.say('Je ne joue actuellement rien (╥﹏╥)')
            return

        voter = ctx.message.author
        if voter == state.current.requester:
            await self.bot.say('Merci aux Skiper ヾ(`ヘ´)ﾉﾞ')
            state.skip()
        elif voter.id not in state.skip_votes:
            state.skip_votes.add(voter.id)
            total_votes = len(state.skip_votes)
            if total_votes >= 2:
                await self.bot.say('Les votes passe la musique ...')
                state.skip()
            else:
                await self.bot.say('+1 vote pour passer [{}/2]'.format(total_votes))
        else:
            await self.bot.say('Vous avez deja voté pour passer le son.')

    @commands.Cog.listener()
    async def playing(self, ctx):
        """Montre quel son est actuellement joué (〜￣△￣)〜."""

        state = self.get_voice_state(ctx.message.server)
        if state.current is None:
            await self.bot.say('Je ne joue actuellement rien (╥﹏╥)')
        else:
            skip_count = len(state.skip_votes)
            await self.bot.say('Joue désormais {} [skips: {}/2]'.format(state.current, skip_count))


def setup(bot):
    bot.add_cog(Music(bot))
    print('Musique chargée (*^^*)♡')
