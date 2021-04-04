__version__ = "0.1.0"

import json
import os
import random
from difflib import get_close_matches
from urllib.parse import quote_plus

import discord
from discord.ext import tasks
import requests
import requests_cache
from dotenv import load_dotenv

with open('subreddits.json') as file:
    subreddits = json.load(file)
load_dotenv()
requests_cache.install_cache('cache', expire_after=2400)
pexels = os.environ.get("PEXELS_API")
pixabay = os.environ.get("PIXABAY_API")
unsplash = os.environ.get("UNSPLASH_API")


class CuteBot(discord.Client):
    def __init__(self, **options):
        super().__init__(**options)
        self.activity = discord.Game(f"cute help | some servers | v{__version__}")

    async def on_ready(self):
        print("-" * 24)
        print("Logged in as:")
        print(bot.user.name + "#" + bot.user.discriminator)
        print("Id: " + str(bot.user.id))
        print(f"Discord version: {discord.__version__}")
        print("-" * 24)
        print("I am logged in and ready!")

    async def on_message(self, message):
        await self.wait_until_ready()
        send = message.channel.send
        if not message.author.bot and message.content.lower().startswith("cute "):
            content = message.content.lower().replace("cute ", "", 1).strip()
            if content == "help":
                pass
            elif content == "ping":
                await send("Pong!")
            elif content == "cnf":
                pass
            elif content == "github":
                pass
            else:
                animal = get_close_matches(content, subreddits, 1)
                if animal:
                    animal = animal[0]
                    if animal == "random":
                        animal = random.choice(list(subreddits)[1:])
                    embed = discord.Embed(
                        title="here is a" + (
                            "n " if animal.startswith(("a", "e", "i", "o", "u")) else " ") + animal)
                    do_reddit = True
                    url = ""
                    rand = random.random()
                    if rand < 0.3 and pexels:
                        do_reddit = False
                        try:
                            search = random.choice(requests.get(
                                f"https://api.pexels.com/v1/search?query={animal}&per_page=80",
                                headers={"Authorization": pexels}).json()["photos"])
                            url = search["src"]["original"]
                            embed.description = f"*Photo by [{search['photographer']}]({search['photographer_url']}) on [" \
                                                f"Pexels]({search['url']})*"
                        except:
                            do_reddit = True
                    elif rand < 0.6 and pixabay:
                        do_reddit = False
                        try:
                            search = random.choice(requests.get(
                                f"https://pixabay.com/api/?key={pixabay}&q={quote_plus(animal)}&image_type=photo"
                                f"&safesearch=true&per_page=100").json()["hits"])
                            url = search["largeImageURL"]
                            embed.description = f"*Photo by [{search['user']}](https://pixabay.com/users/{search['user']}-{search['user_id']}) on [Pixabay]({search['pageURL']})*"
                        except:
                            do_reddit = True
                    elif rand < 0.9 and unsplash:
                        do_reddit = False
                        try:
                            search = random.choice(requests.get(
                                f"https://api.unsplash.com/search/photos?query={animal}&per_page=80",
                                headers={"Authorization": f"Client-ID {unsplash}"}).json()["results"])
                            url = search["urls"]["raw"]
                            embed.description = f"*Photo by [{search['user']['name']}]({search['user']['links']['html']}) on [Unsplash]({search['links']['html']})* "
                        except:
                            do_reddit = True
                    if do_reddit:
                        subreddit = random.choice(subreddits[animal])
                        subreddit = requests.get(
                            f"https://api.reddit.com/r/{subreddit}/top.json?sort=top&t=year&limit=40",
                            headers={"User-agent": f"A discord bot: {self.user.name}#{self.user.discriminator}"}).json()
                        random.shuffle(subreddit["data"]["children"])
                        while not url.endswith((".gif", ".png", ".jpg")):
                            image = subreddit["data"]["children"].pop()["data"]
                            url = image["url"]
                            if url.startswith("https://gfycat.com"):
                                url = image["media"]["oembed"]["thumbnail_url"]
                            if not subreddit["data"]["children"]:
                                return await send("No results.")
                        embed.description = f"*Photo by [u/{image['author']}](https://reddit.com/u/{image['author']}) " \
                                            f"on [Reddit](https://reddit.com{image['permalink']})* "
                    embed.set_image(url=url)
                    embed.set_footer(icon_url=message.author.avatar_url,
                                     text=f"Requested by: {message.author.name}#{message.author.discriminator}")
                    await send(embed=embed)
                elif 1 < len(content) < 10:
                    embed = discord.Embed(
                        description=f"Command or animal `{content}` not found.",
                        color=discord.Color.red())
                    embed.set_footer(
                        text="For more info, use \"cute help\".\nTo disable these messages, see \"cute cnf\".")
                    await send(embed=embed)


@tasks.loop(minutes=2.0)
async def status_loop(bot):
    await bot.wait_for("ready")
    await change_status(bot)


async def change_status(bot):
    servers = "{:,}".format(len(bot.guilds))
    text = f"cute help | {servers} servers | v{__version__}"
    await bot.change_presence(activity=discord.Game(text))


bot = CuteBot()
status_loop.start(bot)

token = os.environ.get("TOKEN", None)
if token is None or len(token.strip()) == 0:
    print("A bot token is necessary for the bot to function.")
    raise RuntimeError
else:
    bot.run(token)
