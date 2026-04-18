import discord
import os
from dotenv import load_dotenv
from discord.ext import commands 
from bdd.main import generate_recipe
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


@bot.tree.command(name="recette", description="renvoie une recette")
async def recette(interaction: discord.Interaction, request: str):
    await interaction.response.defer(thinking=True)

    try:
        recipe = await generate_recipe(request)
        await interaction.followup.send(recipe)

    except Exception as e:
        await interaction.followup.send(
            "Une erreur est survenue lors de la génération de la recette."
        )
        print(f"Erreur recette: {e}")


bot.run(os.getenv('TOKEN'))