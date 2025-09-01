#!/usr/bin/env python3
"""
LoyaltyAnnouncementOTP.py
Combined Web Automation + Mobile Automation + OTP Capture
Complete workflow: Web Login → Mobile Login → OTP Detection → Mobile Navigation
"""

import subprocess
import time
import os
import re
import json
import asyncio
from datetime import datetime
from playwright.async_api import async_playwright
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
# OTP CAPTURE FUNCTIONS (from OTP_Capture.py)
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
    phone_number = "8528528521"
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
# WEB AUTOMATION FUNCTIONS (converted from LoyaltyAnnouncement.sh)
# ============================================================================

async def run_web_automation():
    """Run web automation using Playwright"""
    print_header("Starting Web Automation")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False, slow_mo=300)
        context = await browser.new_context()
        page = await context.new_page()
        
        try:
            # Navigate to login page
            print_status("Navigating to login page...")
            await page.goto('http://digisol.loyaltyxpert.staging/auth/auth/login', 
                           wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_load_state('domcontentloaded')
            print_success("Login page loaded")
            
            # Login process
            print_status("Starting login process...")
            
            # Find and fill username field
            username_selectors = [
                'input[name="username"]', 'input[name="email"]', 'input[type="email"]',
                'input[type="text"]', '#username', '#email', '.username', '.email',
                'input[placeholder*="username" i]', 'input[placeholder*="email" i]'
            ]
            
            username_field = None
            for selector in username_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    username_field = await page.query_selector(selector)
                    if username_field:
                        break
                except:
                    continue
            
            if not username_field:
                print_error("Username field not found")
                return False
            
            await username_field.click()
            await username_field.fill('ishita.popat@ecosmob.com')
            print_success("Username entered")
            
            # Find and fill password field
            password_selectors = [
                'input[name="password"]', 'input[type="password"]', '#password',
                '.password', 'input[placeholder*="password" i]'
            ]
            
            password_field = None
            for selector in password_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    password_field = await page.query_selector(selector)
                    if password_field:
                        break
                except:
                    continue
            
            if not password_field:
                print_error("Password field not found")
                return False
            
            await password_field.click()
            await password_field.fill('Test@123')
            print_success("Password entered")
            
            # Find and click login button
            login_selectors = [
                'button[type="submit"]', 'input[type="submit"]', '.login-btn',
                '#login', 'button:has-text("Login")', 'button:has-text("Sign In")'
            ]
            
            login_button = None
            for selector in login_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    login_button = await page.query_selector(selector)
                    if login_button:
                        break
                except:
                    continue
            
            if not login_button:
                print_error("Login button not found")
                return False
            
            await login_button.click()
            print_success("Login button clicked")
            
            # Wait after login
            await page.wait_for_timeout(5000)
            await page.wait_for_load_state('networkidle', timeout=60000)
            print_success("Post-login page loaded")
            
            # Find and click search box from left navigation
            print_status("Looking for search box...")
            search_box_selectors = [
                'input[placeholder*="search" i]', 'input[type="search"]', '.search-box input',
                '.search input', '[data-testid="search"]', 'input[aria-label*="search" i]',
                '.nav input[type="text"]', '.sidebar input[type="text"]', 'input[name="search"]'
            ]
            
            search_box = None
            for selector in search_box_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    search_box = await page.query_selector(selector)
                    if search_box:
                        break
                except:
                    continue
            
            if not search_box:
                print_error("Search box not found")
                return False
            
            await search_box.click()
            print_success("Search box clicked")
            
            # Type "anno" in search box gradually with pauses
            print_status("Typing 'anno' gradually...")
            search_text = 'anno'
            for i in range(len(search_text)):
                await search_box.type(search_text[i])
                await page.wait_for_timeout(200)  # 200ms pause between each character
            
            print_success("Typed 'anno' gradually with pauses")
            
            # Wait a moment for the interface to update after typing
            await page.wait_for_timeout(1000)
            
            # Navigate to announcements
            print_status("Navigating to announcements...")
            await page.goto('http://digisol.loyaltyxpert.staging/announcement/announcement-master', 
                           wait_until='domcontentloaded', timeout=60000)
            await page.wait_for_load_state('networkidle', timeout=60000)
            print_success("Announcement page loaded")
            
            # Click ADD NEW button
            add_new_selectors = [
                'a.btn-primary.btn-sm.text-bold-700.top-margin', 'a:has-text("ADD NEW")',
                'a[href*="create"]', 'a[href*="add"]', 'button:has-text("ADD NEW")'
            ]
            
            add_new_button = None
            for selector in add_new_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    add_new_button = await page.query_selector(selector)
                    if add_new_button:
                        break
                except:
                    continue
            
            if not add_new_button:
                print_error("ADD NEW button not found")
                return False
            
            await add_new_button.click()
            print_success("Clicked ADD NEW button")
            
            # Wait for form to load
            await page.wait_for_load_state('domcontentloaded')
            await page.wait_for_timeout(2000)
            
            # Fill title field
            title_selectors = [
                'input[name="title"]', 'input[placeholder*="title" i]', '#title',
                '.title-input', 'input[type="text"]:first-of-type'
            ]
            
            title_field = None
            for selector in title_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    title_field = await page.query_selector(selector)
                    if title_field:
                        break
                except:
                    continue
            
            if not title_field:
                print_error("Title field not found")
                return False
            
            await title_field.click()
            await title_field.fill('Hello_Automatio')
            print_success("Title filled")
            
            # Select Announcement Type dropdown
            print_status("Selecting Announcement Type dropdown...")
            announcement_dropdown_selectors = [
                'span#select2-announcementmaster-announcement_type_id-container',
                'span[title="Select Type"]:first-of-type', 'span.select2-selection__rendered:first-of-type',
                'select[name="AnnouncementMaster[announcement_type_id]"]', 'select#announcementmaster-announcement_type_id',
                'select.form-control.select2', 'input[placeholder="Select Type"]:first-of-type',
                'div[role="combobox"]:has-text("Select Type"):first-of-type'
            ]
            
            announcement_dropdown = None
            for selector in announcement_dropdown_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    announcement_dropdown = await page.query_selector(selector)
                    if announcement_dropdown:
                        break
                except:
                    continue
            
            if not announcement_dropdown:
                print_error("Announcement Type dropdown not found")
                return False
            
            await announcement_dropdown.click()
            print_success("Clicked Announcement Type dropdown to expand")
            
            # Wait for options to be visible
            await page.wait_for_timeout(1500)
            
            # Select General option
            general_option_selectors = [
                'li.select2-results__option:has-text("General")', 'li:has-text("General")',
                '.select2-results__option:has-text("General")', 'option:has-text("General")',
                'option[value="4"]', '[data-value="General"]', 'div[role="option"]:has-text("General")'
            ]
            
            general_option = None
            for selector in general_option_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    general_option = await page.query_selector(selector)
                    if general_option:
                        break
                except:
                    continue
            
            if not general_option:
                print_error("General option not found")
                return False
            
            await general_option.click()
            print_success("Selected General option")
            await page.wait_for_timeout(1000)
            
            # Select User Type dropdown
            print_status("Selecting User Type dropdown...")
            user_type_dropdown_selectors = [
                'span#select2-announcementmaster-user_type-container',
                'span[title="Select Type"]:nth-of-type(2)', 'span.select2-selection__rendered:nth-of-type(2)',
                'select[name="AnnouncementMaster[user_type]"]', 'select#announcementmaster-user_type',
                'select.form-control.select2:nth-of-type(2)', 'div[role="combobox"]:has-text("User Type")'
            ]
            
            user_type_dropdown = None
            for selector in user_type_dropdown_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    user_type_dropdown = await page.query_selector(selector)
                    if user_type_dropdown:
                        break
                except:
                    continue
            
            if not user_type_dropdown:
                print_error("User Type dropdown not found")
                return False
            
            await user_type_dropdown.click()
            print_success("Clicked User Type dropdown to expand")
            
            # Wait for options to be visible
            await page.wait_for_timeout(1500)
            
            # Select Customer option
            customer_option_selectors = [
                'li.select2-results__option:has-text("Customer")', 'li:has-text("Customer")',
                '.select2-results__option:has-text("Customer")', 'option:has-text("Customer")',
                'option[value="193"]', '[data-value="Customer"]', 'div[role="option"]:has-text("Customer")'
            ]
            
            customer_option = None
            for selector in customer_option_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    customer_option = await page.query_selector(selector)
                    if customer_option:
                        break
                except:
                    continue
            
            if not customer_option:
                print_error("Customer option not found")
                return False
            
            await customer_option.click()
            print_success("Selected Customer option")
            await page.wait_for_timeout(1000)
            
            # Scroll down a little
            print_status("Scrolling down...")
            await page.evaluate("window.scrollBy(0, 300)")
            await page.wait_for_timeout(1000)
            print_success("Scrolled down")
            
            # Fill short description
            short_desc_selectors = [
                'textarea[name="shortDescription"]', 'textarea[name="short_description"]',
                'textarea[name="description"]', 'textarea[placeholder*="short description" i]'
            ]
            
            short_desc_field = None
            for selector in short_desc_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    short_desc_field = await page.query_selector(selector)
                    if short_desc_field:
                        break
                except:
                    continue
            
            if short_desc_field:
                await short_desc_field.click()
                await short_desc_field.fill('Hello For Testing Purpose ')
                print_success("Short description filled")
            
            # Fill content description
            content_desc_selectors = [
                'div.ql-editor[data-placeholder="Description..."]', 'div.ql-editor.ql-blank',
                'textarea[name="content"]', 'textarea[name="contentDescription"]'
            ]
            
            content_desc_field = None
            for selector in content_desc_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    content_desc_field = await page.query_selector(selector)
                    if content_desc_field:
                        break
                except:
                    continue
            
            if content_desc_field:
                await content_desc_field.click()
                await content_desc_field.fill('for demo purpose')
                print_success("Content description filled")
            
            # Click Add button
            add_button_selectors = [
                'button:has-text("Add")', 'button:has-text("Submit")', 'button:has-text("Save")',
                'button[type="submit"]', '.add-btn', '.submit-btn'
            ]
            
            add_button = None
            for selector in add_button_selectors:
                try:
                    await page.wait_for_selector(selector, state='visible', timeout=2000)
                    add_button = await page.query_selector(selector)
                    if add_button:
                        break
                except:
                    continue
            
            if not add_button:
                print_error("Add button not found")
                return False
            
            await add_button.click()
            print_success("Clicked Add button")
            
            # Wait after submission
            await page.wait_for_timeout(6000)
            print_success("Web automation completed")
            
            return True
            
        except Exception as e:
            print_error(f"Web automation error: {e}")
            return False
        finally:
            await browser.close()

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
    
    # Step 5: Wait 15 seconds after OTP submission
    print_status("Step 5: Waiting 15 seconds after OTP submission...")
    time.sleep(15)
    print_success("Waited 15 seconds after OTP submission")
    
    # Step 6: Click three line menu
    print_status("Step 6: Clicking three line menu...")
    if not click_at_position(29, 149, "Three line menu"):
        print_error("Three line menu click failed")
        return False
    
    # Step 7: Wait 5 seconds after three line click
    print_status("Step 7: Waiting 5 seconds after three line click...")
    time.sleep(5)
    print_success("Waited 5 seconds after three line click")
    
    # Step 8: Click announcements
    print_status("Step 8: Clicking announcements...")
    if not click_at_position(230, 1096, "Announcements"):
        print_error("Announcements click failed")
        return False
    
    # Step 9: Wait 6 seconds after announcements click
    print_status("Step 9: Waiting 6 seconds after announcements click...")
    time.sleep(6)
    print_success("Waited 6 seconds after announcements click")
    
    # Step 10: Click top announcements
    print_status("Step 10: Clicking top announcements...")
    if not click_at_position(335, 353, "Top announcements"):
        print_error("Top announcements click failed")
        return False
    
    # Step 11: Wait 5 seconds after top announcements click
    print_status("Step 11: Waiting 5 seconds after top announcements click...")
    time.sleep(5)
    print_success("Waited 5 seconds after top announcements click")
    
    print_success("Mobile automation with OTP capture completed")
    return True

# ============================================================================
# MAIN EXECUTION
# ============================================================================

async def main():
    """Main function"""
    print_header("LOYALTY ANNOUNCEMENT AUTOMATION WITH OTP CAPTURE")
    print("=" * 80)
    print("Complete workflow:")
    print("1. Web Automation: Login → Create Announcement")
    print("2. Mobile Automation: Launch App → Login → OTP Capture → Navigate")
    print("=" * 80)
    
    # Setup environment
    setup_android_environment()
    
    # Check device connection
    if not check_device():
        print_error("Cannot proceed without connected device")
        return
    
    # Create logs directory
    os.makedirs('loyalty_logs', exist_ok=True)
    
    # Log the attempt
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = f"loyalty_logs/loyalty_otp_attempt_{timestamp}.log"
    
    print(f"📝 Logging to: {log_file}")
    
    # Step 1: Web Automation
    print_header("PHASE 1: WEB AUTOMATION")
    web_success = await run_web_automation()
    
    if web_success:
        print_success("Web automation completed successfully!")
    else:
        print_error("Web automation failed")
    
    # Step 2: Mobile Automation with OTP
    print_header("PHASE 2: MOBILE AUTOMATION WITH OTP CAPTURE")
    mobile_success = run_mobile_automation()
    
    if mobile_success:
        print_success("Mobile automation with OTP capture completed successfully!")
    else:
        print_error("Mobile automation failed")
    
    # Final summary
    print_header("FINAL SUMMARY")
    print("=" * 80)
    if web_success and mobile_success:
        print_success("🎉 Complete automation suite finished successfully!")
        print("✅ Web Automation: COMPLETED")
        print("✅ Mobile Automation: COMPLETED")
        print("✅ OTP Capture: COMPLETED")
    else:
        print_error("❌ Some automation phases failed")
        if not web_success:
            print_error("❌ Web automation failed")
        if not mobile_success:
            print_error("❌ Mobile automation failed")
    
    print("=" * 80)

if __name__ == "__main__":
    # Check if required packages are installed
    try:
        import playwright
    except ImportError:
        print_error("Playwright not installed. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "playwright"])
        subprocess.run([sys.executable, "-m", "playwright", "install", "chromium"])
    
    # Run the main function
    asyncio.run(main())
