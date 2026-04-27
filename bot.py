import re
import discord
from predict import predict_url

TOKEN = "Your Bot Token Here"

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)


def extract_urls(text):
    pattern = r"https?://[^\s]+"
    return re.findall(pattern, text)


@client.event
async def on_ready():
    print(f"Bot berhasil login sebagai {client.user}")


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    urls = extract_urls(message.content)

    if not urls:
        return

    for url in urls:
        result = predict_url(url)

        if result == "Phishing":
            response = (
                "⚠️ **Phishing URL Detected!**\n"
                f"🔗 URL: {url}\n"
                "🚨 Status: Berbahaya / Phishing"
            )
        else:
            response = (
                "✅ **Legitimate URL Detected**\n"
                f"🔗 URL: {url}\n"
                "🟢 Status: Aman / Legitimate"
            )

        await message.channel.send(response)


client.run(TOKEN)