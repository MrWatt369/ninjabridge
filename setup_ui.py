import customtkinter as ctk
import json
import os
import threading
import keyboard
import winreg
from hotkey import load_config, save_config, StealthEngine

# --- CONSTANTS & STYLE ---
ACCENT_COLOR = "#2ECC71"  # Emerald
BG_COLOR = "#0F1113"      # Deep Matte
SIDEBAR_COLOR = "#161B22" # Dark Slate
CARD_COLOR = "#1C2128"    # Lighter Slate for sections
TEXT_COLOR = "#F0F6FC"
SUBTEXT_COLOR = "#8B949E"

class HotkeyRecorder(ctk.CTkEntry):
    def __init__(self, master, **kwargs):
        super().__init__(master, 
                         fg_color="#0D1117", 
                         border_color="#30363D", 
                         text_color=ACCENT_COLOR,
                         font=("Inter", 12, "bold"),
                         height=35,
                         justify="center",
                         **kwargs)
        self.bind("<KeyPress>", self.on_key)
        self._keys = set()
        self.configure(state="readonly", placeholder_text="--- RECORDING ---")
        self._recording = False

    def on_key(self, event):
        if not self._recording: return "break"
        key = event.keysym.lower()
        mapping = {
            "control_l": "ctrl", "control_r": "ctrl",
            "shift_l": "shift", "shift_r": "shift",
            "alt_l": "alt", "alt_r": "alt",
            "win_l": "windows", "win_r": "windows"
        }
        key = mapping.get(key, key)
        self._keys.add(key)
        self.update_text()
        return "break"

    def start_recording(self):
        self._recording = True
        self._keys = set()
        self.configure(state="normal", border_color=ACCENT_COLOR)
        self.delete(0, "end")
        self.focus_set()

    def stop_recording(self):
        self._recording = False
        self.configure(state="readonly", border_color="#30363D")

    def update_text(self):
        self.configure(state="normal")
        self.delete(0, "end")
        self.insert(0, "+".join(sorted(list(self._keys))))
        self.configure(state="readonly")

class SetupApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.title("NINJA BRIDGE | AI STEALTH")
        self.geometry("1000x750")
        self.configure(fg_color=BG_COLOR)
        
        ctk.set_appearance_mode("dark")
        
        self.config = load_config()
        self.engine = StealthEngine()
        self.engine_active = False
        
        self._init_layout()
        
    def _init_layout(self):
        # Navigation Sidebar
        self.sidebar = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color=SIDEBAR_COLOR, border_width=0)
        self.sidebar.pack(side="left", fill="y")
        
        # Logo with Glow Effect (Simulation)
        # Logo Frame
        self.logo_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.logo_frame.pack(pady=(60, 40))
        
        self.logo_text = ctk.CTkLabel(self.logo_frame, text="NINJA BRIDGE", font=("Outfit", 22, "bold"), text_color=TEXT_COLOR)
        self.logo_text.pack()

        self.tabs = {}
        self._create_tab_button("Config", "⚡")
        self._create_tab_button("Prompts", "📝")
        self._create_tab_button("Privacy", "🔒")
        self._create_tab_button("Console", "💻")
        
        # Bottom Actions
        self.action_frame = ctk.CTkFrame(self.sidebar, fg_color="transparent")
        self.action_frame.pack(side="bottom", pady=30, padx=20, fill="x")

        self.engine_btn = ctk.CTkButton(self.action_frame, text="INITIATE ENGINE", height=45, 
                                       fg_color="#30363D", hover_color="#3FB950", 
                                       font=("Outfit", 14, "bold"), command=self.toggle_engine)
        self.engine_btn.pack(pady=10, fill="x")
        
        self.stealth_btn = ctk.CTkButton(self.action_frame, text="STEALTH MODE", height=45, 
                                        fg_color="#238636", hover_color="#2EA043", 
                                        font=("Outfit", 14, "bold"), command=self.go_stealth)
        self.stealth_btn.pack(pady=5, fill="x")
        
        self.kill_btn = ctk.CTkButton(self.action_frame, text="TERMINATE ALL", height=40, 
                                     fg_color="transparent", border_width=1, border_color="#F85149", 
                                     text_color="#F85149", hover_color="#F85149",
                                     font=("Outfit", 12, "bold"), command=self.engine.execute_kill)
        self.kill_btn.pack(pady=(20, 0), fill="x")

        # Container
        self.view = ctk.CTkFrame(self, corner_radius=15, fg_color=BG_COLOR, border_width=0)
        self.view.pack(side="right", expand=True, fill="both", padx=40, pady=40)
        
        self.frames = {}
        self._init_config_view()
        self._init_prompts_view()
        self._init_privacy_view()
        self._init_console_view()
        
        self.show_tab("Config")

    def _create_tab_button(self, name, icon):
        btn = ctk.CTkButton(self.sidebar, text=f"{icon}  {name}", 
                           height=45, fg_color="transparent", 
                           text_color=SUBTEXT_COLOR, anchor="w", 
                           font=("Inter", 14, "bold"), 
                           hover_color="#1C2128",
                           command=lambda n=name: self.show_tab(n))
        btn.pack(pady=3, padx=15, fill="x")
        self.tabs[name] = btn

    def show_tab(self, name):
        for frame in self.frames.values(): frame.pack_forget()
        for btn in self.tabs.values(): btn.configure(fg_color="transparent", text_color=SUBTEXT_COLOR)
        
        self.frames[name].pack(expand=True, fill="both")
        self.tabs[name].configure(fg_color="#1C2128", text_color=ACCENT_COLOR)

    def _card_section(self, master, title):
        card = ctk.CTkFrame(master, fg_color=CARD_COLOR, border_width=1, border_color="#30363D", corner_radius=12)
        card.pack(fill="x", pady=15, padx=5)
        lbl = ctk.CTkLabel(card, text=title, font=("Outfit", 12, "bold"), text_color=ACCENT_COLOR)
        lbl.pack(anchor="w", padx=20, pady=(15, 5))
        inner = ctk.CTkFrame(card, fg_color="transparent")
        inner.pack(fill="x", padx=20, pady=(0, 15))
        return inner

    def _init_config_view(self):
        f = ctk.CTkFrame(self.view, fg_color="transparent")
        self.frames["Config"] = f
        
        ctk.CTkLabel(f, text="Core Settings", font=("Outfit", 32, "bold"), text_color=TEXT_COLOR).pack(pady=(0, 30), anchor="w")
        
        ai_card = self._card_section(f, "ARTIFICIAL INTELLIGENCE CORE")
        self.ai_prov = ctk.CTkComboBox(ai_card, values=["gemini", "openai", "anthropic", "openrouter", "nvidia", "moonshot", "custom"], width=180, font=("Inter", 12))
        self.ai_prov.set(self.config.get("ai_provider", "gemini"))
        self.ai_prov.pack(side="left", padx=(0, 10))
        
        ai_model_v = self.config.get("ai_model", "")
        self.ai_model = ctk.CTkEntry(ai_card, placeholder_text="Advanced Model ID", width=350, border_color="#30363D")
        if ai_model_v: self.ai_model.insert(0, ai_model_v)
        self.ai_model.pack(side="left", expand=True, fill="x")

        self.ai_key = ctk.CTkEntry(f, placeholder_text="Universal API Key (Private Key)", width=600, show="*", height=40, font=("Consolas", 12))
        key_v = self.config.get("ai_api_key", "")
        if key_v: self.ai_key.insert(0, key_v)
        self.ai_key.pack(pady=10, anchor="w")

        self.ai_url = ctk.CTkEntry(f, placeholder_text="Custom API Base URL (For 'custom' provider, e.g. https://api.moonshot.cn/v1)", width=600, height=40)
        url_v = self.config.get("ai_base_url", "")
        if url_v: self.ai_url.insert(0, url_v)
        self.ai_url.pack(pady=10, anchor="w")

        msg_card = self._card_section(f, "COMMUNICATION BRIDGE")
        self.br_prov = ctk.CTkComboBox(msg_card, values=["telegram", "discord"], width=180)
        self.br_prov.set(self.config.get("bridge_provider", "telegram"))
        self.br_prov.pack(side="left", padx=(0, 10))
        
        self.br_id = ctk.CTkEntry(msg_card, placeholder_text="Secure Chat / Channel ID", width=350)
        id_v = self.config.get("telegram_chat_id", "")
        if id_v: self.br_id.insert(0, id_v)
        self.br_id.pack(side="left", expand=True, fill="x")

        self.br_token = ctk.CTkEntry(f, placeholder_text="Bot Authentication Token", width=600, height=40)
        tok_v = self.config.get("telegram_bot_token", "")
        if tok_v: self.br_token.insert(0, tok_v)
        self.br_token.pack(pady=10, anchor="w")

        save_btn = ctk.CTkButton(f, text="SYNC CONFIGURATION", command=self.save_general, width=220, height=40, fg_color=ACCENT_COLOR, text_color="#000000", font=("Outfit", 14, "bold"))
        save_btn.pack(side="bottom", pady=20, anchor="e")

    def _init_prompts_view(self):
        f = ctk.CTkFrame(self.view, fg_color="transparent")
        self.frames["Prompts"] = f
        
        ctk.CTkLabel(f, text="AI Workflows", font=("Outfit", 32, "bold")).pack(pady=(0, 30), anchor="w")

        create_box = self._card_section(f, "NEW STEALTH HOOK")
        
        hk_side = ctk.CTkFrame(create_box, fg_color="transparent")
        hk_side.pack(side="left", padx=10, fill="y")
        
        self.hk_preset = ctk.CTkComboBox(hk_side, values=["Record New...", "ctrl+shift", "alt+shift", "alt+f1"], width=130)
        self.hk_preset.pack(pady=5)
        
        self.new_hk_entry = HotkeyRecorder(hk_side, width=130)
        self.new_hk_entry.pack(pady=5)
        
        hb = ctk.CTkFrame(hk_side, fg_color="transparent")
        hb.pack()
        ctk.CTkButton(hb, text="REC", width=60, height=26, fg_color=ACCENT_COLOR, text_color="black", command=self.new_hk_entry.start_recording).pack(side="left", padx=2)
        ctk.CTkButton(hb, text="CLR", width=60, height=26, fg_color="#30363D", command=self.new_hk_entry.stop_recording).pack(side="left", padx=2)
        
        prompt_side = ctk.CTkFrame(create_box, fg_color="transparent")
        prompt_side.pack(side="left", padx=20, expand=True, fill="both")
        
        self.new_prompt_box = ctk.CTkTextbox(prompt_side, height=110, fg_color="#0D1117", border_color="#30363D", border_width=1)
        
        # --- QUICK TEMPLATES ---
        self.templates = {
            "Tech Summary": "Summarize the technical documentation in this image. Highlight key parameters and implementation steps.",
            "Logic Flow": "Identify the core logic of this code block. Explain what it does as if I am a senior developer.",
            "Bug Hunt": "Analyze this snippet and identify potential edge cases, security vulnerabilities, or logical bugs.",
            "Meeting Notes": "Extract the action items, key decisions, and follow-up tasks from these meeting notes.",
            "UI/UX Audit": "What is the primary customer journey being highlighted on this dashboard? Suggest three improvements for clarity.",
            "Accessibility": "Describe the visual hierarchy of this page for screen-reader optimization. What is the most important element?"
        }

        def apply_template(choice):
            if choice in self.templates:
                self.new_prompt_box.delete("1.0", "end")
                self.new_prompt_box.insert("1.0", self.templates[choice])
                self.template_selector.set("Quick Templates")

        self.template_selector = ctk.CTkOptionMenu(prompt_side, 
                                                 values=["Quick Templates"] + list(self.templates.keys()),
                                                 command=apply_template,
                                                 fg_color="#1C2128", button_color="#30363D", button_hover_color=ACCENT_COLOR,
                                                 font=("Inter", 11, "bold"))
        self.template_selector.pack(fill="x", pady=(0, 5))
        self.new_prompt_box.pack(fill="both", expand=True, pady=5)
        
        def quick_add():
            hk = self.new_hk_entry.get() if self.hk_preset.get() == "Record New..." else self.hk_preset.get()
            hk = hk.lower().strip()
            prompt = self.new_prompt_box.get("1.0", "end-1c").strip()
            
            if not hk or not prompt: return
            
            # Uniqueness Check
            if any(w['hotkey'].lower() == hk for w in self.workflows):
                self.update_log(f"Error: Hotkey '{hk}' is already assigned.")
                return

            self.workflows.append({"hotkey": hk, "prompt": prompt})
            self._refresh_wf_ui()
            self.new_hk_entry.configure(state="normal"); self.new_hk_entry.delete(0, "end"); self.new_hk_entry.configure(state="readonly")
            self.new_prompt_box.delete("1.0", "end")
        
        ctk.CTkButton(create_box, text="+", width=60, height=140, fg_color=ACCENT_COLOR, text_color="black", font=("Inter", 24, "bold"), command=quick_add).pack(side="right", padx=5)

        self.wf_list = ctk.CTkScrollableFrame(f, height=300, fg_color="transparent")
        self.wf_list.pack(fill="both", expand=True, pady=10)
        
        self.workflows = self.config.get("workflows", [])
        self._refresh_wf_ui()
        
        ctk.CTkButton(f, text="DEPLOY WORKFLOWS", command=self.save_workflows, width=200).pack(side="bottom", pady=20, anchor="e")

    def _init_privacy_view(self):
        f = ctk.CTkFrame(self.view, fg_color="transparent")
        self.frames["Privacy"] = f
        
        ctk.CTkLabel(f, text="Stealth & Privacy", font=("Outfit", 32, "bold")).pack(pady=(0, 30), anchor="w")
        
        card = self._card_section(f, "SYSTEM AUTONOMY")
        self.auto_start_var = ctk.BooleanVar(value=self.config.get("auto_start", False))
        ctk.CTkSwitch(card, text="Launch on Windows Startup (Invisible Mode)", variable=self.auto_start_var, progress_color=ACCENT_COLOR).pack(pady=10, padx=20, anchor="w")
        ctk.CTkLabel(card, text="Note: Enabling this will start the bridge in Stealth Mode automatically.", font=("Inter", 10), text_color="gray").pack(padx=60, anchor="w")

        safe_card = self._card_section(f, "SECURE KILL SWITCH")
        self.kill_hk_entry = HotkeyRecorder(safe_card, width=200)
        self.kill_hk_entry.configure(state="normal")
        self.kill_hk_entry.insert(0, self.config.get("kill_switch", "ctrl+alt+k"))
        self.kill_hk_entry.configure(state="readonly")
        self.kill_hk_entry.pack(side="left", padx=10)
        
        ctk.CTkButton(safe_card, text="RECORD NEW PANIC KEY", command=self.kill_hk_entry.start_recording).pack(side="left", padx=10)

        ctk.CTkButton(f, text="APPLY PRIVACY ARMOR", command=self.save_notifications, width=220).pack(side="bottom", pady=20, anchor="e")

    def _update_startup_registry(self, enabled):
        reg_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        app_name = "NinjaBridgeStealth"
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_SET_VALUE) as key:
                if enabled:
                    exe_path = os.path.abspath(sys.executable)
                    if exe_path.lower().endswith(".exe"):
                        # Running as a compiled EXE
                        cmd = f'"{exe_path}" --stealth'
                    else:
                        # Running as a script
                        script_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "main.py"))
                        pythonw = os.path.join(os.path.dirname(sys.executable), "pythonw.exe")
                        if not os.path.exists(pythonw): pythonw = sys.executable
                        cmd = f'"{pythonw}" "{script_path}" --stealth'
                    
                    winreg.SetValueEx(key, app_name, 0, winreg.REG_SZ, cmd)
                else:
                    try:
                        winreg.DeleteValue(key, app_name)
                    except FileNotFoundError:
                        pass
            return True
        except Exception as e:
            self.update_log(f"Startup registry error: {e}")
            return False

    def _init_console_view(self):
        f = ctk.CTkFrame(self.view, fg_color="transparent")
        self.frames["Console"] = f
        ctk.CTkLabel(f, text="Engine Logs", font=("Outfit", 32, "bold")).pack(pady=(0, 20), anchor="w")
        self.log_box = ctk.CTkTextbox(f, height=500, font=("Consolas", 12), fg_color="#0D1117", text_color="#A5D6FF", border_color="#30363D", border_width=1)
        self.log_box.pack(fill="both", expand=True)
        self.log_box.configure(state="disabled")

    def _refresh_wf_ui(self):
        for child in self.wf_list.winfo_children(): child.destroy()
        for i, wf in enumerate(self.workflows):
            row = ctk.CTkFrame(self.wf_list, fg_color=CARD_COLOR, border_width=1, border_color="#30363D")
            row.pack(fill="x", pady=4)
            ctk.CTkLabel(row, text=wf['hotkey'].upper(), font=("Inter", 12, "bold"), text_color=ACCENT_COLOR, width=100).pack(side="left", padx=15)
            ctk.CTkLabel(row, text=wf['prompt'][:80] + "...", font=("Inter", 11), text_color=SUBTEXT_COLOR).pack(side="left", expand=True, fill="x")
            ctk.CTkButton(row, text="×", width=30, height=30, fg_color="transparent", hover_color="#F85149", command=lambda idx=i: self._remove_wf(idx)).pack(side="right", padx=10)

    def _remove_wf(self, idx):
        del self.workflows[idx]; self._refresh_wf_ui()

    def update_log(self, text):
        def _exec():
            if hasattr(self, "log_box"):
                self.log_box.configure(state="normal")
                self.log_box.insert("end", f"▸ {text}\n")
                self.log_box.see("end")
                self.log_box.configure(state="disabled")
        self.after(0, _exec)

    def save_general(self):
        self.config.update({
            "ai_provider": self.ai_prov.get(), "ai_api_key": self.ai_key.get(), "ai_model": self.ai_model.get(),
            "ai_base_url": self.ai_url.get(),
            "bridge_provider": self.br_prov.get(), "telegram_bot_token": self.br_token.get(),
            "telegram_chat_id": self.br_id.get(), "kill_switch": self.kill_hk_entry.get() or "ctrl+alt+k"
        })
        save_config(self.config); self.update_log("System configuration synchronized.")

    def save_workflows(self):
        self.config["workflows"] = self.workflows
        save_config(self.config); self.update_log("Workflows deployed to engine.")

    def save_notifications(self):
        self.config["kill_switch"] = self.kill_hk_entry.get() or "ctrl+alt+k"
        self.config["auto_start"] = self.auto_start_var.get()
        
        # Registry update
        self._update_startup_registry(self.config["auto_start"])
        
        save_config(self.config); self.update_log("Privacy armor applied.")

    def toggle_engine(self):
        if not self.engine_active:
            self.engine.start(callback=self.update_log)
            self.engine_btn.configure(text="DEACTIVATE", fg_color="#F1C40F", text_color="black")
            self.engine_active = True
        else:
            self.engine.stop()
            self.engine_btn.configure(text="INITIATE ENGINE", fg_color="#30363D", text_color="white")
            self.engine_active = False

    def go_stealth(self):
        if not self.engine_active: self.toggle_engine()
        self.withdraw()

if __name__ == "__main__":
    app = SetupApp()
    app.mainloop()
