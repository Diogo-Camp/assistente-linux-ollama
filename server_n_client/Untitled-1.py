# ```python
# import logging
# from telethon import TelegramClient, events

# # Seu API_ID e API_HASH aqui
# API_ID = 12345678
# API_HASH = "your_api_hash"

# bot = TelegramClient("my_session", API_ID, API_HASH)

# @bot.on(events.NewMessage(outgoing=True, pattern="/start"))
# async def start_command(event):
#     await event.reply("/ola")

# bot.start()
# bot.run_until_disconnected()
# ```

# Lembre-se de substituir o seu `API_ID`, `API_HASH` e o nome da sessão pelo seu próprio. Você também precisará instalar a biblioteca Telethon se você não já não a possui:

# ```bash
# pip install telegram-python3
# ```

# Após isso, rode o script com o seguinte comando:

# ```bash
# python nome_do_seu_script.py
# ```