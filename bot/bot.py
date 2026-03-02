import discord
import os
from dotenv import load_dotenv
from discord.ext import commands 
load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix='/',intents=intents,)

@bot.event
async def on_ready():
    try:
       await bot.tree.sync()
       print("bot sync")
    except Exception as e:
        print(e)


@bot.tree.command(name="recette", description="renvoie une recette avec les informations demandé")
async def recette(interation:discord.Interaction):
    await interation.response.send_message("alors la recette arrive")
    print("j'ai besoin de la base de donnée et du llm ")


bot.run(os.getenv('TOKEN'))