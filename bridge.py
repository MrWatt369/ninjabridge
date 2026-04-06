import requests
import os

def send_to_telegram(bot_token, chat_id, message, photo_path=None):
    """
    Sends a message to a Telegram chat. If photo_path is provided, sends it as a photo with a caption.
    """
    if photo_path and os.path.exists(photo_path):
        url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"
        # Telegram caption limit is 1024 characters.
        caption = message[:1024] if message else ""
        
        try:
            with open(photo_path, "rb") as photo:
                files = {"photo": photo}
                payload = {"chat_id": chat_id, "caption": caption}
                response = requests.post(url, data=payload, files=files, timeout=15)
                response.raise_for_status()
                
                # If message was truncated, send the rest as a text message
                if len(message) > 1024:
                    send_to_telegram(bot_token, chat_id, f"...continued: {message[1024:]}")
                    
                return True
        except Exception as e:
            print(f"Error sending photo to Telegram: {e}")
            return False
    else:
        url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message}
        try:
            response = requests.post(url, json=payload, timeout=15)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending message to Telegram: {e}")
            return False

def send_to_discord(webhook_url, message, photo_path=None):
    """
    Sends a message to a Discord webhook. If photo_path is provided, sends it as an attachment.
    """
    if photo_path and os.path.exists(photo_path):
        try:
            with open(photo_path, "rb") as photo:
                files = {"file": photo}
                payload = {"content": message[:2000]} # Discord character limit is 2000
                response = requests.post(webhook_url, data=payload, files=files, timeout=15)
                response.raise_for_status()
                
                if len(message) > 2000:
                    send_to_discord(webhook_url, f"...continued: {message[2000:]}")
                    
                return True
        except Exception as e:
            print(f"Error sending photo to Discord: {e}")
            return False
    else:
        payload = {"content": message[:2000]}
        try:
            response = requests.post(webhook_url, json=payload, timeout=15)
            response.raise_for_status()
            return True
        except Exception as e:
            print(f"Error sending message to Discord: {e}")
            return False

if __name__ == "__main__":
    # Test placeholders
    pass
