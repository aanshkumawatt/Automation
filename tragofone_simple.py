#!/usr/bin/env python3

import time
import subprocess
import pyautogui
import cv2
import numpy as np
from PIL import Image

# Simple configuration
pyautogui.FAILSAFE = False
pyautogui.PAUSE = 1

def find_image_on_screen(image_path, confidence=0.8):
    """Find an image on screen using template matching"""
    try:
        # Load the template image
        template = cv2.imread(image_path, cv2.IMREAD_COLOR)
        if template is None:
            print(f"Could not load image: {image_path}")
            return None
            
        # Take screenshot
        screenshot = pyautogui.screenshot()
        screenshot_np = np.array(screenshot)
        screenshot_bgr = cv2.cvtColor(screenshot_np, cv2.COLOR_RGB2BGR)
        
        # Template matching
        result = cv2.matchTemplate(screenshot_bgr, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= confidence:
            # Get center of the matched region
            h, w = template.shape[:2]
            center_x = max_loc[0] + w // 2
            center_y = max_loc[1] + h // 2
            return (center_x, center_y)
        else:
            return None
            
    except Exception as e:
        print(f"Error finding image {image_path}: {e}")
        return None

def find_and_click_by_image(image_path, description, confidence=0.8):
    """Find image on screen and click on it"""
    print(f"Looking for {description}...")
    
    position = find_image_on_screen(image_path, confidence)
    
    if position:
        pyautogui.click(position)
        print(f"Clicked on {description}")
        return True
    else:
        print(f"Could not find {description}")
        return False

def focus_tragofone_window():
    """Focus Tragofone window"""
    print("Focusing Tragofone window...")
    
    try:
        result = subprocess.run(["wmctrl", "-l"], capture_output=True, text=True)
        
        if "Tragofone" in result.stdout:
            subprocess.run(["wmctrl", "-a", "Tragofone"])
            time.sleep(2)
            print("Tragofone window focused")
            return True
        else:
            print("Tragofone window not found")
            return False
            
    except Exception as e:
        print(f"Error focusing window: {e}")
        return False

def take_screenshot_and_save(filename):
    """Take screenshot and save it for reference"""
    try:
        screenshot = pyautogui.screenshot()
        screenshot.save(filename)
        print(f"Screenshot saved as {filename}")
        return True
    except Exception as e:
        print(f"Error taking screenshot: {e}")
        return False

print("🎯 Tragofone Automation (Image-based)")
print("=====================================")

# Kill existing Tragofone
print("Killing existing Tragofone...")
subprocess.run(["pkill", "-f", "tragofone"])
time.sleep(2)

# Start Tragofone
print("Starting Tragofone...")
subprocess.Popen(["tragofone"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
time.sleep(10)

# Focus the window
focus_tragofone_window()

print("Starting automation...")
time.sleep(2)

# Take initial screenshot for reference
take_screenshot_and_save("tragofone_initial.png")

# Try to find and click username field
# You would need to create reference images for these elements
username_found = False
if find_and_click_by_image("username_field.png", "username field"):
    username_found = True
elif find_and_click_by_image("email_field.png", "email field"):
    username_found = True
elif find_and_click_by_image("login_field.png", "login field"):
    username_found = True

if username_found:
    # Clear and type username
    print("Typing username...")
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('delete')
    pyautogui.typewrite("ansh.kumawat@ecosmob.com")
    time.sleep(4)
else:
    print("Could not find username field - using fallback coordinates")
    pyautogui.moveTo(974, 345)
    pyautogui.click()
    time.sleep(1)
    pyautogui.hotkey('ctrl', 'a')
    pyautogui.press('delete')
    pyautogui.typewrite("ansh.kumawat@ecosmob.com")
    time.sleep(4)

# Try to find and click password field
password_found = False
if find_and_click_by_image("password_field.png", "password field"):
    password_found = True
elif find_and_click_by_image("pass_field.png", "password field"):
    password_found = True

if password_found:
    # Type password
    print("Typing password...")
    pyautogui.typewrite("Ansh@123")
    time.sleep(1)
else:
    print("Could not find password field - using fallback coordinates")
    pyautogui.moveTo(1231, 385)
    pyautogui.click()
    time.sleep(1)
    pyautogui.typewrite("Ansh@123")
    time.sleep(1)

# Try to find and click login button
login_found = False
if find_and_click_by_image("login_button.png", "login button"):
    login_found = True
elif find_and_click_by_image("signin_button.png", "sign in button"):
    login_found = True
elif find_and_click_by_image("submit_button.png", "submit button"):
    login_found = True

if login_found:
    print("Login button clicked")
    time.sleep(18)
else:
    print("Could not find login button - using fallback coordinates")
    pyautogui.moveTo(1234, 439)
    pyautogui.click()
    time.sleep(18)

# Take final screenshot
take_screenshot_and_save("tragofone_final.png")

print("Automation completed!")
print("Check the screenshots to see the results!")
