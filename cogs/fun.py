import string
import praw
import discord
import aiohttp
from discord.ext import commands
import requests
import random


class Fun(commands.Cog):
    def __init__(self, bot):
        self._bot = bot

    @commands.Cog.listener()
    async def on_ready(self):
        print('Fun commands are ready')

    @commands.command(help="DOGO!!! \U0001f436")
    async def dog(self, ctx, breed=None, sub_breed=None):
        if breed is None:
            async with aiohttp.ClientSession() as cs:
                async with cs.get('https://dog.ceo/api/breeds/image/random') as r:
                    dogo_dict = await r.json()
        else:
            breed = breed.lower()
            if sub_breed is not None:
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f'https://dog.ceo/api/breed/{breed}/{sub_breed}/images/random') as r:
                        result = await r.json()
            else:
                async with aiohttp.ClientSession() as cs:
                    async with cs.get(f'https://dog.ceo/api/breed/{breed}/images/random') as r:
                        result = await r.json()
            dogo_dict = result.json()
            if dogo_dict['status'] == 'error':
                await ctx.send('Sorry, the breed you specified is invalid! Please try again.')
                return

        dogo_link = dogo_dict['message']

        dogo_embed = discord.Embed(title='\U0001f436 Woof!', description='', url=dogo_link)
        dogo_embed.set_image(url=dogo_link)
        dogo_embed.set_footer(text="Images courtesy of the Dog API [dog.ceo]")
        await ctx.send(embed=dogo_embed)

    @commands.command(help="Slaps a specified member. >:)")
    async def slap(self, ctx, member: commands.MemberConverter, *, reason=":("):
        to_slap = member
        await ctx.send(f'{ctx.author} slapped {to_slap.name}#{to_slap.discriminator} because **{reason}**')

    @commands.command(help="A d d s  s p a c e s  t o  y o  m e s s a g e s")
    async def spaces(self, ctx, *, message):
        await ctx.send(" ".join(message))

    @commands.command(aliases=['sc'], help="ᴄᴏɴᴠᴇʀᴛ ʏᴏᴜʀ ᴛᴇxᴛ ᴛᴏ ꜱᴍᴀʟʟ ᴄᴀᴘꜱ!")
    @commands.guild_only()
    async def smallcaps(self, ctx, *, message):
        alpha = list(string.ascii_lowercase)
        converter = ['ᴀ', 'ʙ', 'ᴄ', 'ᴅ', 'ᴇ', 'ꜰ', 'ɢ', 'ʜ', 'ɪ', 'ᴊ', 'ᴋ', 'ʟ', 'ᴍ', 'ɴ', 'ᴏ', 'ᴘ', 'ǫ', 'ʀ', 'ꜱ', 'ᴛ',
                     'ᴜ', 'ᴠ', 'ᴡ', 'x', 'ʏ', 'ᴢ']
        new = ""
        exact = message.lower()
        for letter in exact:
            if letter in alpha:
                index = alpha.index(letter)
                new += converter[index]
            else:
                new += letter
        await ctx.send(new)

    @commands.command(name='8ball', aliases=["8"], help="...its an 8ball. Do you need more explanation?")
    async def _8ball(self, ctx, *, question):
        responses = ['It is Certain.',
                     'It is decidedly so.',
                     'Without a doubt.',
                     'Yes definitely.',
                     'You may rely on it.',
                     'As I see it, yes.',
                     'Most likely.',
                     'Outlook good.',
                     'Yes.',
                     'Signs point to yes.',
                     'Reply hazy, try again.',
                     'Ask again later.',
                     'Better not tell you now.',
                     'Cannot predict now.',
                     'Concentrate and ask again.',
                     "Don't count on it.",
                     'My reply is no.',
                     'My sources say no.',
                     'Outlook not so good.',
                     'Very doubtful.']
        await ctx.send(f"Question: {question}\nAnswer: {random.choice(responses)}")

    @commands.command(help="Pong! Gets the latency of the bot.")
    async def ping(self, ctx):
        await ctx.send(f"Pong! **{round(self._bot.latency * 1000)}** ms")

    @commands.command(help="Its rock paper scissors :D (one player for now)")
    async def rps(self, ctx, *, args):
        msg = args.lower()
        responses = ['**rock**',
                     '**paper**',
                     '**scissors**']

        random_res = random.choice(responses)
        results = {'rock': {'**paper**': f'I win! I chose {random_res}.',
                            '**scissors**': f'You win! I chose {random_res}.'},
                   'paper': {'**rock**': f'You win! I chose {random_res}.',
                             '**scissors**': f'I win! I chose {random_res}.'},
                   'scissors': {'**rock**': f'I win! I chose {random_res}.',
                                '**paper**': f'You win! I chose {random_res}.'}}

        if msg not in ('rock', 'paper', 'scissors'):
            await ctx.send("Invalid Argument!")
            return
        elif random_res == f'**{msg}**':
            await ctx.send(f"It's a Draw! I chose {random_res}.")
            return
        else:
            await ctx.send(results[msg][random_res])
            return

    async def get_reddit_submission(self, ctx):
        reddit = praw.Reddit(client_id='r9iCbMevLSuhCAbBlqoakA',
                             client_secret='pmvkADXxBayrJY5kf5JlH4xJeWjErw',
                             user_agent='my user agent')
        sub = 'dankmemes'
        while True:
            submissions = reddit.subreddit(sub).random()
            if submissions is not None and not submissions.url.startswith("https://gfycat.com") \
                    and int(submissions.score) > 999:
                submission_embed = discord.Embed(title=submissions.title,
                                                 description='',
                                                 url=f"https://reddit.com{submissions.permalink}",
                                                 color=discord.Color.green())
                submission_embed.set_image(url=submissions.url)
                submission_embed.set_footer(text=f'\U0001f44d {submissions.score} | '
                                                 f'\U0001f4ac {submissions.num_comments}')
                await ctx.send(embed=submission_embed)
                break

    @commands.command(help='Takes a random meme from r/dankmemes.')
    async def meme(self, ctx):
        await self._bot.loop.create_task(self.get_reddit_submission(ctx=ctx))


def setup(bot):
    bot.add_cog(Fun(bot))
