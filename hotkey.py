import json
import os
import time

def get_config_path():
    """Points to a persistent location in Windows AppData for standalone sharing."""
    appdata = os.getenv('APPDATA')
    app_dir = os.path.join(appdata, "NinjaBridge")
    if not os.path.exists(app_dir):
        os.makedirs(app_dir)
    return os.path.join(app_dir, "config.json")

CONFIG_FILE = get_config_path()

def load_config():
    if not os.path.exists(CONFIG_FILE):
        return {
            "ai_provider": "gemini",
            "ai_api_key": "",
            "bridge_provider": "telegram",
            "telegram_bot_token": "",
            "telegram_chat_id": "",
            "hotkey": "ctrl+shift", "ai_model": "",
            "workflows": [
                {"hotkey": "ctrl+!+shift", "prompt": "Analyze the coding problem in this image. 1. Identify core algorithm. 2. Provide logic plan. 3. List 3 critical edge cases."},
                {"hotkey": "alt+ctrl+shift", "prompt": "Write the most efficient solution in Python. Include Time and Space Complexity at the top."},
                {"hotkey": "ctrl+#+shift", "prompt": "Suggest optimized version. Trade-offs. 2 sentences on scalability."},
                {"hotkey": "ctrl+$+shift", "prompt": "Find and fix the bug in the code. Tell me the line number and why it was failing."}
            ],
            "auto_start": False
        }
    try:
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    except:
        return {}

def save_config(config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=4)

class StealthEngine:
    def __init__(self):
        self.config = load_config()
        self.running = False
        self.hooks = []

    def start(self, callback=None):
        if self.running: return
        
        # Delayed import for speed
        import keyboard
        
        self.config = load_config()
        workflows = self.config.get("workflows", [])
        
        # Register Workflows
        for wf in workflows:
            hk = wf.get("hotkey", "").lower().strip()
            if not hk: continue
            prompt = wf.get("prompt", "")
            hook = keyboard.add_hotkey(hk, lambda p=prompt: self.on_trigger(p, callback))
            self.hooks.append(hook)
            print(f"  Listening for {hk}")

        # Kill Switch Implementation
        kill_hk = self.config.get("kill_switch", "ctrl+alt+k").lower().strip()
        if kill_hk:
            hook = keyboard.add_hotkey(kill_hk, self.execute_kill)
            self.hooks.append(hook)
            print(f"  Kill Switch armed: {kill_hk}")

        self.running = True

    def execute_kill(self):
        print("KILL SWITCH TRIGGERED. Terminating system.")
        os._exit(0)

    def stop(self):
        if not self.running: return
        import keyboard
        keyboard.unhook_all_hotkeys()
        self.hooks = []
        self.running = False
        print("Engine stopped.")

    def on_trigger(self, prompt, callback=None):
        """Ultra-smooth trigger flow with minimal blocking."""
        start_t = time.perf_counter()
        if callback: callback("⚡ INITIATING FLOW")
        
        self.config = load_config()
        
        # 1. Capture (Lazy)
        t1 = time.perf_counter()
        from capture import capture_screen
        monitor = self.config.get("monitor", 1)
        image_path = capture_screen(monitor_index=monitor)
        cap_t = time.perf_counter() - t1
        if callback: callback(f"📸 Captured ({cap_t:.1f}s)")
        
        # 2. AI Analysis (Offloaded & Lazy)
        t2 = time.perf_counter()
        if callback: callback("🤖 Processing with AI...")
        
        ai_choice = self.config.get("ai_provider", "gemini")
        api_key = self.config.get("ai_api_key", "")
        ai_model = self.config.get("ai_model", "")
        
        result = ""
        try:
            if ai_choice == "gemini":
                from ai_handler import process_image_gemini
                result = process_image_gemini(api_key, image_path, prompt)
            elif ai_choice in ["openai", "openrouter", "nvidia"]:
                from ai_handler import process_image_openai
                # Super-lightweight defaults
                base_urls = {"openrouter": "https://openrouter.ai/api/v1", "nvidia": "https://integrate.api.nvidia.com/v1"}
                def_models = {"openai": "gpt-4o-mini", "openrouter": "google/gemini-2.0-flash-001", "nvidia": "meta/llama-3.2-11b-vision-instruct"}
                model = ai_model or def_models.get(ai_choice, "gpt-4o-mini")
                result = process_image_openai(api_key, image_path, prompt, base_url=base_urls.get(ai_choice), model=model)
            elif ai_choice == "anthropic":
                from ai_handler import process_image_anthropic
                result = process_image_anthropic(api_key, image_path, prompt)
        except Exception as e:
            result = f"Error: {e}"
        
        ai_t = time.perf_counter() - t2
        if not result: result = "No response from AI."
        if callback: callback(f"🧠 AI Solved ({ai_t:.1f}s)")

        # 3. Bridge (Non-blocking Threaded Delivery)
        import threading
        full_message = f"🔹 PROMPT: {prompt}\n\n🤖 ANSWER: {result}"
        
        def delivery():
            t3 = time.perf_counter()
            self.send_bridge_msg(full_message, image_path=image_path)
            bridge_t = time.perf_counter() - t3
            total_t = time.perf_counter() - start_t
            if callback: 
                callback(f"🚀 Bridge Delivered ({bridge_t:.1f}s)")
                callback(f"✅ Total: {total_t:.1f}s")
        
        threading.Thread(target=delivery, daemon=True).start()

    def send_bridge_msg(self, text, image_path=None):
        """Sends raw text/image to the configured bridge (Lazy loaded)."""
        bridge_choice = self.config.get("bridge_provider", "telegram")
        if bridge_choice == "telegram":
            from bridge import send_to_telegram
            return send_to_telegram(self.config.get("telegram_bot_token", ""), self.config.get("telegram_chat_id", ""), text, photo_path=image_path)
        elif bridge_choice == "discord":
            from bridge import send_to_discord
            return send_to_discord(self.config.get("discord_webhook_url", ""), text, photo_path=image_path)
        return False

    def show_toast(self, title, message):
        """Sleek startup toast using minimal system resources."""
        import subprocess
        ps_cmd = f'''
        $t = "{title}"; $m = "{message}";
        [reflection.assembly]::loadwithpartialname("System.Windows.Forms");
        [reflection.assembly]::loadwithpartialname("System.Drawing");
        $bal = New-Object System.Windows.Forms.NotifyIcon;
        $bal.Icon = [System.Drawing.Icon]::ExtractAssociatedIcon((Get-Process -id $pid).Path);
        $bal.BalloonTipIcon = "Info";
        $bal.BalloonTipText = $m; $bal.BalloonTipTitle = $t;
        $bal.Visible = $true; $bal.ShowBalloonTip(5000);
        '''
        try: subprocess.Popen(["powershell", "-Command", ps_cmd], creationflags=subprocess.CREATE_NO_WINDOW)
        except: pass
