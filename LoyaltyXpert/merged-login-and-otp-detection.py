#!/usr/bin/env python3
"""
Merged Login and OTP Detection Script
Complete workflow: Login -> Phone Number -> X Button -> Login Button -> OTP Detection -> OTP Submission
"""
import subprocess
import time
import os
import re
import json
from datetime import datetime

def setup_environment():
    """Setup Android environment"""
    android_home = r"C:\Users\anshk\AppData\Local\Android\Sdk"
    os.environ['ANDROID_HOME'] = android_home
    os.environ['PATH'] = f"{android_home}\\platform-tools;{android_home}\\emulator;{os.environ.get('PATH', '')}"

def check_device():
    """Check if device is connected"""
    try:
        result = subprocess.run(['adb', 'devices'], capture_output=True, text=True)
        devices = result.stdout.strip().split('\n')[1:]
        connected_devices = [d for d in devices if d.strip() and 'device' in d]
        
        if connected_devices:
            print(f"✅ Device connected: {connected_devices[0]}")
            return True
        else:
            print("❌ No device connected")
            return False
    except Exception as e:
        print(f"❌ Error checking device: {e}")
        return False

def launch_app():
    """Launch LoyaltyXpert app"""
    print("🚀 Launching LoyaltyXpert app...")
    try:
        # Force stop first
        subprocess.run(['adb', 'shell', 'am', 'force-stop', 'ecosmob.loyaltyxpert.com'], check=True)
        time.sleep(2)
        
        # Launch app
        subprocess.run(['adb', 'shell', 'am', 'start', '-n', 'ecosmob.loyaltyxpert.com/.MainActivity'], check=True)
        print("⏳ Waiting 20 seconds for app to fully load...")
        time.sleep(20)
        print("✅ App launched successfully!")
        return True
    except Exception as e:
        print(f"❌ Error launching app: {e}")
        return False

def click_at_position(x, y, description=""):
    """Click at specific coordinates"""
    try:
        print(f"📱 Clicking at position ({x}, {y}): {description}")
        subprocess.run(['adb', 'shell', 'input', 'tap', str(x), str(y)], check=True)
        time.sleep(1)
        print(f"✅ Click executed at ({x}, {y})")
        return True
    except Exception as e:
        print(f"❌ Error clicking at ({x}, {y}): {e}")
        return False

def clear_input_field():
    """Clear input field"""
    print("🧹 Clearing input field...")
    try:
        subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_CTRL_A'], check=True)
        time.sleep(0.5)
        subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_DEL'], check=True)
        time.sleep(1)
        print("✅ Input field cleared")
        return True
    except Exception as e:
        print(f"❌ Error clearing input field: {e}")
        return False

def enter_phone_number():
    """Enter phone number with multiple attempts"""
    phone_number = "8528528521"
    input_positions = [
        (118, 1732),  # Original position
        (300, 800),   # Alternative position
        (400, 800),   # Another alternative
        (200, 800),   # Left side
        (500, 800),   # Right side
    ]
    
    print(f"📞 Entering phone number: {phone_number}")
    
    # Try multiple input field positions
    for x, y in input_positions:
        print(f"🔍 Trying input field at ({x}, {y})...")
        if click_at_position(x, y, f"Phone input field at ({x}, {y})"):
            break
        time.sleep(1)
    
    # Clear and enter phone number
    clear_input_field()
    time.sleep(2)
    
    print(f"📞 Entering phone number: {phone_number}")
    subprocess.run(['adb', 'shell', 'input', 'text', phone_number])
    time.sleep(2)
    
    print("✅ Phone number entered!")
    return True

def press_enter_key():
    """Press Enter key to submit the phone number"""
    print("↵ Pressing Enter key...")
    try:
        subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_ENTER'], check=True)
        time.sleep(2)
        print("✅ Enter key pressed successfully!")
        return True
    except Exception as e:
        print(f"❌ Error pressing Enter key: {e}")
        return False

