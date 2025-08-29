#!/bin/bash

# ========================================
# LoyaltyXpert Mobile Announcement Automation
# ========================================
# Simple mobile automation for LoyaltyXpert announcements
# ========================================

echo -e "\033[32m🎯 LoyaltyXpert Mobile Announcement Automation Started\033[0m"
echo -e "\033[36m====================================================\033[0m"

# Check if adb is available
if ! command -v adb &> /dev/null; then
    echo -e "\033[31m❌ ADB is not installed. Please install Android SDK\033[0m"
    exit 1
fi

# Device configuration
DEVICE_ID="emulator-5554"

# Function to perform mobile actions
mobile_action() {
    local x="$1"
    local y="$2"
    local description="$3"
    local wait_time="${4:-2}"
    
    echo -e "\033[33m📱 Clicking ($x, $y) - $description\033[0m"
    adb -s $DEVICE_ID shell input tap $x $y
    sleep $wait_time
}

# Function to type text on mobile
mobile_type() {
    local text="$1"
    local description="$2"
    
    echo -e "\033[33m📱 Typing: $text - $description\033[0m"
    adb -s $DEVICE_ID shell input text "$text"
    sleep 2
}

# Function to wait
wait_for() {
    local seconds="$1"
    local description="$2"
    
    echo -e "\033[35m⏱️  Waiting $seconds seconds - $description\033[0m"
    sleep $seconds
}

# Check mobile device connection
echo -e "\033[33m🔍 Checking mobile device connection...\033[0m"
if adb devices | grep -q "$DEVICE_ID"; then
    echo -e "\033[32m✅ Mobile device connected: $DEVICE_ID\033[0m"
else
    echo -e "\033[31m❌ Mobile device not found: $DEVICE_ID\033[0m"
    echo -e "\033[33mPlease ensure emulator-5554 is running\033[0m"
    exit 1
fi

# ============================================================================
# MOBILE AUTOMATION - LOYALTYXPRT ANNOUNCEMENTS
# ============================================================================

echo -e "\033[32m📱 Starting LoyaltyXpert Mobile Automation\033[0m"
echo -e "\033[36m==========================================\033[0m"

# Step 1: Launch LoyaltyXpert
echo -e "\033[33m📱 Launching LoyaltyXpert Application\033[0m"
adb -s $DEVICE_ID shell am start -n ecosmob.loyaltyxpert.com/.MainActivity
wait_for 13 "App to load"

# Step 2: Click Mobile Number Field
mobile_action 331 1672 "Mobile Number Field"

# Step 3: Type Mobile Number
mobile_type "8528528521" "Mobile Number"

# Step 4: Click Login Button
mobile_action 530 1282 "Login Button"

# Step 5: Wait for Loading
wait_for 3 "Loading Dialog"

# Step 6: OTP Enter
mobile_action 157 1851 "Type OTP"

# Step 7: Read OTP from screen
echo -e "\033[33m📱 Reading OTP from screen...\033[0m"

# Take screenshot to read OTP
adb -s $DEVICE_ID shell screencap /sdcard/otp_screen.png
adb -s $DEVICE_ID pull /sdcard/otp_screen.png ./otp_screen.png

# Function to automatically read OTP from screenshot using advanced Python script
read_otp_automatically() {
    echo -e "\033[33m📱 Capturing OTP screenshot for advanced automatic reading...\033[0m"
    
    # Take screenshot of OTP screen
    adb -s $DEVICE_ID shell screencap /sdcard/otp_screen.png
    adb -s $DEVICE_ID pull /sdcard/otp_screen.png ./otp_screen.png
    
    # Create a unique filename with timestamp
    local timestamp=$(date +"%Y%m%d_%H%M%S")
    local otp_image="./otp_screen_${timestamp}.png"
    cp ./otp_screen.png "$otp_image"
    
    echo -e "\033[32m📱 OTP Screenshot saved as: $otp_image\033[0m"
    
    # Use the advanced Python OTP reader
    if command -v python3 &> /dev/null; then
        echo -e "\033[33m📱 Using advanced OTP reader...\033[0m"
        
        # Change to the script directory to ensure Python can find the file
        cd "$(dirname "$0")"
        
        # Run the advanced Python script and capture output
        local python_output=$(python3 ./advanced_otp_detector.py "$otp_image" 2>&1)
        echo -e "\033[33m📱 Python script output:\033[0m"
        echo "$python_output"
        
        # Extract OTP from output
        local otp=$(echo "$python_output" | grep "FINAL_OTP:" | cut -d':' -f2)
        
        if [[ -n "$otp" && "$otp" != "0000" ]]; then
            echo -e "\033[32m📱 OTP Found via advanced reader: $otp\033[0m"
            echo "$otp" > ./last_otp.txt
            echo "$otp"
            return 0
        else
            echo -e "\033[31m❌ Advanced OTP reader failed. Using fallback.\033[0m"
            echo "3234" > ./last_otp.txt
            echo "3234"
        fi
    else
        echo -e "\033[31m❌ Python3 not available. Using fallback.\033[0m"
        echo "3234" > ./last_otp.txt
        echo "3234"
    fi
}



# Read and save OTP
OTP_VALUE=$(read_otp_automatically)
echo -e "\033[32m📱 Saved OTP: $OTP_VALUE\033[0m"

# Step 8: Type the read OTP
echo -e "\033[33m📱 Typing OTP: $OTP_VALUE\033[0m"
# Ensure OTP is properly formatted and type it
if [[ -n "$OTP_VALUE" && "$OTP_VALUE" =~ ^[0-9]{4}$ ]]; then
    adb -s $DEVICE_ID shell input text "$OTP_VALUE"
else
    echo -e "\033[31m❌ Invalid OTP format: $OTP_VALUE\033[0m"
    # Use fallback OTP
    adb -s $DEVICE_ID shell input text "3234"
fi

# Step 9: Wait for OTP Typing
wait_for 17 "OTP Typing"

# Step 10: Three Line Click
mobile_action 29 149 "Three Line Click" 6

# Step 11: Click Announcements
mobile_action 230 1096 "Announcements"

# Step 12: Wait for Loading
wait_for 4 "Loading Dialog"

# Step 13: Click Top Announcements
mobile_action 335 353 "Announcements"

# Step 14: Wait to see Announcements
wait_for 5 "Announcements"

echo -e "\033[32m✅ LoyaltyXpert Mobile Announcement Automation Completed!\033[0m"
echo -e "\033[36m====================================================\033[0m"
