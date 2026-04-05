import mss
import mss.tools
from PIL import Image
import os

def capture_screen(monitor_index=1, output_path="screenshot.png"):
    """
    Captures the specified monitor and saves it to a file.
    monitor_index: 1 is the primary monitor, 0 is all monitors.
    """
    with mss.mss() as sct:
        # Get information of monitor 1-n
        if monitor_index > len(sct.monitors) - 1:
            monitor_index = 1
        
        monitor = sct.monitors[monitor_index]
        
        # Capture the screen
        sct_img = sct.grab(monitor)
        
        # Save to the file
        mss.tools.to_png(sct_img.rgb, sct_img.size, output=output_path)
        
    return output_path

if __name__ == "__main__":
    # Test capture
    path = capture_screen()
    print(f"Screenshot saved to {path}")
    # Open image to verify (optional)
    # Image.open(path).show()
