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

# (Checker Bot setting ကို ဖျက်လိုက်ပါပြီ)

# ==========================================

client = TelegramClient('relay_session', api_id, api_hash)

# CC Pattern
cc_pattern = r'(\d{15,16}\|\d{1,2}\|\d{2,4}\|\d{3,4})'
card_num_pattern = r'(\d{15,16})'

# 🔥 Memory for Anti-Duplicate
seen_cards = set()

async def load_history():
    print("⏳ Loading history to prevent duplicates...")
    count = 0
    try:
        async for msg in client.iter_messages(DESTINATION_CHANNEL, limit=500):
            if msg.text:
                match = re.search(card_num_pattern, msg.text)
                if match:
                    seen_cards.add(match.group(1))
                    count += 1
    except Exception as e:
        print(f"⚠️ History Load Error: {e}")
    print(f"✅ Loaded {count} existing cards into memory!")

async def main():
    await client.start(phone=phone_number)
    await load_history()
    
    print("🤖 Super Forwarder Started...")
    print(f"👀 Watching: {len(SOURCE_CHANNELS)} Channels")
    print(f"📂 Save to: {DESTINATION_CHANNEL}")
    print("❌ Checker Bot: DISABLED")

    # -------------------------------------------------------
    # EVENT 1: Source Channel Handling
    # -------------------------------------------------------
    @client.on(events.NewMessage(chats=SOURCE_CHANNELS))
    async def source_handler(event):
        text = event.message.text or ""
        
        # 🟢 CASE 1: AES Encrypted -> Decrypt Bot ဆီပို့
        if "/decrypt AES_" in text:
            match = re.search(r'(/decrypt AES_[a-zA-Z0-9\-\_\=\+]+)', text)
            if match:
                final_command = match.group(1)
                print(f"🔐 Found AES! Sending to Decrypt Bot...")
                try:
                    await client.send_message(DECRYPT_BOT, final_command)
                    # Decrypt Bot က Reply ပြန်ဖို့ အချိန်ခဏစောင့်ပေးတာ (မဖြုတ်ရ)
                    await asyncio.sleep(4) 
                except: pass

        # 🟢 CASE 2: Plain CC -> Channel ကိုပဲ ပို့မယ် (Checker မပို့တော့ဘူး)
        elif re.search(cc_pattern, text):
            clean_match = re.search(cc_pattern, text)
            if clean_match:
                clean_cc = clean_match.group(1)
                cc_num = clean_cc.split('|')[0]

                if cc_num in seen_cards:
                    print(f"⚠️ Ignored Duplicate CC: {cc_num}")
                    return

                print(f"💳 New CC Found! Saving to Channel...")
                seen_cards.add(cc_num)
                
                try:
                    # 🔥 Only Save to Destination Channel
                    await client.send_message(DESTINATION_CHANNEL, clean_cc)
                    print(f"✅ Saved: {clean_cc}")

                except Exception as e:
                    print(f"❌ Error forwarding: {e}")

    # -------------------------------------------------------
    # EVENT 2: Decrypt Bot Reply Handling
    # -------------------------------------------------------
    @client.on(events.NewMessage(chats=DECRYPT_BOT))
    async def bot_reply_handler(event):
        me = await client.get_me()
        if event.sender_id == me.id: return

        text = event.message.text or ""
        
        clean_match = re.search(cc_pattern, text)
        if clean_match:
            clean_cc = clean_match.group(1) 
            cc_num = clean_cc.split('|')[0]

            if cc_num in seen_cards:
                print(f"⚠️ Ignored Duplicate from Decrypt Bot: {cc_num}")
                return

            print(f"✅ Decrypted! Saving to Channel...")
            seen_cards.add(cc_num)
            
            try:
                # 🔥 Only Save to Destination Channel
                await client.send_message(DESTINATION_CHANNEL, clean_cc)
                print(f"✅ Saved: {clean_cc}")

            except Exception as e:
                print(f"❌ Error forwarding: {e}")

    print("🚀 System is Running...")
    await client.run_until_disconnected()

if __name__ == '__main__':
    asyncio.run(main())
