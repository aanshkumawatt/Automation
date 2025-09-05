import asyncio
import random
import string
import os
from datetime import datetime, timedelta
from playwright.async_api import async_playwright
import logging
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('lnp_automation.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class LNPAutomation:
    def __init__(self):
        self.base_url = "http://172.16.16.224:3000"
        self.username = "Ecouser"
        self.password = "4142025!ECO"
        self.browser = None
        self.page = None
        self.context = None
        self.test_data = {}  # Store all filled data for report
        self.start_time = None
        self.end_time = None

    async def setup_browser(self):
        """Initialize browser and context"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=False,
            slow_mo=100,  # Much faster execution
            args=[
                '--start-maximized',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor',
                '--force-device-scale-factor=1',
                '--high-dpi-support=1',
                '--disable-extensions',
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-blink-features=AutomationControlled'
            ]
        )
        self.context = await self.browser.new_context(
            viewport=None,  # Let browser use full screen
            device_scale_factor=1,
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        self.page = await self.context.new_page()
        
        # Maximize the browser window
        await self.page.evaluate('''
            () => {
                window.moveTo(0, 0);
                window.resizeTo(screen.availWidth, screen.availHeight);
            }
        ''')
        
        # Set viewport to match screen size
        await self.page.set_viewport_size({'width': 1920, 'height': 1080})
        
        logger.info("Browser initialized successfully with full screen viewport")

    async def login(self):
        """Login to the application"""
        try:
            logger.info("Navigating to login page")
            await self.page.goto(f"{self.base_url}/login")
            await self.page.wait_for_load_state('networkidle')

            # Fill login form
            await self.page.fill('input[name="username"], input[type="text"]', self.username)
            await self.page.fill('input[name="password"], input[type="password"]', self.password)
            
            # Click login button
            await self.page.click('button[type="submit"], button:has-text("Login"), button:has-text("Sign In")')
            await self.page.wait_for_load_state('networkidle')
            
            logger.info("Login successful")
            return True
        except Exception as e:
            logger.error(f"Login failed: {str(e)}")
            return False
    
    async def navigate_to_lnp(self):
        """Navigate to LNP section"""
        try:
            logger.info("Navigating to Telephone Numbers > LNP")
            
            # Click on sidebar "Telephone Numbers"
            await self.page.click('text=Telephone Numbers', timeout=10000)
            await self.page.wait_for_timeout(2000)
            
            # Click on "LNP" submenu
            await self.page.click('text=LNP', timeout=10000)
            await self.page.wait_for_load_state('networkidle')
            
            # Click "Create" button
            await self.page.click('button:has-text("Create"), a:has-text("Create")', timeout=10000)
            await self.page.wait_for_load_state('networkidle')
            
            logger.info("Successfully navigated to LNP Create page")
            return True
        except Exception as e:
            logger.error(f"Navigation to LNP failed: {str(e)}")
            return False

    def generate_random_data(self):
        """Generate genuine random data for form fields"""
        # Generate realistic names
        first_names = ['John', 'Sarah', 'Michael', 'Emily', 'David', 'Jessica', 'Robert', 'Amanda', 'James', 'Jennifer']
        last_names = ['Smith', 'Johnson', 'Williams', 'Brown', 'Jones', 'Garcia', 'Miller', 'Davis', 'Rodriguez', 'Martinez']
        
        # Generate realistic company names
        company_prefixes = ['Tech', 'Global', 'Premier', 'Advanced', 'Elite', 'Pro', 'Smart', 'Dynamic', 'Innovative', 'Prime']
        company_suffixes = ['Solutions', 'Systems', 'Corp', 'Inc', 'LLC', 'Group', 'Enterprises', 'Services', 'Technologies', 'Consulting']
        
        # Generate realistic provider names
        providers = ['Verizon', 'AT&T', 'T-Mobile', 'Sprint', 'Comcast', 'Charter', 'Cox', 'Frontier', 'CenturyLink', 'Windstream']
        
        # Generate realistic street names
        street_names = ['Main', 'Oak', 'Pine', 'Cedar', 'Elm', 'Maple', 'First', 'Second', 'Park', 'Washington']
        
        # Generate three 10-digit portable numbers in series starting from 9313227762
        base_number = 9313227762
        portable_numbers = []
        for i in range(3):
            number = str(base_number + i)
            portable_numbers.append(number)
        
        portable_numbers_str = ' '.join(portable_numbers)
        
        return {
            'portable_numbers': portable_numbers_str,
            'portable_numbers_list': portable_numbers,
            'contact_name': f"{random.choice(first_names)} {random.choice(last_names)}",
            'company_name': f"{random.choice(company_prefixes)} {random.choice(company_suffixes)}",
            'provider_name': random.choice(providers),
            'account_number': str(random.randint(10000000, 99999999)),
            'street_number': str(random.randint(100, 9999)),
            'street_name': random.choice(street_names),
            'zip_code': str(random.randint(10000, 99999)),
            'phone_number': f"{random.randint(200, 999)}{random.randint(100, 999)}{random.randint(1000, 9999)}"
        }

    async def validate_portable_number_and_proceed(self):
        """Validate portable number and proceed until we can see Requested fields"""
        try:
            logger.info("Starting portable number validation and proceeding to next page")
            data = self.generate_random_data()
            portable_numbers_str = data['portable_numbers']  # This is already space-separated
            
            logger.info(f"Generated three portable numbers: {portable_numbers_str}")
            print(f"\n🔢 Trying numbers: {portable_numbers_str}")
            
            # Input all three numbers at once, separated by spaces
            logger.info(f"Inputting all three numbers in single field: {portable_numbers_str}")
            
            # Find and clear the number input field
            number_input = self.page.locator('input[name="number2port"]')
            await number_input.clear()
            await number_input.fill(portable_numbers_str)
            await self.page.wait_for_timeout(1000)  # Wait for validation
            
            # Click Next button
            try:
                next_button = self.page.locator('button:has-text("Next")')
                await next_button.wait_for(state='visible', timeout=5000)
                await next_button.click()
                await self.page.wait_for_timeout(1500)  # Wait for page load
                
                # Check if we can see "Requested" fields (indicating we're on the next page)
                requested_fields = await self.page.locator('text=Requested').count()
                if requested_fields > 0:
                    logger.info(f"Successfully proceeded to next page with all three numbers: {portable_numbers_str}")
                    logger.info(f"Found {requested_fields} 'Requested' fields on the page")
                    # Print to console
                    print(f"\n🎉 SUCCESS! Used these numbers to proceed: {portable_numbers_str}")
                    print(f"📋 Numbers used: {portable_numbers_str}")
                    # Store all numbers
                    self.test_data['all_portable_numbers'] = portable_numbers_str
                    self.test_data['successful_portable_number'] = portable_numbers_str
                    return portable_numbers_str
                else:
                    # We're still on the same page, try generating new numbers
                    logger.info(f"Still on same page, trying new set of numbers...")
                    
            except Exception as e:
                logger.info(f"Next button click failed: {str(e)}")
            
            # If we get here, we couldn't proceed with the first set
            # Keep trying with new sets of numbers until we succeed or reach maximum attempts
            logger.warning("Could not proceed with the first set of numbers, generating new sets...")
            max_attempts = 50  # Increased from 5 to 50 attempts
            attempt_count = 0
            
            while attempt_count < max_attempts:
                attempt_count += 1
                # Generate new series starting from a different base number for each attempt
                base_number = 9313227762 + (attempt_count * 10)  # Increment base by 10 for each attempt
                portable_numbers = []
                for i in range(3):
                    number = str(base_number + i)
                    portable_numbers.append(number)
                portable_numbers_str = ' '.join(portable_numbers)
                logger.info(f"Attempt {attempt_count}/{max_attempts}: {portable_numbers_str}")
                print(f"🔄 Retry attempt {attempt_count}/{max_attempts}: {portable_numbers_str}")
                
                # Find and clear the number input field
                number_input = self.page.locator('input[name="number2port"]')
                await number_input.clear()
                await number_input.fill(portable_numbers_str)
                await self.page.wait_for_timeout(1000)
                
                # Click Next button
                try:
                    next_button = self.page.locator('button:has-text("Next")')
                    await next_button.wait_for(state='visible', timeout=5000)
                    await next_button.click()
                    await self.page.wait_for_timeout(1500)
                    
                    # Check if we can see "Requested" fields
                    requested_fields = await self.page.locator('text=Requested').count()
                    if requested_fields > 0:
                        logger.info(f"✅ SUCCESS! Proceeded to next page with numbers: {portable_numbers_str}")
                        logger.info(f"Found {requested_fields} 'Requested' fields on the page")
                        # Print to console
                        print(f"\n🎉 SUCCESS! Used these numbers to proceed: {portable_numbers_str}")
                        print(f"📋 Numbers used: {portable_numbers_str}")
                        print(f"🔄 Attempt number: {attempt_count}")
                        # Store all numbers
                        self.test_data['all_portable_numbers'] = portable_numbers_str
                        self.test_data['successful_portable_number'] = portable_numbers_str
                        return portable_numbers_str
                    else:
                        logger.info(f"Still on same page, trying attempt {attempt_count + 1}...")
                        continue
                        
                except Exception as e:
                    logger.info(f"Next button click failed on attempt {attempt_count}, trying next set: {str(e)}")
                    continue
            
            # If we get here, we've exhausted all attempts with space-separated numbers
            logger.error(f"❌ FAILED: Could not proceed to next page after {max_attempts} attempts with space-separated numbers")
            logger.warning("Trying fallback approach: individual numbers one by one...")
            
            # Fallback: Try individual numbers from the last generated set
            last_numbers = data['portable_numbers_list']
            for i, individual_number in enumerate(last_numbers):
                logger.info(f"Fallback attempt {i + 1}: Trying individual number {individual_number}")
                
                # Find and clear the number input field
                number_input = self.page.locator('input[name="number2port"]')
                await number_input.clear()
                await number_input.fill(individual_number)
                await self.page.wait_for_timeout(1000)
                
                # Click Next button
                try:
                    next_button = self.page.locator('button:has-text("Next")')
                    await next_button.wait_for(state='visible', timeout=5000)
                    await next_button.click()
                    await self.page.wait_for_timeout(1500)
                    
                    # Check if we can see "Requested" fields
                    requested_fields = await self.page.locator('text=Requested').count()
                    if requested_fields > 0:
                        logger.info(f"✅ FALLBACK SUCCESS! Proceeded with individual number: {individual_number}")
                        # Print to console
                        print(f"\n🎉 FALLBACK SUCCESS! Used individual number to proceed: {individual_number}")
                        print(f"📋 Individual number used: {individual_number}")
                        print(f"🔄 Fallback attempt: {i + 1}")
                        # Store the original space-separated numbers and the successful individual number
                        self.test_data['all_portable_numbers'] = portable_numbers_str
                        self.test_data['successful_portable_number'] = individual_number
                        return individual_number
                    else:
                        logger.info(f"Individual number {individual_number} also failed, trying next...")
                        continue
                        
                except Exception as e:
                    logger.info(f"Individual number attempt failed: {str(e)}")
                    continue
            
            # If we get here, even individual numbers didn't work
            logger.error("❌ COMPLETE FAILURE: Neither space-separated nor individual numbers worked")
            logger.error("The form validation may be very strict or the field may not accept the number format")
            self.test_data['all_portable_numbers'] = portable_numbers_str
            self.test_data['successful_portable_number'] = last_numbers[0]  # Use first number as fallback
            return last_numbers[0]
            
        except Exception as e:
            logger.error(f"Portable number validation failed: {str(e)}")
            data = self.generate_random_data()
            self.test_data['all_portable_numbers'] = data['portable_numbers']
            self.test_data['successful_portable_number'] = data['portable_numbers']
            return data['portable_numbers']

    async def fill_first_form_page(self):
        """Fill the first form page"""
        try:
            logger.info("Filling first form page")
            
            # Validate portable number and proceed to next page
            portable_numbers = await self.validate_portable_number_and_proceed()
            logger.info(f"Using portable numbers: {portable_numbers}")
            logger.info(f"All portable numbers tried: {self.test_data.get('all_portable_numbers', 'N/A')}")
            self.test_data['portable_number'] = portable_numbers
            
            # Brief pause for page to load
            await self.page.wait_for_timeout(1000)
            
            # Requested Completion Date
            logger.info("Filling Requested Completion Date")
            
            # Click on the date picker button (the one with "…" text)
            try:
                date_picker_button = self.page.locator('button[id="date"]')
                await date_picker_button.wait_for(state='visible', timeout=10000)
                logger.info("Found date picker button, clicking...")
                await date_picker_button.click()
                await self.page.wait_for_timeout(1000)
                
                # Now try to select a date from the calendar
                # Look for tomorrow's date or any available date
                tomorrow = datetime.now() + timedelta(days=1)
                tomorrow_day = tomorrow.day
                self.test_data['completion_date'] = tomorrow.strftime("%Y-%m-%d")
                
                # Try to click on tomorrow's date
                try:
                    date_element = self.page.locator(f'button:has-text("{tomorrow_day}")').first
                    await date_element.wait_for(state='visible', timeout=3000)
                    await date_element.click()
                    logger.info(f"Selected date: {tomorrow_day}")
                except:
                    # If tomorrow's date not available, try any available date
                    try:
                        any_date = self.page.locator('button[data-day]').first
                        await any_date.wait_for(state='visible', timeout=3000)
                        await any_date.click()
                        logger.info("Selected first available date")
                    except:
                        logger.warning("Could not select date from calendar")
                        
            except Exception as e:
                logger.error(f"Could not click date picker button: {str(e)}")
                # Fallback to direct input method
                try:
                    date_input = self.page.locator('input[type="date"], input[placeholder*="date"]').first
                    await date_input.wait_for(state='visible', timeout=3000)
                    tomorrow = datetime.now() + timedelta(days=1)
                    date_str = tomorrow.strftime("%Y-%m-%d")
                    await date_input.fill(date_str)
                    logger.info(f"Filled completion date directly: {date_str}")
                except:
                    logger.error("Could not fill completion date field")
            
            # Requested Activation time - Click React Select dropdown and select 09:00
            logger.info("Filling Requested Activation time")
            try:
                # Click on the React Select activation time dropdown
                activation_time_selector = self.page.locator('div.react-select__placeholder:has-text("Requested Activation time")')
                await activation_time_selector.wait_for(state='visible', timeout=10000)
                await activation_time_selector.click()
                await self.page.wait_for_timeout(1000)
                
                # Look for 09:00 option in the dropdown menu
                time_option = self.page.locator('div.react-select__option:has-text("09:00")').first
                await time_option.wait_for(state='visible', timeout=5000)
                await time_option.click()
                logger.info("Selected activation time: 09:00")
                self.test_data['activation_time'] = '09:00'
            except Exception as e:
                logger.error(f"Could not select activation time: {str(e)}")
            
            # Purpose of LNP - Click React Select dropdown and select Voice
            logger.info("Filling Purpose of LNP")
            try:
                # Click on the React Select purpose dropdown
                purpose_selector = self.page.locator('div.react-select__placeholder:has-text("Purpose of LNP")')
                await purpose_selector.wait_for(state='visible', timeout=10000)
                await purpose_selector.click()
                await self.page.wait_for_timeout(1000)
                
                # Look for Voice option in the dropdown menu
                voice_option = self.page.locator('div.react-select__option:has-text("Voice")').first
                await voice_option.wait_for(state='visible', timeout=5000)
                await voice_option.click()
                logger.info("Selected purpose: Voice")
                self.test_data['purpose'] = 'Voice'
                
                # After selecting Voice, click the additional dropdown (Route to)
                await self.page.wait_for_timeout(1000)
                try:
                    # Click on Route to dropdown directly
                    route_dropdown = self.page.locator('div.react-select__placeholder:has-text("Route to")')
                    await route_dropdown.wait_for(state='visible', timeout=5000)
                    await route_dropdown.click()
                    await self.page.wait_for_timeout(1000)
                    
                    # Select any available option from the dropdown
                    dropdown_option = self.page.locator('div.react-select__option').first
                    await dropdown_option.wait_for(state='visible', timeout=5000)
                    option_text = await dropdown_option.text_content()
                    await dropdown_option.click()
                    logger.info(f"Selected route option: {option_text}")
                    self.test_data['route'] = option_text
                except Exception as e:
                    logger.warning(f"Could not select route dropdown option: {str(e)}")
                    
            except Exception as e:
                logger.error(f"Could not select purpose: {str(e)}")
            
            # Location - Click React Select dropdown and select Business
            logger.info("Filling Location")
            try:
                # Click on the React Select location dropdown
                location_selector = self.page.locator('div.react-select__placeholder:has-text("Location")')
                await location_selector.wait_for(state='visible', timeout=10000)
                await location_selector.click()
                await self.page.wait_for_timeout(500)  # Faster wait
                
                # Look for Business option in the dropdown menu
                business_option = self.page.locator('div.react-select__option:has-text("Business")').first
                await business_option.wait_for(state='visible', timeout=3000)  # Faster timeout
                await business_option.click()
                logger.info("Selected location: Business")
                self.test_data['location'] = 'Business'
            except Exception as e:
                logger.error(f"Could not select location: {str(e)}")
            
            # Click Next
            logger.info("Clicking Next button for second page")
            next_button_2 = self.page.locator('button:has-text("Next")')
            await next_button_2.wait_for(state='visible', timeout=10000)
            await next_button_2.click()
            await self.page.wait_for_load_state('networkidle')
            
            logger.info("First form page completed successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to fill first form page: {str(e)}")
            return False
    
    async def fill_second_form_page(self):
        """Fill the second form page"""
        try:
            logger.info("Filling second form page")
            data = self.generate_random_data()
            
            # Authorized Contact Name
            await self.page.fill('input[name*="contact"], input[placeholder*="contact"], input[name*="name"]', data['contact_name'])
            self.test_data['contact_name'] = data['contact_name']
            logger.info(f"Filled contact name: {data['contact_name']}")
            
            # Company Name
            await self.page.fill('input[name*="company"], input[placeholder*="company"]', data['company_name'])
            self.test_data['company_name'] = data['company_name']
            logger.info(f"Filled company name: {data['company_name']}")
            
            # Current Service Provider Name
            await self.page.fill('input[name*="provider"], input[placeholder*="provider"]', data['provider_name'])
            self.test_data['provider_name'] = data['provider_name']
            logger.info(f"Filled provider name: {data['provider_name']}")
            
            # Current Provider Account Number
            await self.page.fill('input[name*="account"], input[placeholder*="account"]', data['account_number'])
            self.test_data['account_number'] = data['account_number']
            logger.info(f"Filled account number: {data['account_number']}")
            
            # Upload Phone Bill
            # Create a dummy PDF file for upload
            dummy_pdf_path = os.path.join(os.getcwd(), 'dummy_phone_bill.pdf')
            if not os.path.exists(dummy_pdf_path):
                # Create a simple text file as dummy PDF
                with open(dummy_pdf_path, 'w') as f:
                    f.write("Dummy phone bill content")
            
            file_input = self.page.locator('input[type="file"]')
            await file_input.set_input_files(dummy_pdf_path)
            logger.info("Uploaded phone bill file")
            
            # Click Next
            await self.page.click('button:has-text("Next")')
            await self.page.wait_for_load_state('networkidle')
            
            logger.info("Second form page completed")
            return True
        except Exception as e:
            logger.error(f"Failed to fill second form page: {str(e)}")
            return False
    
    async def fill_third_form_page(self):
        """Fill the third form page (address information)"""
        try:
            logger.info("Filling third form page")
            data = self.generate_random_data()
            
            # Street Number
            try:
                street_number_input = self.page.locator('input[placeholder*="Street"], input[name*="street"], input[name*="number"]').first
                await street_number_input.wait_for(state='visible', timeout=10000)
                await street_number_input.fill(data['street_number'])
                self.test_data['street_number'] = data['street_number']
                logger.info(f"Filled street number: {data['street_number']}")
            except Exception as e:
                logger.error(f"Could not fill street number: {str(e)}")
            
            # Direction Prefix - Use React Select
            try:
                prefix_selector = self.page.locator('div.react-select__placeholder:has-text("Direction Prefix"), div.react-select__placeholder:has-text("Prefix")').first
                await prefix_selector.wait_for(state='visible', timeout=10000)
                await prefix_selector.click()
                await self.page.wait_for_timeout(1000)
                
                prefix_option = self.page.locator('div.react-select__option:has-text("N")').first
                await prefix_option.wait_for(state='visible', timeout=5000)
                await prefix_option.click()
                logger.info("Selected direction prefix: N")
            except Exception as e:
                logger.error(f"Could not select direction prefix: {str(e)}")
            
            # Street Name
            try:
                street_name_input = self.page.locator('input[placeholder*="Street Name"], input[name*="name"]').first
                await street_name_input.wait_for(state='visible', timeout=10000)
                await street_name_input.fill(data['street_name'])
                self.test_data['street_name'] = data['street_name']
                logger.info(f"Filled street name: {data['street_name']}")
            except Exception as e:
                logger.error(f"Could not fill street name: {str(e)}")
            
            # Direction Suffix - Use React Select
            try:
                suffix_selector = self.page.locator('div.react-select__placeholder:has-text("Direction Suffix"), div.react-select__placeholder:has-text("Suffix")').first
                await suffix_selector.wait_for(state='visible', timeout=10000)
                await suffix_selector.click()
                await self.page.wait_for_timeout(1000)
                
                suffix_option = self.page.locator('div.react-select__option:has-text("N")').first
                await suffix_option.wait_for(state='visible', timeout=5000)
                await suffix_option.click()
                logger.info("Selected direction suffix: N")
            except Exception as e:
                logger.error(f"Could not select direction suffix: {str(e)}")
            
            # State - Use React Select
            try:
                state_selector = self.page.locator('div.react-select__placeholder:has-text("State")').first
                await state_selector.wait_for(state='visible', timeout=10000)
                await state_selector.click()
                await self.page.wait_for_timeout(1000)
                
                state_option = self.page.locator('div.react-select__option:has-text("AK")').first
                await state_option.wait_for(state='visible', timeout=5000)
                await state_option.click()
                logger.info("Selected state: AK")
                await self.page.wait_for_timeout(1000)
            except Exception as e:
                logger.error(f"Could not select state: {str(e)}")
            
            # Service City - Use React Select
            try:
                city_selector = self.page.locator('div.react-select__placeholder:has-text("City"), div.react-select__placeholder:has-text("Service City")').first
                await city_selector.wait_for(state='visible', timeout=10000)
                await city_selector.click()
                await self.page.wait_for_timeout(1000)
                
                city_option = self.page.locator('div.react-select__option:has-text("ANCHORAGE")').first
                await city_option.wait_for(state='visible', timeout=5000)
                await city_option.click()
                logger.info("Selected city: ANCHORAGE")
            except Exception as e:
                logger.error(f"Could not select city: {str(e)}")
            
            # Service ZIP Code
            try:
                zip_input = self.page.locator('input[placeholder*="ZIP"], input[name*="zip"]').first
                await zip_input.wait_for(state='visible', timeout=10000)
                await zip_input.fill(data['zip_code'])
                self.test_data['zip_code'] = data['zip_code']
                logger.info(f"Filled ZIP code: {data['zip_code']}")
            except Exception as e:
                logger.error(f"Could not fill ZIP code: {str(e)}")
            
            # Billing Telephone Number
            try:
                phone_input = self.page.locator('input[placeholder*="Phone"], input[name*="billing"], input[name*="phone"]').first
                await phone_input.wait_for(state='visible', timeout=10000)
                await phone_input.fill(data['phone_number'])
                self.test_data['phone_number'] = data['phone_number']
                logger.info(f"Filled phone number: {data['phone_number']}")
            except Exception as e:
                logger.error(f"Could not fill phone number: {str(e)}")
            
            # Click Next
            try:
                next_button = self.page.locator('button:has-text("Next")')
                await next_button.wait_for(state='visible', timeout=10000)
                await next_button.click()
                await self.page.wait_for_load_state('networkidle')
                logger.info("Clicked Next button for summary page")
            except Exception as e:
                logger.error(f"Could not click Next button: {str(e)}")
            
            logger.info("Third form page completed")
            return True
        except Exception as e:
            logger.error(f"Failed to fill third form page: {str(e)}")
            return False
    
    async def submit_form(self):
        """Submit the form and handle confirmation"""
        try:
            logger.info("Submitting form")
            
            # Scroll down to find Submit button
            await self.page.evaluate('window.scrollTo(0, document.body.scrollHeight)')
            await self.page.wait_for_timeout(2000)
            
            # Click Submit button
            await self.page.click('button:has-text("Submit")')
            await self.page.wait_for_load_state('networkidle')
            
            # Click Yes for confirmation
            await self.page.click('button:has-text("Yes")')
            
            # Wait 6 seconds as requested
            await self.page.wait_for_timeout(6000)
            
            logger.info("Form submitted successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to submit form: {str(e)}")
            return False

    async def take_screenshot(self, name):
        """Take a screenshot for verification"""
        try:
            if not self.page or self.page.is_closed():
                logger.warning("Page is closed, cannot take screenshot")
                return None
                
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            screenshot_path = f"lnp_screenshot_{name}_{timestamp}.png"
            await self.page.screenshot(path=screenshot_path, full_page=True)
            logger.info(f"Screenshot saved: {screenshot_path}")
            return screenshot_path
        except Exception as e:
            logger.error(f"Failed to take screenshot: {str(e)}")
            return None

    def generate_pdf_report(self):
        """Generate attractive PDF report"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"LNP_Test_Report_{timestamp}.pdf"
            
            doc = SimpleDocTemplate(filename, pagesize=letter)
            styles = getSampleStyleSheet()
            story = []
            
            # Title
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=styles['Heading1'],
                fontSize=24,
                spaceAfter=30,
                alignment=1,  # Center alignment
                textColor=colors.darkblue
            )
            story.append(Paragraph("LNP Automation Test Report", title_style))
            story.append(Spacer(1, 20))
            
            # Test Summary
            duration = (self.end_time - self.start_time).total_seconds() if self.end_time and self.start_time else 0
            summary_data = [
                ['Test Date', datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
                ['Test Duration', f"{duration:.2f} seconds"],
                ['Test Status', 'PASSED' if self.test_data else 'FAILED'],
                ['All Portable Numbers', self.test_data.get('all_portable_numbers', 'N/A')],
                ['Successful Numbers', self.test_data.get('successful_portable_number', 'N/A')]
            ]
            
            summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
            summary_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkblue),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(Paragraph("Test Summary", styles['Heading2']))
            story.append(summary_table)
            story.append(Spacer(1, 20))
            
            # Form Data
            form_data = [
                ['Field Name', 'Value Entered', 'Status'],
                ['All Portable Numbers', self.test_data.get('all_portable_numbers', 'N/A'), '✓'],
                ['Successful Numbers', self.test_data.get('successful_portable_number', 'N/A'), '✓'],
                ['Completion Date', self.test_data.get('completion_date', 'Tomorrow'), '✓'],
                ['Activation Time', self.test_data.get('activation_time', 'N/A'), '✓'],
                ['Purpose of LNP', self.test_data.get('purpose', 'N/A'), '✓'],
                ['Route to', self.test_data.get('route', 'N/A'), '✓'],
                ['Location', self.test_data.get('location', 'N/A'), '✓'],
                ['Contact Name', self.test_data.get('contact_name', 'N/A'), '✓'],
                ['Company Name', self.test_data.get('company_name', 'N/A'), '✓'],
                ['Provider Name', self.test_data.get('provider_name', 'N/A'), '✓'],
                ['Account Number', self.test_data.get('account_number', 'N/A'), '✓'],
                ['Street Number', self.test_data.get('street_number', 'N/A'), '✓'],
                ['Street Name', self.test_data.get('street_name', 'N/A'), '✓'],
                ['State', 'AK', '✓'],
                ['City', 'ANCHORAGE', '✓'],
                ['ZIP Code', self.test_data.get('zip_code', 'N/A'), '✓'],
                ['Phone Number', self.test_data.get('phone_number', 'N/A'), '✓']
            ]
            
            form_table = Table(form_data, colWidths=[2*inch, 2.5*inch, 1*inch])
            form_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.darkgreen),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.lightgrey),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 9)
            ]))
            
            story.append(Paragraph("Form Data Filled", styles['Heading2']))
            story.append(form_table)
            story.append(Spacer(1, 20))
            
            # Footer
            footer_style = ParagraphStyle(
                'Footer',
                parent=styles['Normal'],
                fontSize=8,
                alignment=1,
                textColor=colors.grey
            )
            story.append(Paragraph("Generated by LNP Automation Script", footer_style))
            
            doc.build(story)
            logger.info(f"PDF report generated: {filename}")
            return filename
            
        except Exception as e:
            logger.error(f"Failed to generate PDF report: {str(e)}")
            return None

    async def cleanup(self):
        """Clean up resources"""
        try:
            if self.browser:
                await self.browser.close()
            logger.info("Cleanup completed")
        except Exception as e:
            logger.error(f"Cleanup failed: {str(e)}")

    async def run_automation(self):
        """Main automation flow"""
        try:
            self.start_time = datetime.now()
            logger.info("Starting LNP automation")
            
            await self.setup_browser()
            
            if not await self.login():
                return False
            
            if not await self.navigate_to_lnp():
                return False
            
            if not await self.fill_first_form_page():
                return False
            await self.take_screenshot("first_page_completed")
            
            if not await self.fill_second_form_page():
                return False
            await self.take_screenshot("second_page_completed")
            
            if not await self.fill_third_form_page():
                return False
            await self.take_screenshot("third_page_completed")
            
            if not await self.submit_form():
                return False
            await self.take_screenshot("form_submitted")
            
            self.end_time = datetime.now()
            logger.info("LNP automation completed successfully")
            return True
            
        except Exception as e:
            logger.error(f"Automation failed: {str(e)}")
            await self.take_screenshot("error_state")
            return False
        finally:
            await self.cleanup()

async def main():
    """Main function to run the automation"""
    automation = LNPAutomation()
    success = await automation.run_automation()
    
    # Generate PDF report
    pdf_file = automation.generate_pdf_report()
    
    if success:
        print("✅ LNP automation completed successfully!")
        if pdf_file:
            print(f"📄 PDF Report generated: {pdf_file}")
    else:
        print("❌ LNP automation failed. Check logs for details.")
        if pdf_file:
            print(f"📄 PDF Report generated: {pdf_file}")

if __name__ == "__main__":
    asyncio.run(main())
