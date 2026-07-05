import discord
from discord.ext import commands
from discord import app_commands
import json
import random
import string
import os

TOKEN = "TON_TOKEN_ICI"

intents = discord.Intents.default()
bot = commands.Bot(command_prefix="!", intents=intents)

DB = "keys.json"

# Création automatique de la base de données
if not os.path.exists(DB):
    with open(DB, "w") as f:
        json.dump({}, f)

def load_keys():
    with open(DB, "r") as f:
        return json.load(f)

def save_keys(data):
    with open(DB, "w") as f:
        json.dump(data, f, indent=4)

def generate_key():
    return "-".join(
        "".join(random.choices(string.ascii_uppercase + string.digits, k=5))
        for _ in range(3)
    )

@bot.event
async def on_ready():
    try:
        synced = await bot.tree.sync()
        print(f"{len(synced)} commandes synchronisées.")
    except Exception as e:
        print(e)

    print(f"Connecté en tant que {bot.user}")

# Générer une clé
@bot.tree.command(name="gen", description="Générer une clé")
@app_commands.describe(jours="Nombre de jours de validité")
async def gen(interaction: discord.Interaction, jours: int):
    data = load_keys()

    key = generate_key()

    data[key] = {
        "jours": jours,
        "utilisee": False,
        "bannie": False
    }

    save_keys(data)

    await interaction.response.send_message(
        f"✅ Clé générée !\n\n🔑 `{key}`\n📅 Durée : **{jours} jours**"
    )

# Supprimer une clé
@bot.tree.command(name="delete", description="Supprimer une clé")
@app_commands.describe(cle="La clé à supprimer")
async def delete(interaction: discord.Interaction, cle: str):
    data = load_keys()

    if cle in data:
        del data[cle]
        save_keys(data)
        await interaction.response.send_message("🗑️ Clé supprimée.")
    else:
        await interaction.response.send_message("❌ Clé introuvable.")

# Bannir une clé
@bot.tree.command(name="ban", description="Bannir une clé")
@app_commands.describe(cle="La clé à bannir")
async def ban(interaction: discord.Interaction, cle: str):
    data = load_keys()

    if cle in data:
        data[cle]["bannie"] = True
        save_keys(data)
        await interaction.response.send_message(f"🚫 Clé `{cle}` bannie.")
    else:
        await interaction.response.send_message("❌ Clé introuvable.")

# Réinitialiser toutes les clés
@bot.tree.command(name="reset", description="Supprimer toutes les clés")
async def reset(interaction: discord.Interaction):
    save_keys({})
    await interaction.response.send_message("✅ Toutes les clés ont été supprimées.")

# Voir toutes les clés
@bot.tree.command(name="list", description="Afficher toutes les clés")
async def list_keys(interaction: discord.Interaction):
    data = load_keys()

    if not data:
        await interaction.response.send_message("📂 Aucune clé enregistrée.")
        return

    texte = ""

    for key, info in data.items():
        statut = "🚫 Bannie" if info["bannie"] else "✅ Active"
        texte += f"🔑 `{key}` | {info['jours']} jours | {statut}\n"

    await interaction.response.send_message(texte)

bot.run(TOKEN)