import discord
import requests
from bs4 import BeautifulSoup
import re
import asyncio 

TOKEN = "YOUR_TOKEN_HERE"
INTENTS = discord.Intents.default()

bot = discord.Client(intents=INTENTS)
tree = discord.app_commands.CommandTree(bot)

@bot.event
async def on_ready():
    await tree.sync()
    print(f"Connected as {bot.user}")

def scrape_pcpartpicker(url):
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        return None

    soup = BeautifulSoup(response.text, "html.parser")

    title_tag = soup.find("h1")
    title = title_tag.text.strip() if title_tag else "Configuration inconnue" 
    image_tag = soup.find("img", {"class": re.compile(r"^pcpp-part-image")})
    image_url = image_tag["src"] if image_tag else None

    components = []
    total_price = "Price unavailable"
    part_rows = soup.select("tr.tr__product")
    
    for row in part_rows:
        part_name_tag = row.select_one("td.td__name a")
        part_price_tag = row.select_one("td.td__price")
        part_image_tag = row.select_one("td.td__image img")
        
        if part_name_tag:
            part_name = part_name_tag.text.strip()
            part_price = part_price_tag.text.strip() if part_price_tag else "Unknown price"
            part_image = part_image_tag["src"] if part_image_tag else None
            
            if part_image:
                if part_image.startswith("http:"):
                    part_image = part_image.replace("http:", "https:")
                elif part_image.startswith("//"):
                    part_image = "https:" + part_image

            components.append({"name": part_name, "price": part_price, "image": part_image})


    total_price_tag = soup.select_one(".tr__total .td__price")
    if total_price_tag:
        total_price = total_price_tag.text.strip()

    total_price_value = 0.0
    if "€" in total_price:
        total_price_value = float(re.sub(r'[^\d.]', '', total_price))
    elif "$" in total_price:
        total_price_value = float(re.sub(r'[^\d.]', '', total_price))

    return {"title": title, "image_url": image_url, "components": components, "total_price": total_price_value, "currency": "€" if "€" in total_price else "$"}

@tree.command(name="pcpartpicker", description="Display a PCPartPicker configuration")
async def pcpartpicker_command(interaction: discord.Interaction, url: str):
    if "pcpartpicker.com" not in url:
        await interaction.response.send_message("Invalid link! Please provide a PCPartPicker link.")
        return

    data = scrape_pcpartpicker(url)
    if not data:
        await interaction.response.send_message("Unable to fetch information.")
        return

    await interaction.response.defer()

    gif_url = ""
    if data["currency"] == "€":
        if data["total_price"] > 1300:
            gif_url = "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZTk1dGo5djFwMXE5aGY0OHkwNHo2MHY2NXBrdmNscXYwa3RkODBmNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/G69rTjPLi5YcpXTX5k/giphy.gif"  
        elif data["total_price"] > 700:
            gif_url = "https://media1.giphy.com/media/3o6nV2zbDxVuGcEbaE/giphy.gif?cid=6c09b952are0ryx3q4wn88h6crnes5deawxyr69nq5f4tusf&ep=v1_gifs_search&rid=giphy.gif&ct=g"  
        elif data["total_price"] < 500:
            gif_url = "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjVka3VwenA0M29ib2xkNXdmeTRwYTR6Nm80cnAzeHBjeWh4b2d1MyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/t1QH3xvhEUhe9Tjf5j/giphy.gif"  
    else:
        if data["total_price"] > 1300:
            gif_url = "https://media2.giphy.com/media/v1.Y2lkPTc5MGI3NjExZTk1dGo5djFwMXE5aGY0OHkwNHo2MHY2NXBrdmNscXYwa3RkODBmNyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/G69rTjPLi5YcpXTX5k/giphy.gif" 
        elif data["total_price"] > 700:
            gif_url = "https://media1.giphy.com/media/3o6nV2zbDxVuGcEbaE/giphy.gif?cid=6c09b952are0ryx3q4wn88h6crnes5deawxyr69nq5f4tusf&ep=v1_gifs_search&rid=giphy.gif&ct=g" 
        elif data["total_price"] < 500:
            gif_url = "https://media3.giphy.com/media/v1.Y2lkPTc5MGI3NjExYjVka3VwenA0M29ib2xkNXdmeTRwYTR6Nm80cnAzeHBjeWh4b2d1MyZlcD12MV9pbnRlcm5hbF9naWZfYnlfaWQmY3Q9Zw/t1QH3xvhEUhe9Tjf5j/giphy.gif" 

    for component in data["components"]:
        if component["image"] and component["image"].startswith("https"):
            component_embed = discord.Embed(title=f"{component['name']} - {component['price']}", color=discord.Color.blue())
            component_embed.set_image(url=component["image"])
            await interaction.followup.send(embed=component_embed) 
            await asyncio.sleep(1.5)  

    if gif_url:
        gif_embed = discord.Embed(title=f"Total Price: {data['total_price']} {data['currency']}", color=discord.Color.blue())
        gif_embed.set_image(url=gif_url)
        await interaction.followup.send(embed=gif_embed) 
bot.run(TOKEN)
