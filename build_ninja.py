# Build script for Ninja Stealth Bridge
import os
import subprocess
import sys

# Requirements: pip install pyinstaller pillow

def build():
    print("🚀 Starting Ninja Stealth Build...")
    
    # 1. Paths
    current_dir = os.path.dirname(os.path.abspath(__file__))
    main_script = os.path.join(current_dir, "main.py")
    icon_path = os.path.join(current_dir, "icon.ico")
    output_name = "NinjaBridge"
    
    # Check for icon conversion (if only PNG exists)
    png_icon = "icon.png" 
    # I'll use pillow to convert it if possible
    try:
        from PIL import Image
        img = Image.open(os.path.join(current_dir, png_icon))
        img.save(icon_path, format='ICO', sizes=[(256, 256), (128, 128), (64, 64), (32, 32)])
        print("✅ Icon converted to ICO.")
    except Exception as e:
        print(f"⚠️ Icon conversion failed: {e}. Building without custom icon.")
        icon_path = None

    # 2. PyInstaller Command
    # --onefile: single exe
    # --noconsole: no popup window
    # --uac-admin: not needed for HKCU but could be useful? No, better without it for stealth.
    
    cmd = [
        "pyinstaller",
        "--noconsole",
        "--onefile",
        f"--name={output_name}",
        "--clean",
        "--collect-all", "customtkinter"
    ]
    
    if icon_path and os.path.exists(icon_path):
        cmd.append(f"--icon={icon_path}")
        
    cmd.append(main_script)
    
    print(f"📦 Running: {' '.join(cmd)}")
    subprocess.check_call(cmd)
    
    print(f"\n✨ BUILD SUCCESSFUL!")
    print(f"📍 Your professional software is in: {os.path.join(current_dir, 'dist', output_name + '.exe')}")
    print("💡 You can now move this EXE anywhere and it will work independently.")

if __name__ == "__main__":
    build()