def add_number_at_coordinates(x, y, number="8528528521"):
    """Add number at specific coordinates using ADB"""
    try:
        print(f"📞 Adding number {number} at coordinates ({x}, {y})...")
        
        # Click at the specified position
        print(f"📱 Clicking at position ({x}, {y})...")
        subprocess.run(['adb', 'shell', 'input', 'tap', str(x), str(y)], check=True)
        time.sleep(1)
        
        # Clear any existing text
        print("🧹 Clearing input field...")
        subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_CTRL_A'], check=True)
        time.sleep(0.5)
        subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_DEL'], check=True)
        time.sleep(1)
        
        # Enter the number
        print(f"📞 Entering number: {number}")
        subprocess.run(['adb', 'shell', 'input', 'text', number], check=True)
        time.sleep(2)
        
        print(f"✅ Number {number} added successfully at ({x}, {y})!")
        return True
        
    except Exception as e:
        print(f"❌ Error adding number at ({x}, {y}): {e}")
        return False

def take_screenshot(filename="otp_screenshot.png"):
    """Take screenshot and save it"""
    try:
        print(f"📸 Taking screenshot: {filename}")
        subprocess.run(['adb', 'shell', 'screencap', '/sdcard/screenshot.png'], check=True)
        subprocess.run(['adb', 'pull', '/sdcard/screenshot.png', filename], check=True)
        print(f"✅ Screenshot saved as {filename}")
        return filename
    except Exception as e:
        print(f"❌ Error taking screenshot: {e}")
        return None

