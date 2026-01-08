from telethon import TelegramClient, events
from telethon.tl.functions.messages import ImportChatInviteRequest, CheckChatInviteRequest
from telethon.errors import UserAlreadyParticipantError
import asyncio
import re

# ==========================================
# 👇 မင်းရဲ့ API SETTINGS (ထည့်ပေးထားပြီးသား)
# ==========================================
api_id = 22009063                
api_hash = 'fc7065f35831e39d77eccd52da1f4039' 
phone_number = '+959769262933'

# ==========================================
# 👇 TARGET SETTINGS (Updated Link)
# ==========================================
# 1. Source Channel Invite Hash (Link ထဲက နောက်ဆုံးအပိုင်း)
# Link: https://t.me/+-G9aYBIM4J8xZWVh
SOURCE_INVITE_HASH = '-G9aYBIM4J8xZWVh'

# 2. Decrypt Bot Username
DECRYPT_BOT = '@Unknownscrapperbot'

# 3. Destination Channel ID
DESTINATION_CHANNEL = -1003427673884

# ==========================================

client = TelegramClient('relay_session', api_id, api_hash)

async def main():
    await client.start(phone=phone_number)
    print("🤖 Bot Started...")

    # 1. Source Channel ကို ရှာမယ် (သို့) Join မယ်
    try:
        print(f"🔄 Joining/Locating Source Channel...")
        try:
            updates = await client(ImportChatInviteRequest(SOURCE_INVITE_HASH))
            source_entity = updates.chats[0]
            print(f"✅ Joined new channel: {source_entity.title}")
        except UserAlreadyParticipantError:
            # Already joined, get chat info
            invite = await client(CheckChatInviteRequest(SOURCE_INVITE_HASH))
            source_entity = invite.chat
            print(f"✅ Already joined: {source_entity.title}")
    except Exception as e:
        print(f"❌ Error accessing source channel: {e}")
        return

    source_id = source_entity.id
    print(f"👀 Watching Source Channel ID: {source_id}")
    print(f"wd Sending to Bot: {DECRYPT_BOT}")
    print(f"📂 Forwarding to Your Channel: {DESTINATION_CHANNEL}")

    # -------------------------------------------------------
    # EVENT 1: Channel က AES ကုဒ်တွေကို ဖမ်းပြီး Bot ဆီပို့မယ်
    # -------------------------------------------------------
    @client.on(events.NewMessage(chats=source_id))
    async def aes_handler(event):
        text = event.message.text or ""
        
        # /decrypt AES_ နဲ့စတဲ့ စာကြောင်းကို ရှာမယ်
        if "/decrypt AES_" in text:
            # စာတစ်ကြောင်းလုံးကို ယူမယ် (Command အပြည့်အစုံ)
            # Regex နဲ့ AES ကုဒ်ကို သေချာပြန်ဆွဲထုတ်မယ်
            match = re.search(r'(/decrypt AES_[a-zA-Z0-9\-\_\=\+]+)', text)
            
            if match:
                final_command = match.group(1)
                print(f"📥 Got AES Code! Sending to Bot...")
                
                try:
                    await client.send_message(DECRYPT_BOT, final_command)
                    # Bot ပိတ်မသွားအောင် 3-5 စက္ကန့် စောင့်မယ်
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
            print(f"✅ Decrypted Successfully! Forwarding to Private Channel...")
            
            try:
                # မင်းရဲ့ Private Channel ထဲကို Message ပို့မယ်
                await client.send_message(DESTINATION_CHANNEL, text)
            except Exception as e:
                print(f"❌ Error forwarding to Private Channel: {e}")

    print("🚀 System is Running... Waiting for new AES codes.")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
