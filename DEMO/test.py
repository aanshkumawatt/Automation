#!/usr/bin/env python3
"""
Auto Logout Finder Script
Automatically finds and clicks the logout element (arrow in circle)
"""

import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options

def setup_chrome_driver():
    """Setup Chrome WebDriver"""
    chrome_options = Options()
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-web-security")
    chrome_options.add_argument("--start-maximized")
    
    try:
        driver = webdriver.Chrome(options=chrome_options)
        return driver
    except Exception as e:
        print(f"Chrome WebDriver failed: {e}")
        return None

def login_and_navigate(driver):
    """Login and navigate to a page where logout would be visible"""
    print("🔐 Logging in...")
    
    try:
        # Navigate to login page
        driver.get("http://172.16.16.224:3000/login")
        time.sleep(3)
        
        # Enter username
        username_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='username']"))
        )
        username_field.clear()
        username_field.send_keys("Ecouser")
        print("✅ Username entered")
        
        # Enter password
        password_field = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "input[name='password']"))
        )
        password_field.clear()
        password_field.send_keys("4142025!ECO")
        print("✅ Password entered")
        
        # Click login button
        login_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Login')]"))
        )
        login_button.click()
        print("✅ Login button clicked")
        
        # Wait for redirect
        time.sleep(5)
        
        if "login" not in driver.current_url.lower():
            print("✅ Login successful!")
            return True
        else:
            print("❌ Login failed")
            return False
            
    except Exception as e:
        print(f"❌ Login error: {e}")
        return False

def find_and_click_logout(driver):
    """Find and click the logout element (arrow in circle)"""
    print("🔍 Looking for logout element (arrow in circle)...")
    
    # Priority selectors for logout elements
    logout_selectors = [
        # Most likely logout selectors
        "//button[contains(@class, 'logout')]",
        "//a[contains(@class, 'logout')]",
        "//*[contains(@class, 'logout')]",
        "//button[contains(text(), 'Logout')]",
        "//a[contains(text(), 'Logout')]",
        
        # Arrow-related selectors
        "//button[contains(@class, 'arrow')]",
        "//svg[contains(@class, 'arrow')]",
        "//button[contains(@class, 'chevron')]",
        "//svg[contains(@class, 'chevron')]",
        
        # Right-positioned elements (common for logout)
        "//*[contains(@class, 'right')]//button",
        "//*[contains(@class, 'end')]//button",
        "//header//button[last()]",
        "//nav//button[last()]",
        
        # Profile/user menu elements
        "//*[contains(@class, 'profile')]//button",
        "//*[contains(@class, 'user')]//button",
        "//*[contains(@class, 'avatar')]//button",
        "//*[contains(@class, 'menu')]//button",
        
        # All buttons in header
        "//header//button",
        "//nav//button",
        
        # Elements with cursor pointer
        "//*[contains(@class, 'cursor-pointer')]"
    ]
    
    for i, selector in enumerate(logout_selectors, 1):
        try:
            print(f"Trying selector {i}: {selector}")
            elements = driver.find_elements(By.XPATH, selector)
            
            for element in elements:
                try:
                    # Get element details
                    tag_name = element.tag_name
                    class_name = element.get_attribute("class")
                    text = element.text.strip()
                    aria_label = element.get_attribute("aria-label")
                    title = element.get_attribute("title")
                    
                    print(f"  Found: {tag_name} | Class: '{class_name}' | Text: '{text}' | Aria: '{aria_label}'")
                    
                    # Check if this looks like a logout element
                    is_logout_candidate = (
                        'logout' in (class_name or '').lower() or
                        'logout' in (text or '').lower() or
                        'logout' in (aria_label or '').lower() or
                        'logout' in (title or '').lower() or
                        'arrow' in (class_name or '').lower() or
                        'chevron' in (class_name or '').lower() or
                        'right' in (class_name or '').lower()
                    )
                    
                    if is_logout_candidate:
                        print(f"🎯 Potential logout element found!")
                        print(f"   Tag: {tag_name}")
                        print(f"   Class: '{class_name}'")
                        print(f"   Text: '{text}'")
                        print(f"   Aria: '{aria_label}'")
                        print(f"   Selector: {selector}")
                        
                        # Try to click it
                        try:
                            element.click()
                            print("✅ Logout element clicked!")
                            time.sleep(3)
                            
                            # Check if we're logged out
                            if "login" in driver.current_url.lower():
                                print("✅ Successfully logged out!")
                                return True
                            else:
                                print("⚠️ Clicked but not logged out - might be a different element")
                                
                        except Exception as click_error:
                            print(f"❌ Error clicking element: {click_error}")
                            
                except Exception as e:
                    print(f"  Error reading element: {e}")
                    continue
                    
        except Exception as e:
            print(f"❌ Error with selector {selector}: {e}")
            continue
    
    print("❌ No logout element found with any selector")
    return False

def main():
    """Main function"""
    driver = setup_chrome_driver()
    if not driver:
        print("❌ Failed to setup Chrome WebDriver")
        return
    
    try:
        print("🔍 Starting Auto Logout Finder...")
        
        # Login and navigate
        if not login_and_navigate(driver):
            print("❌ Login failed - cannot proceed")
            return
        
        # Find and click logout
        if find_and_click_logout(driver):
            print("🎉 Logout successful!")
        else:
            print("❌ Logout failed")
        
        print("\n🔍 Logout finding completed!")
        input("Press Enter to close the browser...")
        
    except Exception as e:
        print(f"❌ Error during logout finding: {e}")
    
    finally:
        try:
            driver.quit()
            print("🔒 Browser closed")
        except:
            pass

if __name__ == "__main__":
    main() 