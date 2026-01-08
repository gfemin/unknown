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
# 👇 TARGET SETTINGS
# ==========================================
SOURCE_CHANNELS = [
    -1002594842235,  # Unknown Channel
    -1001803262016,  # Other Channel 1
    -1002549684865   # Other Channel 2
]

DECRYPT_BOT = '@Unknownscrapperbot'
DESTINATION_CHANNEL = -1003473556518

# ==========================================

client = TelegramClient('relay_session', api_id, api_hash)

# CC Pattern (ဒီပုံစံကိုပဲ ရှာပြီး ဆွဲထုတ်မယ်)
cc_pattern = r'(\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4})'
# Duplicate စစ်ဖို့ ကဒ်နံပါတ် Pattern
card_num_pattern = r'(\d{15,16})'

# 🔥 Memory for Anti-Duplicate
seen_cards = set()

async def load_history():
    print("⏳ Loading history to prevent duplicates...")
    count = 0
    async for msg in client.iter_messages(DESTINATION_CHANNEL, limit=500):
        if msg.text:
            match = re.search(card_num_pattern, msg.text)
            if match:
                seen_cards.add(match.group(1))
                count += 1
    print(f"✅ Loaded {count} existing cards into memory!")

async def main():
    await client.start(phone=phone_number)
    await load_history()
    
    print("🤖 Clean Forwarder Started...")
    print(f"👀 Watching {len(SOURCE_CHANNELS)} Channels")
    print(f"📂 Forwarding CLEAN CCs to: {DESTINATION_CHANNEL}")

    # -------------------------------------------------------
    # EVENT 1: Source Channel Handling
    # -------------------------------------------------------
    @client.on(events.NewMessage(chats=SOURCE_CHANNELS))
    async def source_handler(event):
        text = event.message.text or ""
        
        # 🟢 CASE 1: AES Encrypted -> Bot ဆီပို့
        if "/decrypt AES_" in text:
            match = re.search(r'(/decrypt AES_[a-zA-Z0-9\-\_\=\+]+)', text)
            if match:
                final_command = match.group(1)
                print(f"🔐 Found AES! Sending to Bot...")
                try:
                    await client.send_message(DECRYPT_BOT, final_command)
                    await asyncio.sleep(4) 
                except: pass

        # 🟢 CASE 2: Plain CC -> သန့်ရှင်းရေးလုပ်ပြီး ပို့မယ်
        elif re.search(cc_pattern, text):
            # CC အပြည့်အစုံကို ဆွဲထုတ်မယ် (စာတွေမပါတော့ဘူး)
            clean_match = re.search(cc_pattern, text)
            if clean_match:
                clean_cc = clean_match.group(1) # cc|mm|yy|cvc သက်သက်
                cc_num = clean_cc.split('|')[0]

                if cc_num in seen_cards:
                    print(f"⚠️ Ignored Duplicate CC: {cc_num}")
                    return

                print(f"💳 Clean CC Found! Forwarding...")
                seen_cards.add(cc_num)
                try:
                    # 'text' အစား 'clean_cc' ကို ပို့လိုက်ပြီ
                    await client.send_message(DESTINATION_CHANNEL, clean_cc)
                except Exception as e:
                    print(f"❌ Error forwarding: {e}")

    # -------------------------------------------------------
    # EVENT 2: Bot Reply Handling (အရေးကြီးဆုံးအပိုင်း) 🔥
    # -------------------------------------------------------
    @client.on(events.NewMessage(chats=DECRYPT_BOT))
    async def bot_reply_handler(event):
        me = await client.get_me()
        if event.sender_id == me.id: return

        text = event.message.text or ""
        
        # Bot ကပို့လိုက်တဲ့ စာထဲက CC ကိုပဲ ရွေးထုတ်မယ်
        clean_match = re.search(cc_pattern, text)
        
        if clean_match:
            clean_cc = clean_match.group(1) # ဒါက cc|mm|yy|cvc သက်သက်ပဲရမယ်
            cc_num = clean_cc.split('|')[0]

            # ⚠️ DUPLICATE CHECK
            if cc_num in seen_cards:
                print(f"⚠️ Ignored Duplicate from Bot: {cc_num}")
                return

            print(f"✅ Decrypted & Cleaned! Forwarding...")
            seen_cards.add(cc_num)
            try:
                # ရှင်းထားတဲ့ ကဒ်ကိုပဲ ပို့မယ် (ရှုပ်တာတွေမပါတော့ဘူး)
                await client.send_message(DESTINATION_CHANNEL, clean_cc)
            except Exception as e:
                print(f"❌ Error forwarding: {e}")

    print("🚀 System is Running...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
