#!/usr/bin/env python3
"""
New_Customer_Login.py
Mobile Automation for Customer Login with OTP Capture
Complete workflow: Launch App → Login → OTP Detection → Wait
"""

import subprocess
import time
import os
import re
import json
from datetime import datetime
import sys

# Colors for output
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    CYAN = '\033[0;36m'
    MAGENTA = '\033[0;35m'
    GRAY = '\033[0;90m'
    NC = '\033[0m'  # No Color

def print_status(message):
    print(f"{Colors.GREEN}[INFO]{Colors.NC} {message}")

def print_warning(message):
    print(f"{Colors.YELLOW}[WARNING]{Colors.NC} {message}")

def print_error(message):
    print(f"{Colors.RED}[ERROR]{Colors.NC} {message}")

def print_header(message):
    print(f"{Colors.BLUE}[HEADER]{Colors.NC} {message}")

def print_success(message):
    print(f"{Colors.GREEN}[SUCCESS]{Colors.NC} {message}")

def print_fail(message):
    print(f"{Colors.RED}[FAIL]{Colors.NC} {message}")

# ============================================================================
# OTP CAPTURE FUNCTIONS
# ============================================================================

def setup_android_environment():
    """Setup Android environment"""
    android_home = "/home/ansh/Android/Sdk"
    os.environ['ANDROID_HOME'] = android_home
    os.environ['PATH'] = f"{android_home}/platform-tools:{android_home}/emulator:{os.environ.get('PATH', '')}"

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

def launch_loyalty_app():
    """Launch LoyaltyXpert app"""
    print("🚀 Launching LoyaltyXpert app...")
    try:
        # Force stop first
        subprocess.run(['adb', 'shell', 'am', 'force-stop', 'ecosmob.loyaltyxpert.com'], check=True)
        time.sleep(2)
        
        # Launch app
        subprocess.run(['adb', 'shell', 'am', 'start', '-n', 'ecosmob.loyaltyxpert.com/.MainActivity'], check=True)
        time.sleep(20)  # Wait 20 seconds for app to fully load
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
    """Enter phone number"""
    phone_number = "1112223334"
    print(f"📞 Entering phone number: {phone_number}")
    
    # Click phone number field
    if click_at_position(331, 1672, "Phone number field"):
        clear_input_field()
        time.sleep(2)
        
        # Enter phone number
        subprocess.run(['adb', 'shell', 'input', 'text', phone_number])
        time.sleep(2)
        print("✅ Phone number entered!")
        return True
    return False

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
    target_x, target_y = 157, 1851  # OTP input field coordinates
    
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

# ============================================================================
# MOBILE AUTOMATION FUNCTIONS
# ============================================================================

def run_mobile_automation():
    """Run mobile automation with OTP capture"""
    print_header("Starting Mobile Automation with OTP Capture")
    
    # Step 1: Launch app
    print_status("Step 1: Launching LoyaltyXpert app...")
    if not launch_loyalty_app():
        print_error("App launch failed")
        return False
    
    time.sleep(3)
    
    # Step 2: Enter phone number
    print_status("Step 2: Entering phone number...")
    if not enter_phone_number():
        print_error("Phone number input failed")
        return False
    
    time.sleep(2)
    
    # Step 3: Click login button
    print_status("Step 3: Clicking login button...")
    if not click_at_position(530, 1282, "Login button"):
        print_error("Login button click failed")
        return False
    
    time.sleep(3)
    
    # Step 4: Extract and fill OTP
    print_status("Step 4: Extracting and filling OTP...")
    if not extract_and_fill_otp():
        print_error("OTP extraction and filling failed")
        return False
    
    # Step 5: Wait 5 seconds after OTP submission (removed three-line click)
    print_status("Step 5: Waiting 5 seconds after OTP submission...")
    time.sleep(5)
    print_success("Waited 5 seconds after OTP submission")
    
    print_success("Mobile automation with OTP capture completed")
    return True

# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main function"""
    print_header("CUSTOMER LOGIN MOBILE AUTOMATION WITH OTP CAPTURE")
    print("=" * 80)
    print("Complete workflow:")
    print("1. Mobile Automation: Launch App → Login → OTP Capture → Wait")
    print("=" * 80)
    
    # Setup environment
    setup_android_environment()
    
    # Check device connection
    if not check_device():
        print_error("Cannot proceed without connected device")
        return
    
    # Create logs directory
    os.makedirs('customer_login_logs', exist_ok=True)
    
    # Log the attempt
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"customer_login_logs/customer_login_attempt_{timestamp}.log"
    
    print(f"📝 Logging to: {log_file}")
    
    # Run Mobile Automation with OTP
    print_header("PHASE 1: MOBILE AUTOMATION WITH OTP CAPTURE")
    mobile_success = run_mobile_automation()
    
    if mobile_success:
        print_success("Mobile automation with OTP capture completed successfully!")
    else:
        print_error("Mobile automation failed")
    
    # Final summary
    print_header("FINAL SUMMARY")
    print("=" * 80)
    if mobile_success:
        print_success("🎉 Customer Login mobile automation completed successfully!")
        print("✅ Mobile Automation: COMPLETED")
        print("✅ App Launch: COMPLETED")
        print("✅ Phone Number Input: COMPLETED")
        print("✅ Login Button: COMPLETED")
        print("✅ OTP Capture: COMPLETED")
        print("✅ Post-Login Wait: COMPLETED")
    else:
        print_error("❌ Customer Login mobile automation failed")
    
    print("=" * 80)

if __name__ == "__main__":
    # Run the main function
    main()
