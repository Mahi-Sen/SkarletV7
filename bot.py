import sys, glob, importlib, logging, logging.config, pytz, asyncio
from pathlib import Path
from aiohttp import ClientSession, web  # ClientSession yaha add kiya

# Logging setup
logging.config.fileConfig('logging.conf')
logging.getLogger().setLevel(logging.INFO)
logging.getLogger("pyrogram").setLevel(logging.ERROR)
logging.getLogger("cinemagoer").setLevel(logging.ERROR)

from pyrogram import Client, idle
from database.users_chats_db import db
from info import *
from utils import temp
from typing import Union, Optional, AsyncGenerator
from Script import script 
from datetime import date, datetime 
from plugins import web_server
from plugins.clone import restart_bots

from TechVJ.bot import TechVJBot
from TechVJ.util.keepalive import ping_server
from TechVJ.bot.clients import initialize_clients

ppath = "plugins/*.py"
files = glob.glob(ppath)
TechVJBot.start()
loop = asyncio.get_event_loop()

# Naya Render ping function (1 minute ka interval)
async def ping_render():
    RENDER_URL = "https://skarletv7.onrender.com"  # 🔴 Yaha apna Render URL daalna
    while True:
        try:
            async with ClientSession() as session:
                async with session.get(RENDER_URL) as resp:
                    print(f"✅ Render Pinged! Status: {resp.status}")
        except Exception as e:
            print(f"❌ Ping Failed: {str(e)}")
        await asyncio.sleep(60)  # 60 sec = 1 minute (Badal sakta hai)

async def start():
    print('\n')
    print('🚀 Bot Starting...')
    bot_info = await TechVJBot.get_me()
    
    # Background tasks shuru
    asyncio.create_task(ping_render())  # Render pinging
    if ON_HEROKU:
        asyncio.create_task(ping_server())  # Heroku wala (agar chahiye)

    await initialize_clients()
    
    # Plugins load karne ka hissa (tera existing code)
    for name in files:
        with open(name) as a:
            patt = Path(a.name)
            plugin_name = patt.stem.replace(".py", "")
            plugins_dir = Path(f"plugins/{plugin_name}.py")
            import_path = "plugins.{}".format(plugin_name)
            spec = importlib.util.spec_from_file_location(import_path, plugins_dir)
            load = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(load)
            sys.modules["plugins." + plugin_name] = load
            print(f"🔥 Plugin Loaded: {plugin_name}")

    # Banned users/chats
    b_users, b_chats = await db.get_banned()
    temp.BANNED_USERS = b_users
    temp.BANNED_CHATS = b_chats
    
    # Bot info set karna
    me = await TechVJBot.get_me()
    temp.BOT = TechVJBot
    temp.ME = me.id
    temp.U_NAME = me.username
    temp.B_NAME = me.first_name
    
    # Logging aur startup message
    logging.info(script.LOGO)
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    time = now.strftime("%H:%M:%S %p")
    await TechVJBot.send_message(chat_id=LOG_CHANNEL, text=script.RESTART_TXT.format(today, time))
    
    # Clone mode check
    if CLONE_MODE == True:
        print("♻️ Restarting Clone Bots...")
        await restart_bots()
        print("✅ Clones Restarted!")
    
    # Web server setup
    app = web.AppRunner(await web_server())
    await app.setup()
    bind_address = "0.0.0.0"
    await web.TCPSite(app, bind_address, PORT).start()
    
    # Idle mode
    await idle()

if __name__ == '__main__':
    try:
        loop.run_until_complete(start())
    except KeyboardInterrupt:
        logging.info('❌ Bot Stopped!')
