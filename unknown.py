from telethon import TelegramClient, events
import asyncio
import re

# ==========================================
# 👇 API SETTINGS
# ==========================================
api_id = 38370771                
api_hash = 'c6bf6948172c59515b6545af34ec8aaf' 
phone_number = '+959794663260'

# ==========================================
# 👇 TARGET SETTINGS (Channel ID Version)
# ==========================================

# 1. Source Channel ID (Unknown Channel)
# ⚠️ ဒီ Channel ထဲကို မင်းအကောင့် ဝင်ပြီးသားဖြစ်ရပါမယ်
SOURCE_CHANNEL_ID = -1002594842235

# 2. Decrypt Bot Username
DECRYPT_BOT = '@Unknownscrapperbot'

# 3. Destination Channel ID (မင်းရဲ့ Private Channel)
DESTINATION_CHANNEL = -1003473556518

# ==========================================

client = TelegramClient('relay_session', api_id, api_hash)

async def main():
    await client.start(phone=phone_number)
    print("🤖 Bot Started (ID Mode)...")
    print(f"👀 Watching Source ID: {SOURCE_CHANNEL_ID}")
    print(f"wd Sending to Bot: {DECRYPT_BOT}")
    print(f"📂 Forwarding to Your Channel: {DESTINATION_CHANNEL}")

    # -------------------------------------------------------
    # EVENT 1: Channel ID ကနေ AES ကုဒ်တွေကို ဖမ်းမယ်
    # -------------------------------------------------------
    @client.on(events.NewMessage(chats=SOURCE_CHANNEL_ID))
    async def aes_handler(event):
        text = event.message.text or ""
        
        # /decrypt AES_ နဲ့စတဲ့ စာကြောင်းကို ရှာမယ်
        if "/decrypt AES_" in text:
            # Regex နဲ့ AES ကုဒ်ကို သေချာပြန်ဆွဲထုတ်မယ်
            match = re.search(r'(/decrypt AES_[a-zA-Z0-9\-\_\=\+]+)', text)
            
            if match:
                final_command = match.group(1)
                print(f"📥 Found AES! Sending to Bot...")
                
                try:
                    await client.send_message(DECRYPT_BOT, final_command)
                    # Bot ပိတ်မသွားအောင် 4 စက္ကန့် စောင့်မယ်
                    await asyncio.sleep(4) 
                except Exception as e:
                    print(f"❌ Error sending to bot: {e}")

    # -------------------------------------------------------
    # EVENT 2: Bot ကပြန်ပို့တဲ့ အဖြေကို Private Channel ထဲပို့မယ်
    # -------------------------------------------------------
    @client.on(events.NewMessage(chats=DECRYPT_BOT))
    async def bot_reply_handler(event):
        # ကိုယ်ပို့လိုက်တဲ့ message မဟုတ်ဘဲ bot reply ဖြစ်မှယူမယ်
        me = await client.get_me()
        if event.sender_id == me.id:
            return

        text = event.message.text or ""
        
        # ကဒ်ပုံစံ (ဂဏန်း ၁၅ လုံးအထက်) ပါမှ Private Channel ထဲပို့မယ်
        if re.search(r'\d{15,16}', text):
            print(f"✅ Decrypted! Forwarding to Private Channel...")
            try:
                await client.send_message(DESTINATION_CHANNEL, text)
            except Exception as e:
                print(f"❌ Error forwarding: {e}")

    print("🚀 System is Running... Waiting for new AES codes.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