def get_ui_dump():
    """Get UI dump using uiautomator"""
    try:
        print("🔍 Getting UI dump...")
        result = subprocess.run(['adb', 'shell', 'uiautomator', 'dump'], capture_output=True, text=True)
        if result.returncode == 0:
            # Pull the UI dump file
            subprocess.run(['adb', 'pull', '/sdcard/window_dump.xml', 'ui_dump.xml'], check=True)
            print("✅ UI dump saved as ui_dump.xml")
            
            # Read and parse the UI dump
            with open('ui_dump.xml', 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Extract text from UI dump
            text_elements = re.findall(r'text="([^"]*)"', content)
            desc_elements = re.findall(r'content-desc="([^"]*)"', content)
            
            all_text = text_elements + desc_elements
            combined_text = '\n'.join([text for text in all_text if text.strip()])
            
            print(f"📝 Extracted {len(all_text)} text elements from UI dump")
            return combined_text
        else:
            print("❌ Failed to get UI dump")
            return None
    except Exception as e:
        print(f"❌ Error getting UI dump: {e}")
        return None

def get_accessibility_dump():
    """Get accessibility dump"""
    try:
        print("🔍 Getting accessibility dump...")
        result = subprocess.run(['adb', 'shell', 'dumpsys', 'accessibility'], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Save accessibility dump
            with open('accessibility_dump.txt', 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            print("✅ Accessibility dump saved as accessibility_dump.txt")
            
            # Extract text from accessibility dump
            lines = result.stdout.split('\n')
            all_text = []
            
            for line in lines:
                if 'text=' in line or 'content-desc=' in line:
                    text_match = re.search(r'text="([^"]*)"', line)
                    if text_match:
                        text = text_match.group(1).strip()
                        if text:
                            all_text.append(text)
                    
                    desc_match = re.search(r'content-desc="([^"]*)"', line)
                    if desc_match:
                        desc = desc_match.group(1).strip()
                        if desc:
                            all_text.append(desc)
            
            combined_text = '\n'.join(all_text)
            print(f"📝 Extracted {len(all_text)} text elements from accessibility dump")
            return combined_text
        else:
            print("❌ Failed to get accessibility dump")
            return None
    except Exception as e:
        print(f"❌ Error getting accessibility dump: {e}")
        return None

def get_window_dump():
    """Get window dump"""
    try:
        print("🔍 Getting window dump...")
        result = subprocess.run(['adb', 'shell', 'dumpsys', 'window', 'windows'], capture_output=True, text=True)
        
        if result.returncode == 0:
            # Save window dump
            with open('window_dump.txt', 'w', encoding='utf-8') as f:
                f.write(result.stdout)
            print("✅ Window dump saved as window_dump.txt")
            
            # Extract text from window dump
            lines = result.stdout.split('\n')
            all_text = []
            
            for line in lines:
                if 'text=' in line or 'title=' in line:
                    text_match = re.search(r'text="([^"]*)"', line)
                    if text_match:
                        text = text_match.group(1).strip()
                        if text:
                            all_text.append(text)
                    
                    title_match = re.search(r'title="([^"]*)"', line)
                    if title_match:
                        title = title_match.group(1).strip()
                        if title:
                            all_text.append(title)
            
            combined_text = '\n'.join(all_text)
            print(f"📝 Extracted {len(all_text)} text elements from window dump")
            return combined_text
        else:
            print("❌ Failed to get window dump")
            return None
    except Exception as e:
        print(f"❌ Error getting window dump: {e}")
        return None

def find_otp_in_text(text, method_name=""):
    """Find OTP in text using comprehensive regex patterns"""
    if not text:
        print(f"❌ No text to search in {method_name}")
        return None
    
    print(f"🔍 Searching for OTP in {method_name}...")
    
    # Print first 200 characters for debugging
    preview = text[:200].replace('\n', ' ').strip()
    print(f"📝 Text preview: {preview}...")
    
    # Comprehensive OTP patterns (in order of preference)
    otp_patterns = [
        # Specific OTP patterns
        r'OTP[:\s]*(\d{4,6})',                    # OTP: 123456
        r'verification[:\s]*(\d{4,6})',           # verification: 123456
        r'code[:\s]*(\d{4,6})',                   # code: 123456
        r'pin[:\s]*(\d{4,6})',                    # pin: 123456
        r'password[:\s]*(\d{4,6})',               # password: 123456
        
        # Common phrases with OTP
        r'please submit this\s*(\d{4,6})',        # please submit this 123456
        r'enter\s*(\d{4,6})',                     # enter 123456
        r'use\s*(\d{4,6})',                       # use 123456
        r'type\s*(\d{4,6})',                      # type 123456
        
        # Generic number patterns
        r'\b(\d{4})\b',                           # 4-digit numbers
        r'\b(\d{5})\b',                           # 5-digit numbers
        r'\b(\d{6})\b',                           # 6-digit numbers
        
        # Fallback patterns
        r'(\d{4,6})',                             # Any 4-6 digit number
    ]
    
    found_otps = []
    
    for i, pattern in enumerate(otp_patterns):
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            # Extract the actual number from the match
            if isinstance(match, tuple):
                otp = match[0]
            else:
                otp = match
            
            # Validate it's a proper OTP
            if otp.isdigit() and len(otp) >= 4 and len(otp) <= 6:
                # Additional validation: check if it's not a common non-OTP number
                if not is_common_non_otp_number(otp):
                    found_otps.append(otp)
                    print(f"✅ Found potential OTP: {otp} (pattern {i+1})")
    
    if found_otps:
        # Prioritize 4-digit OTPs, then 6-digit, then others
        for otp in found_otps:
            if len(otp) == 4:
                print(f"🎯 Selected 4-digit OTP: {otp}")
                return otp
        
        for otp in found_otps:
            if len(otp) == 6:
                print(f"🎯 Selected 6-digit OTP: {otp}")
                return otp
        
        print(f"🎯 Selected OTP: {found_otps[0]}")
        return found_otps[0]
    
    print(f"❌ No OTP found in {method_name}")
    return None

def is_common_non_otp_number(number):
    """Check if a number is likely not an OTP (common patterns)"""
    common_non_otp = [
        '0000', '1111', '2222', '3333', '4444', '5555', '6666', '7777', '8888', '9999',
        '1234', '4321', '0001', '1000', '9999', '8888', '7777', '6666', '5555', '4444',
        '000000', '111111', '123456', '654321', '000001', '100000', '999999'
    ]
    return number in common_non_otp

def input_text_at_coordinates(text, x, y, description=""):
    """Input text at specific coordinates"""
    try:
        print(f"📝 Inputting text '{text}' at ({x}, {y}): {description}")
        
        # Click at the position
        if not click_at_position(x, y, description):
            return False
        
        # Clear any existing text
        clear_input_field()
        
        # Input the text
        subprocess.run(['adb', 'shell', 'input', 'text', text], check=True)
        time.sleep(2)
        
        print(f"✅ Text '{text}' input successfully at ({x}, {y})")
        return True
    except Exception as e:
        print(f"❌ Error inputting text at ({x}, {y}): {e}")
        return False

def try_common_otp_positions():
    """Try clicking at common OTP positions to trigger text extraction"""
    print("🔍 Trying common OTP positions...")
    
    common_positions = [
        (412, 1708),  # Specific OTP position
        (476, 1753),  # Another common position
        (451, 1761),  # X button position
        (149, 1902),  # OTP input field
        (139, 1899),  # Another input field
        (163, 1868),  # Another position
    ]
    
    for x, y in common_positions:
        print(f"🔍 Trying position ({x}, {y})...")
        if click_at_position(x, y, f"OTP position ({x}, {y})"):
            time.sleep(2)
            
            # Try to get text after clicking
            ui_text = get_ui_dump()
            if ui_text:
                otp = find_otp_in_text(ui_text, f"UI dump after clicking ({x}, {y})")
                if otp:
                    return otp
    
    print("❌ No OTP found in common positions")
    return None

def monitor_for_otp(max_attempts=10, delay=3):
    """Monitor for OTP arrival with multiple attempts"""
    print(f"🔍 Monitoring for OTP (max {max_attempts} attempts, {delay}s delay)...")
    
    for attempt in range(1, max_attempts + 1):
        print(f"\n🔄 Attempt {attempt}/{max_attempts}")
        print("=" * 40)
        
        # Method 1: UI Dump
        ui_text = get_ui_dump()
        if ui_text:
            otp = find_otp_in_text(ui_text, "UI Dump")
            if otp:
                return otp
        
        # Method 2: Accessibility Dump
        acc_text = get_accessibility_dump()
        if acc_text:
            otp = find_otp_in_text(acc_text, "Accessibility Dump")
            if otp:
                return otp
        
        # Method 3: Window Dump
        win_text = get_window_dump()
        if win_text:
            otp = find_otp_in_text(win_text, "Window Dump")
            if otp:
                return otp
        
        # Method 4: Try common positions
        otp = try_common_otp_positions()
        if otp:
            return otp
        
        # Method 5: Take screenshot and save for manual review
        if attempt == max_attempts:
            screenshot = take_screenshot(f"otp_attempt_{attempt}.png")
            print(f"📸 Final screenshot saved as {screenshot} for manual review")
        
        if attempt < max_attempts:
            print(f"⏳ Waiting {delay} seconds before next attempt...")
            time.sleep(delay)
    
    print("❌ OTP not found after all attempts")
    return None

def extract_and_fill_otp():
    """Extract OTP and fill it in input field"""
    print("\n🎯 OTP EXTRACTION AND FILLING PROCESS")
    print("=" * 60)
    
    # Step 1: Monitor for OTP arrival
    print("\n🔍 STEP 1: Monitoring for OTP arrival...")
    otp = monitor_for_otp(max_attempts=15, delay=2)
    
    if not otp:
        print("❌ No OTP found after monitoring")
        return False
    
    # Step 2: Fill OTP in input field
    print(f"\n📝 STEP 2: Filling OTP '{otp}' in input field...")
    target_x, target_y = 149, 1902  # OTP input field coordinates
    
    if input_text_at_coordinates(otp, target_x, target_y, "OTP input field"):
        print(f"✅ OTP '{otp}' successfully filled in input field!")
        
        # Step 3: Press Enter to submit
        print("\n↵ STEP 3: Pressing Enter to submit OTP...")
        try:
            subprocess.run(['adb', 'shell', 'input', 'keyevent', 'KEYCODE_ENTER'], check=True)
            time.sleep(2)
            print("✅ Enter key pressed successfully!")
        except Exception as e:
            print(f"❌ Error pressing Enter: {e}")
        
        return True
    else:
        print(f"❌ Failed to fill OTP '{otp}' in input field")
        return False

def complete_login_workflow():
    """Complete login workflow with OTP detection"""
    print("🎯 COMPLETE LOGIN AND OTP WORKFLOW")
    print("=" * 60)
    
    # Step 1: Launch app
    print("\n📱 STEP 1: Launching app...")
    if not launch_app():
        print("❌ App launch failed")
        return False
    
    time.sleep(3)  # Wait for app to load
    
    # Step 2: Enter phone number
    print("\n📞 STEP 2: Entering phone number...")
    if not enter_phone_number():
        print("❌ Phone number input failed")
        return False
    
    time.sleep(2)
    
    # Step 3: Press Enter key
    print("\n↵ STEP 3: Pressing Enter key...")
    if not press_enter_key():
        print("❌ Enter key press failed")
        return False
    
    time.sleep(2)
    
    # Step 4: Add number at coordinates (528, 1652)
    print("\n📞 STEP 4: Adding number at coordinates (528, 1652)...")
    if not add_number_at_coordinates(528, 1652, "8528528521"):
        print("⚠️ Number input failed, continuing with workflow...")
    
    time.sleep(2)
    
    # Step 5: Click X button at specific coordinates
    print(f"\n❌ STEP 5: Clicking X button at (489, 1916)...")
    if not click_at_position(489, 1916, "X button at user coordinates"):
        print("❌ X button click failed")
        return False
    
    time.sleep(2)
    
    # Step 6: Click login button at specific coordinates
    print(f"\n🔘 STEP 6: Clicking login button at (563, 1270)...")
    if not click_at_position(563, 1270, "Login button at user coordinates"):
        print("❌ Login button click failed")
        return False
    
    time.sleep(5)  # Wait longer for login to process
    
    # Step 7: Extract and fill OTP
    print("\n🔍 STEP 7: Extracting and filling OTP...")
    if not extract_and_fill_otp():
        print("❌ OTP extraction and filling failed")
        return False
    
    print("✅ Complete login and OTP workflow finished successfully!")
    return True

def main():
    """Main function"""
    print("🎯 MERGED LOGIN AND OTP DETECTION SCRIPT")
    print("=" * 60)
    print("Complete workflow:")
    print("1. Launch LoyaltyXpert app")
    print("2. Enter phone number (8528528521)")
    print("3. Press Enter key")
    print("4. Add number at (528, 1652)")
    print("5. Click X button at (489, 1916)")
    print("6. Click login button at (563, 1270)")
    print("7. Extract OTP using multiple methods")
    print("8. Fill OTP and submit")
    print("=" * 60)
    
    setup_environment()
    
    if not check_device():
        print("❌ Cannot proceed without connected device")
        return
    
    # Create logs directory
    os.makedirs('merged_logs', exist_ok=True)
    
    # Log the attempt
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"merged_logs/merged_attempt_{timestamp}.log"
    
    print(f"📝 Logging to: {log_file}")
    
    success = complete_login_workflow()
    
    print("\n" + "=" * 60)
    if success:
        print("✅ Complete login and OTP workflow finished successfully!")
        print("🎉 All steps completed: Login → OTP Detection → OTP Submission")
    else:
        print("❌ Workflow encountered issues")
        print("📝 Check the log files and screenshots for debugging")
    
    print("=" * 60)

if __name__ == "__main__":
    main()
