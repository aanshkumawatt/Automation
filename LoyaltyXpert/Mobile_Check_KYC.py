#!/usr/bin/env python3
"""
Mobile KYC Check Automation Script
Automates the loyalty application on Android emulator
"""

import subprocess
import time
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'mobile_kyc_automation_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

class MobileKYCAutomation:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.package_name = "ecosmob.loyaltyxpert.com"  # Actual package name found on emulator
        
    def run_adb_command(self, command):
        """Execute ADB command and return result"""
        try:
            result = subprocess.run(
                f"adb {command}",
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            if result.returncode == 0:
                self.logger.info(f"ADB command successful: {command}")
                return result.stdout.strip()
            else:
                self.logger.error(f"ADB command failed: {command}")
                self.logger.error(f"Error: {result.stderr}")
                return None
        except subprocess.TimeoutExpired:
            self.logger.error(f"ADB command timed out: {command}")
            return None
        except Exception as e:
            self.logger.error(f"Error executing ADB command: {e}")
            return None
    
    def check_device_connection(self):
        """Check if emulator is connected"""
        devices = self.run_adb_command("devices")
        if devices and "device" in devices:
            self.logger.info("Emulator is connected")
            return True
        else:
            self.logger.error("No emulator found. Please ensure emulator is running.")
            return False
    
    def launch_loyalty_app(self):
        """Launch the loyalty application"""
        self.logger.info("Launching loyalty application...")
        result = self.run_adb_command(f"shell am start -n {self.package_name}/.MainActivity")
        if result:
            self.logger.info("Loyalty application launched successfully")
            return True
        else:
            self.logger.error("Failed to launch loyalty application")
            return False
    
    def wait(self, seconds):
        """Wait for specified number of seconds"""
        self.logger.info(f"Waiting for {seconds} seconds...")
        time.sleep(seconds)
    
    def click_coordinates(self, x, y):
        """Click at specified coordinates"""
        self.logger.info(f"Clicking at coordinates: ({x}, {y})")
        result = self.run_adb_command(f"shell input tap {x} {y}")
        if result is not None:
            self.logger.info(f"Click successful at ({x}, {y})")
            return True
        else:
            self.logger.error(f"Click failed at ({x}, {y})")
            return False
    
    def close_application(self):
        """Close the loyalty application"""
        self.logger.info("Closing loyalty application...")
        result = self.run_adb_command(f"shell am force-stop {self.package_name}")
        if result is not None:
            self.logger.info("Loyalty application closed successfully")
            return True
        else:
            self.logger.error("Failed to close loyalty application")
            return False
    
    def run_automation(self):
        """Main automation sequence"""
        self.logger.info("Starting Mobile KYC Check Automation")
        
        # Check device connection
        if not self.check_device_connection():
            return False
        
        try:
            # Step 1: Launch loyalty application
            if not self.launch_loyalty_app():
                return False
            
            # Step 2: Wait 10 seconds after launch
            self.wait(10)
            
            # Step 3: Click at (x=1022, y=170)
            if not self.click_coordinates(1022, 170):
                return False
            
            # Step 4: Wait 10 seconds after first click
            self.wait(10)
            
            # Step 5: Click at (x=356, y=356)
            if not self.click_coordinates(356, 356):
                return False
            
            # Step 6: Wait 10 seconds after second click
            self.wait(10)
            
            # Step 7: Close the application
            if not self.close_application():
                return False
            
            self.logger.info("Mobile KYC Check Automation completed successfully!")
            return True
            
        except Exception as e:
            self.logger.error(f"Automation failed with error: {e}")
            return False

def main():
    """Main function to run the automation"""
    automation = MobileKYCAutomation()
    
    print("Mobile KYC Check Automation")
    print("=" * 40)
    
    success = automation.run_automation()
    
    if success:
        print("\n✅ Automation completed successfully!")
        print("Check the log file for detailed information.")
    else:
        print("\n❌ Automation failed!")
        print("Check the log file for error details.")
    
    return 0 if success else 1

if __name__ == "__main__":
    exit(main())
