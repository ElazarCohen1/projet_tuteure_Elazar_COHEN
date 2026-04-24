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


def split_message(text: str, max_length: int = 1990) -> list[str]:
    """Coupe le texte aux sauts de ligne pour ne pas tronquer une étape."""
    chunks = []
    current = ""
    for line in text.split("\n"):
        if len(current) + len(line) + 1 > max_length:
            chunks.append(current)
            current = line
        else:
            current += ("\n" if current else "") + line
    if current:
        chunks.append(current)
    return chunks


@bot.tree.command(name="recette", description="renvoie une recette")
async def recette(interaction: discord.Interaction, request: str):
    await interaction.response.defer(thinking=True)
    try:
        recipe = await generate_recipe(request)

        await interaction.followup.send(
            f"{interaction.user.mention} Ta recette est prête :"
        )

        for chunk in split_message(recipe):
            await interaction.followup.send(chunk)

    except Exception as e:
        await interaction.followup.send(
            f"{interaction.user.mention} Une erreur est survenue!!!"
        )
        print(f"Erreur recette: {e}")
        
bot.run(os.getenv('TOKEN'))