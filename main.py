import sys
from setup_ui import SetupApp

def main():
    """
    Main entry point for the Ninja Bridge.
    Initially launches the setup UI.
    """
    app = SetupApp()
    
    # Auto-stealth check (Startup mode)
    if "--stealth" in sys.argv:
        app.go_stealth()
        # Confirmation toast for startup
        app.engine.show_toast("NINJA BRIDGE", "System Initialized in Background. Stealth Active.")
        
        # Confirmation to Bridge
        app.engine.send_bridge_msg("NINJA BRIDGE: System Online & Stealth Active (Boot Confirmation)")
        
    app.mainloop()

if __name__ == "__main__":
    main()
