"""

███╗   ██╗██╗██╗  ██╗███████╗    ██████╗  ██████╗ ████████╗
████╗  ██║██║██║ ██╔╝██╔════╝    ██╔══██╗██╔═══██╗╚══██╔══╝
██╔██╗ ██║██║█████╔╝ █████╗      ██████╔╝██║   ██║   ██║   
██║╚██╗██║██║██╔═██╗ ██╔══╝      ██╔══██╗██║   ██║   ██║   
██║ ╚████║██║██║  ██╗███████╗    ██████╔╝╚██████╔╝   ██║   
╚═╝  ╚═══╝╚═╝╚═╝  ╚═╝╚══════╝    ╚═════╝  ╚═════╝    ╚═╝   
                                                           

"""
#Coded by Mark Cuccarese 

import sys
import os 
import platform
import pause
import arrow 
import webbrowser
import urllib3 
import selenium
import time
import psutil
import signal
import subprocess
import versionCheck #import python versionCheck file 
from os import path
from pyvirtualdisplay import Display
from urllib.request import urlopen 
from datetime import datetime
from selenium import webdriver 
from contextlib import suppress
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys 
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

#Just a fancy exception 
class WebpageNotFound(Exception): 
    """
    This will be raised if the webpage cannot be found 
    """

#Display system version check info 
def displaySysInfo(driver): 
    print("++++++++++++++++++++++++++++++++++++++++++++++++++")
    print("Linux platform system: " + platform.system())
    print("Linux platform version: " + platform.version())
    print("Linux platform release: " + platform.release())
    print("Selenium version: " + (selenium.__version__))
    print("Python version: " + sys.version)

    if 'browserVersion' in driver.capabilities:
        print("Chrome version: " + driver.capabilities['browserVersion'])
    else:
        print("Chrome version: " + driver.capabilities['version'])

    print("Chrome driver version: " + driver.capabilities['chrome']['chromedriverVersion'].split(' ')[0])

    print("++++++++++++++++++++++++++++++++++++++++++++++++++\n")

#Check for appropriate time to exectute 
def waitUntil(specified_dt): 

    #Setting a default refresh rate and updating current time 
    refresh = 10               
    current_dt = arrow.utcnow() 

    #Checking that we are not within 11 seconds of drop 
    while current_dt < specified_dt:
        current_dt = arrow.utcnow() 
        remain = specified_dt - current_dt 

        #Shortening refresh rate if we are close 
        if (remain).seconds < 11: 
            refresh = .001

        print("Waiting..." + str(remain))
        time.sleep(refresh)

    else: 
        print("Starting...")
        return 

#Prompt the user for config file 
def printConfigPrompt(): 
    print(""" 
    Please place the a text file exactly as shown called config.txt 
    in the root directory of this script, delete any excess spaces
    ____________________________________________________________
    time of drop in 24hrs   EXAMPLE [15]    
    size needed             EXAMPLE [7.5]
    pre-release url         EXAMPLE [https://www.nike.com/launch/t/air-force-1-lv8-pacific-blue]
    quantity desired        EXAMPLE [1]  
    email address           EXAMPLE [YouKindaSus@gmail.com]
    password                EXAMPLE [DooDooNose1]
    phone number            EXAMPLE [4074074077]
    card number             EXAMPLE [2222 2222 2222 2222]
    expiration date         EXAMPLE [02/22]
    cvv                     EXAMPLE [222]
    zipcode                 EXAMPLE [22222]
    name on card            EXAMPLE [Martin Lawrence]
    shipping address        EXAMPLE [2222 Estern Way Orlando, Fl 32789]
    ____________________________________________________________
    ***Make sure your config file matches this EXACTLY***
    ***The shoe sizing of the program is should be given in US mens sizes (Does not support children sizes)***
    ***Make sure you have an active internet connection the entire time***
    ***To account for crashes, this program kills any chrome/chromium sessions once finished***\n
    ***Press enter whenever you are ready!***\n
    """)
    
#Make sure internet is available 
def checkinternet():
    try:
        #Setting up a pool to make a request to google 
        http = urllib3.PoolManager()
        resp = http.request('GET', 'https://www.google.com/')
        
        #For success we should have 200 
        if resp.status == 200:
            return True
        else: 
            return False 
    except:
        return False

"""
#A second option for checking internet 
def checkinternet2():
    
    #get_network_conditions() 
    cond = {}
    cond = webdrier.get_network_conditions() 
    if cond["offline"] is True: 
        time.sleep(2)
        checkinternet2()
    else: 
        return 

#A third option for checking internet 
def checkinternet3(driver):
    if driver.capabilities['networkConnection'] == 'Disabled':
        time.sleep(2)
        checkInternet3(driver)   
    else: 
        return  
"""

#Read input from file 
def openfile():

    try:
        #Opening the file and reading into list
        file = open("configfile.txt", "r+")   
        lines = file.read().split("\n")   
        #Switching them to lowercase 
        lines = [lines.lower() for x in lines]

    finally:
        #Closing the file 
        file.close()                          
        return lines

#Verifies that the name of product matches URL 
def compare(elem_name, url):    

    url = url.lower()
    elem_name = elem_name.lower() 

    #Omitting everything except shoe name 
    string = url[30:len(url)]

    #Remove dashes from string/url
    new_string = string.replace('-', '')

    #Remove spaces from elem_name
    new_elem_name = elem_name.replace(' ', '')

    #Extra check for edge cases 
    new_elem_name2 = new_elem_name[0:5]

    #Success, the scraped name is in the url 
    if new_elem_name in new_string: 
        print("Website certainty accepted by name match")
        return

    #Some cases dictate that the name is not the same, will not exit but will raise notice
    elif new_elem_name2 in new_string:
        print("Website certainty accepted by name match")
        return
    else: 
        print("Website certainty challenged by name mismatch")
        return

#This function is used to kill the Child PID in the event of an error 
#To stop the formation of zombie processes          
def kill():

    #Get the PID
    #driver.service.process #<- this is the popen instance for the chroemdriver
    #Cpid = psutil.Process(driver.service.process.pid)
    #print(Cpid.children(recursive=False))
  
    print("\nChecking for sleeping/zombie chromium sessions to kill\n")

    #Loop through process table 
    for process in psutil.process_iter():
        #Check for any zombie or sleeping chromium processes 
        if process.name() == 'chromium': #and process.status() == 'zombie':
            #Attemp to kill zombie processes 
            print("\tFound zombie chromium to kill: " + str(process.ppid()))
            try:    
                os.kill(int(process.ppid()), signal.SIGTERM)
                continue
            except:
                print("Failed to kill chromium process\n")
                driver.quit()
                quit() 
            
    print("Checking for sleeping/zombie google-chrome sessions to kill\n")

      #Loop through the process table 
    for process in psutil.process_iter(): 
        #Check for any zombie or sleeping chrome processes 
        if process.name() == 'chrome':
            print("\tFound google chrome process to kill: " + str(process.ppid()))
            try:
                os.kill(int(process.ppid()), signal.SIGTERM)
                continue
            except:
                print("Failed to kill google-chrome process\n")
                driver.quit()
                quit()         
              
    return

#Takes the sizes and determines type 
def tellType(driver):
    
    #This will get the UL list of sizes 
    resultSet = driver.find_element_by_css_selector(".size-layout")
    #This list hold our list for iteration of individual sizes 
    options = resultSet.find_elements_by_tag_name("li")
    #Setting our sizes into the list 
    for option in options:
        sizeList.append(option.text)

    #We are going to use the first size option present on the page to evaluate 
    string = sizeList[0]

    #If the string starts with a number         
    if string[0].isdigit():
        #Check to see if the sizing is youths                       [5]
        if string.find('Y') != -1:
            sizeType = 5
        #Adults                                                     [1]
        else:                                              
            sizeType = 1 
   
    #If this string starts with M and the next char is a space      [2]
    elif string[0] == 'M' and string[1] == ' ':
        sizeType = 2 
    #elis if this string starts with W and the next char is a space [3]
    elif string[0] == 'W' and string[1] == ' ':
        sizeType = 3
    #If the string starts with XXS S M L {No numbers}               [4]
    elif not any(char.isdigit() for char in string):
        sizeType = 4
        
    return sizeType

#This function has to filter all the sizes to only shoe available ones  
def checkSize(driver, sizeME, sizeType):

    #Clear the sizeList, because it currently holds ALL sizes 
    sizeList.clear()

    #Retrieve only available sizes 
    resultSet = driver.find_element_by_css_selector(".size-layout")
    options = resultSet.find_elements_by_tag_name("li")

    print("\nOur Available list:")

    #Take the option from the list and check avail
    for option in options:
        #If the option is available, place it into the list
        if(option.get_attribute("data-qa") == 'size-available'):
            print(option.text)
            print("\t")
            sizeList.append(option.text)
    print("++++++++++++++++++++++++++\n")

    sizeME = str(sizeME)

    #Verify that we can find our size in the list 
    if sizeME in sizeList:
        print("Desired size: " + sizeME + " is available!")
        return True

    print("Could not find size {0} in list!\n".format(sizeME))
    return False
        
#Function will convert the size taken from config into the size style used on the site  
def stringMagic(driver, temp, sizeType):

    #Cheeky way of using lists in a dictionary 
    dictionary = {} 
    dictionary["XXS"] = [1, 1.5, 2]
    dictionary["XS"] = [2.5, 3]
    dictionary["S"] = [3.5, 4, 4.5, 5, 5.5]
    dictionary["M"] = [6, 6.5, 7, 7.5, 8]
    dictionary["L"] = [8.5, 9, 9.5, 10, 10.5]
    dictionary["XL"] = [11, 11.5, 12, 12.5, 13]
    dictionary["XXL"] = [13.5, 14, 14.5, 15.5]


    tempWomens1 = float(temp) + 1.5
    tempWomens2 = float(temp) - 1.5

    #If temp is a float, the second value must be int 
    if temp.find(".") != -1:   
        temp = str(temp)
        tempWomens1 = int(tempWomens1)
        tempWomens2 = int(tempWomens2)
    #If temp is an int, the second value must be a float 
    else:                   
        temp = int(temp)
        tempWomens1 = str(tempWomens1) 
        tempWomens2 = str(tempWomens2) 

    #If type int just return otherwise convert singular string to type and return 
    if sizeType > 1:

        #The case where M X / W X 
        if sizeType == 2:
            string = ("M " + str(temp) + " / W " + str(tempWomens1))
            return string 

        #The case where W X / M X 
        elif sizeType == 3: 
            string = ("W " + str(temp) + " / M " + str(tempWomens2))
            return string 

        #The case were XXS S M L XL 
        elif sizeType == 4:
            #Breaking up the keys and values 
            key_list = list(dictionary.keys())
            val_list = list(dictionary.values())

            #Sorting the key by the value index
            position = val_list.index(temp)
            size = key_list[position]
            return size

        #The case we have a YOUTHS shoe 
        elif sizeType == 5:
            youths = str(temp) + "Y"
            return youths

    #The case where the value is simplly an int 
    else:
        return temp 

#Determine if the user wants a different shoe size 
def ask(question):
    #Present the question 
    reply = (input(question)).lower().strip()  
    
    if reply[0] == 'y': 
        return True 
    elif reply[0] == 'n':
        return False
    else: 
        return ask("Please enter either y or n dummy: ")

#Make sure that size elements are present! 
def checkAvail(driver):
    
    #checkme = str(driver.find_element_by_css_selector('.mt9-sm').text)

    #Check if the shoe is sold out 
    #if checkme == 'Sold Out':
    #    driver.quit() 
    #    raise NoSuchElementException("Sold out :c\n")
    #else: 
    #    print("Shoe is available!\n")
    #    return
    try: 
        #Wait until the size display is loaded 
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, '.size-layout'))) 
        
        if driver.find_element_by_css_selector('.size-layout').is_displayed():
            return
    except: 
        #If the display is not loaded the shoe must be sold out 
        raise NoSuchElementException("Sold out\n")
        kill()
        driver.quit()
        quit()

#Method to take a screenshot of purchase page 
def shotScreen(driver): 


    #Verify that the file doesnt already exist in root directory 
    if os.path.exists("ConfirmationPage.png") == True:
        os.remove("ConfirmationPage.png")

    try: 
        #Try and screenshot the confirmation 
        if driver.get_screenshot_as_file("ConfirmationPage.png") == True:
            print("Screenshot of Order Confirmation has generated!\n")
            return 
        else: 
            time.sleep(2)
            driver.quit()
            kill()
            quit()
    except: 
        time.sleep(2)
        driver.quit()
        kill()
        quit()


#Open chrome application and execute operations 
def openURL(url):

    try:         
        #Uncommenting the following 2 lines will use PyVirtualDisplay module, in which case you will not see the window##########
        #display = Display(visible = 0, size = (800, 800))
        #display.start()
        try:
            #Load the browser instance 
            driver = webdriver.Chrome()    #This assumes that you have proper permissions for chrome and the driver in root directory of folder, have it in /usr/bin/ also just to be safe 
            print("I have spawned the browser!\n")
        except:
            #The following takes effect in the instance that Chromedriver assuming google chrome has crashed##########
            chrome_options = Options()
            chrome_options.add_argument('--headless')
            chrome_options.add_argument('--no-sandbox')
            chrome_options.add_argument('--disable-dev-shm-usage')
            
            driver = webdriver.Chrome(chrome_options=chrome_options)
            ###############################################
            print("I have spawned the browser with additional arguments!\n")


        #Show system information and versions
        displaySysInfo(driver)   

        #Open the given url and wait for it to load
        driver.get(url)
        time.sleep(5)

    except Exception as e: 
        print("Caught an error while opening browser\n" + e)
        driver.quit()
        quit()

    #This will give us the name of the shoe and price 
    elem_name1 = driver.find_element_by_tag_name('h1').text
    elem_name2 = driver.find_element_by_tag_name('h5').text
    price = driver.find_element_by_css_selector('.headline-5').text
    print("++++++++++++++++++++++++++++++++") 
    print("\t+++++ " + elem_name1 + " +++++")
    print("\t+++++ " + elem_name2 + " +++++")
    print("\t+++++ " + price + " +++++")
    print("++++++++++++++++++++++++++++++++\n") 
    #Check the name of the shoe with the name in the url 
    #if compare(elem_name1, url) or compare(elem_name2, url) is True:
    #    print("Landed on correct web page! Continuing!\n")

    #Check url and shoe name 
    compare(elem_name1, url)
    compare(elem_name2, url)

    #Check for error 
    try:
        error1 = driver.find_element_by_css_selector(".text-color-error")
        error2 = driver.find
        if error.is_displayed():
            print("HALTED no sizes displayed")
    except: 
        pass


    #Get the desired size from config file 
    sizeME = lines[1]

    #Check to make sure that its not sold out and is buy able 
    checkAvail(driver)

    #This func will analyze the sizing style used by the site to later adjust for the the user input 
    sizeType = tellType(driver)

    #Changes the sizeME var into correct type for checking 
    sizeME = stringMagic(driver, sizeME, sizeType)  

    #This will input only available sizes into list and check availability 
    #certain = checkSize(driver, sizeME, sizeType)

    #Raise an assertation error if the size is not available 
    assert checkSize(driver,sizeME,sizeType), "Size requested is not available"

    #Begin the heading to cart process 
    try: 
        #Getting the elements for sizing 
        resultSet = driver.find_element_by_css_selector(".size-layout")
        options = resultSet.find_elements_by_tag_name("li")

        #Finding the correct shoe size and selecting 
        for option in options:
            if(option.get_attribute("data-qa") == 'size-available'):
                if option.text == sizeME:
                    option.click()
                    print("Selected size!")
                    break

        #Clicking the "Add to cart"
        Add2Cart = driver.find_element_by_css_selector(".ncss-btn-primary-dark").click()
        print("Added size " + sizeME + " to cart without error!\n")

    #Failure to select a size 
    except:
        try:

            time.sleep(2)

            #Failed to select a size 
            obj = driver.find_element_by_css_selector('.test-error-message')
            print("Error has been found: {0}\n -->Has been handled<--\n".format(obj.text))

            #If we find an error we are going to handle with different elements
            if obj.is_displayed(): 

                resultSet = driver.find_element_by_css_selector(".border-light-grey")
                options = resultSet.find_elements_by_tag_name("li")

                #Finding the correct shoe size and selecting 
                for option in options:
                    if(option.get_attribute("data-qa") == 'size-available'):
                        if str(option.text) == str(sizeME):
                            option.click()
                            print("Selected size!")
                            break

            #Selecting add to cart option 
            Add2Cart = driver.find_element_by_css_selector("[data-qa='add-to-cart']")
            Add2Cart.click()

        except:
            print("Error inside of error!\n")


    time.sleep(3)

    try:
        #Check to find out of the shopping cart popup is visible [timer of approx 8 seconds]
        cartWindow = driver.find_element_by_css_selector(".cart-item-modal-content-container")                               #Window to proceed to checkout
        checkoutButton = driver.find_element_by_xpath("/html/body/div[2]/div/div/div[2]/div/div/div/div/div[3]/button[2]")   #Go to cart button
        filledShoppingCart1 = driver.find_element_by_css_selector(".right-menu").text                                        #Indicator of a filled cart 
    except:

        time.sleep(1.5)
        #Check to find out of the shopping cart popup is visible [timer of approx 8 seconds]
        cartWindow = driver.find_element_by_css_selector(".cart-item-modal-content-container")                               #Window to proceed to checkout
        checkoutButton = driver.find_element_by_xpath("/html/body/div[2]/div/div/div[2]/div/div/div/div/div[3]/button[2]")   #Go to cart button
        filledShoppingCart1 = driver.find_element_by_css_selector(".right-menu").text        

    try:
        #While the checout window is visible
        if cartWindow.is_displayed():

            cart = checkoutButton.click()
            print("+++++++++++++++++++++++++++++++++++++")
            print("Heading to login page with: ")

    #In the even that the 'head to cart option disappears'
    except StaleElementReferenceException as Exception:
        
        try: 
            #In the event that the window expires we can go to cart manually
            if int(filledShoppingCart1) >= 1:

                print("Heading to cart manually, rather than through the banner.\n")
                shoppingCart = driver.find_element_by_css_selector(".shopping-cart-button")
                shoppingCart.click()

                #This is the cart page...now we wait a second and proceed 
                time.sleep(2)
                goToCheckout = driver.find_element_by_xpath("/html//div[@id='react-root']//button[@class='css-1cv3jkg ezigbjr0']")
                print(goToCheckout.text)
        except: 
            #Need to add functionality to account for difference in proceedure 
            print("Unsupported functionality at the momment")

    time.sleep(2)

    #CHECK FOR INTERNET CONNECTION 
    #BETTER EXCEPTION AND ERROR CHECKING AND FIXXING
    #CLEAN CODE COMMENTS 
    #CHECK FOR CONFIRMATION PAGE
    #KNOWN BUG - SOME CASES WHEN ADDY IS ALREADY SAVED IN ACCOUNT, 
    #THE WEBSITE WILL AUTOMATICALLY SELECT CHEAPEST SHIPPING OPTION
    #THE SCRIPT DOES NOT ACCOUNT FOR THIS SKIPPED STEP YET
    #KNOWN BUG - IF THE "CHECKOUT BUTTON" DISAPPEARS, THE PROCESS TO CHECKOUT IS 
    #NOT SUPPORTED ATM  

        #errormsgCheck(driver): 
        #MORE THAN 1 "Sorry, you have reached the quantity limit. Please remove an item and try again." Resolution >cart> delete> reopen previous page>reselect 
            #GO TO CART AND REMOVE 
        #UNAVAILABLE "Sorry, the product you have selected is not available at this time."      Resolution > Refresh the page 
        #CANT ADD    "We were unable to load the product data at this time. Please refresh, or try again later." (.text-color-error)
        #PRODUCT OUT OF STOCK <p class="error-code-msg mb4-sm">Sorry, one of the products in your bag is now out of stock. Please select another product or size.<br><span class="error-code ncss-base mb8-sm u-bold">[Code: B6CFCA37 ]</span></p>
            #driver.delete_all_cookies()
            #REFRESH PAGE 
        #ELEMENT NOT PRESENT 
            #CLICK THE CART ICON
            #ELSE QUIT


            #InvalidArgumentException
            #NoSuchAttributeException
            #NoSuchAttributeException
            #TimeoutException
            #ConnectionClosedException


    #Want this to return the driver to main for continued use 
    return driver

#Function used to read and input all delivery information 
def deliveryOptions(driver):

    #Wait for form to load
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, ('#shipping > div > div.ncss-container.pt5-sm'))))
    except:
        time.sleep(1)

    try:
        #Attemp to get element for later use 
        presentAddress = driver.find_element_by_css_selector('.label-extra')
    except:
        try:
            presentAddress = driver.find_element_by_css_selector(".label-extra.ncss-label.pb2-lg.pb3-sm.pl4-sm.pr4-sm.pt2-lg.pt3-sm")
        except:
            pass


    try:
        #Entering name details from the card holder field
        name = lines[10].split(" ")
        firstname = driver.find_element_by_id('firstName')
        firstname.click()
        firstname.send_keys(name[0])

        lastname = driver.find_element_by_id('lastName')
        lastname.click()
        lastname.send_keys(name[1])

        #Entering the address details from config 
        addy = lines[11]
        address = driver.find_element_by_id('search-address-input')
        address.click()
        address.send_keys(addy)
        
        #Wait for the drop down to load
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, ('.suggestion-enter-done'))))

        #Find the suggested address list and click it button.d-sm-b
        suggestions = driver.find_element_by_css_selector('.suggestion-enter-done')
        time.sleep(1)
        #options = suggestions.find_elements_by_tag_name('li')
        options = suggestions.find_elements_by_tag_name('button')
        time.sleep(1)

        #This is done becuase the webpage shores part of the address 
        #in one element and the other half in another
        shortAddy = addy.replace(' ', '')            #Cutting out spaces
        x = len(shortAddy)//2
        shortAddy = shortAddy[:x]    #Cutting the string to remove state and zipcode 
        
        #Moving through address results
        for option in options:
            #We are going to remove all spaces and check for substring
            testString = option.text
            testString = testString.replace(' ', '')

            #Checking for addy in the HTML 
            if shortAddy in testString != -1:
                print("I have selected the correct address: " + str(addy))
                option.click()

        time.sleep(3)

        #Entering email
        email = lines[4]
        emailAddress = driver.find_element_by_css_selector('#email')
        emailAddress.click()
        emailAddress.send_keys(email)

        #Enter the phone number for updates
        phone = lines[6]
        phoneNumber = driver.find_element_by_id('phoneNumber')
        phoneNumber.click()
        phoneNumber.send_keys(phone)

        #Click save and continue 
        savecont = driver.find_element_by_css_selector('#shipping > div > div.ncss-container.pt5-sm > form > div > div > div > div.ncss-col-sm-12.mt2-sm.va-sm-t.ta-sm-r > button')
        savecont.click()
        time.sleep(2)

        print("Saved and proceeding to shipping options \n") 
        return None

    except:
        try:
            #Just display and return to shipping function
            if presentAddress.is_displayed():
                print("Address information is already provided---")
                print(presentAddress.text)
                print("...........................................")
                time.sleep(2)
                return None
        except:
            print("We failed to enter address information\n and it doesnt appear to be present on the page :c\n")
            print("This is a known bug. The site automatically enters the shipping speed thus breaking the bot.")

            try: 
                #This is my attempt to avoid the bug by checking if the 
                #Checkout steps are only 1 and 2 meaning Delivery and Payment because the site lumped Shipping into category 1 
                print("Handling bug...")
                skipShipping = driver.find_element_by_css_selector('#payment > header > h2')
                if '2' in skipShipping.text:
                    return True
            except:
                time.sleep(2222222)
                driver.quit()
                kill()
                quit()


#Small shipping selector function 
def shippingOptions(driver):
   
    #Vital that we wait 
    try:
        WebDriverWait(driver, 3).until(EC.presence_of_element_located((By.CSS_SELECTOR, ('div > .d-sm-tc.pb2-sm.pt2-sm.u-full-width > .ncss-label.pl10-sm.u-full-width'))))
    except:
        try:
            time.sleep(1)        
            savecont = driver.find_element_by_css_selector('#shipping > div > div.ncss-container.pt5-sm > form > div > div > div > div.ncss-col-sm-12.mt2-sm.va-sm-t.ta-sm-r > button')
            savecont.click()
        except:
            pass

    #This will give us the list of shipping options 
    shipping = driver.find_elements_by_css_selector('div > .d-sm-tc.pb2-sm.pt2-sm.u-full-width > .ncss-label.pl10-sm.u-full-width')

    print("Automatically proceeding with the cheapest shipping!")
    
    #Goin through and clicking proceeding with the cheapest
    for count, i in enumerate(shipping):
        if count == 1:
            print(i.text + "                       |")
    print("----------------------------------------------------")

    try: 
        #Attemp to proceed to payment information 
        time.sleep(2)
        paymentButton = driver.find_element_by_css_selector('.continuePaymentBtn')
        paymentButton.click()
    except: 
        #If we failed used js to click button 
        print("Failure in continuing...trying alternate method")
        time.sleep(2)
        pio = WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, (".continuePaymentBtn"))))
        driver.execute_script("arguments[0].click();", pio)
 
    finally:
        print("Saved and proceeding to payment details\n")
        time.sleep(2)
        return

def paymentOptions(driver, guest):

    #Wait for the payment form to load 
    WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, ("[class='ncss-col-sm-12 bg-offwhite border-light-grey p5-sm mb3-sm'"))))
    
    card = lines[6]

    #Navigate to the iframe and wait for them to be clickable 
    cardey = WebDriverWait(driver, 10).until(EC.frame_to_be_available_and_switch_to_it((By.XPATH,'//*[@id="payment"]/div/div[1]/div[2]/div[4]/div/div[1]/div[2]/iframe')))
    cc = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="creditCardNumber"]')))

    #Because the driver was sending keys too fast, the iframe was not recieving the full card number 
    billMe = driver.find_element_by_xpath('//*[@id="creditCardNumber"]')

    #This single line executes JS and inputs card details. I had to use this 
    #because send_keys would mismatch order without fail somehow
    driver.execute_script("arguments[0].value= '{0}';".format(card), billMe)
    time.sleep(.5)
    
    #Sending a single space so that the element formats itself 
    #thus making avaiable to order review button
    billMe.send_keys(' ')

    #Check here for card error message 
    try:
        #Try to see if we got an error message 
        fail = driver.find_element_by_css_selector('.number-error')

        #If error message is displayed, clear and retry 
        while fail.is_displayed():

            print(fail.text)
            billMe.clear()
            #Try to reinput card details 
            try:
                driver.execute_script("arguments[0].value= '{0}';".format(card), billMe)
                time.sleep(.5)
                billMe.send_keys(' ')
            except:
                fail = False 
    except:
        print("Card input failed.\n")

    expire = lines[7]

    expire = expire.replace('/', '')
    expireDate = driver.find_element_by_xpath('//*[@id="expirationDate"]')
    expireDate.click()
    expireDate.send_keys(expire)

    #Check here for Expiration error message 
    secu = lines[8]

    securityCVV = driver.find_element_by_xpath('//*[@id="cvNumber"]')
    securityCVV.click()
    securityCVV.send_keys(secu)

    time.sleep(1)

    print("Card details entered successfully: ")
    print("|Card: {0}|Expiration: {1}|CVV: {2}|\n".format(card, expire, secu))

    #Sending keys to body element to escape from CC iframe information 

    #For guest checkout, it lacks an option 
    if guest == True:
        try: 
            #This will push us into order review 
            cum = driver.find_element_by_tag_name("body")
            cum.send_keys(Keys.TAB)
            cum.send_keys(Keys.TAB)
            cum.send_keys(Keys.TAB)
            cum.send_keys(Keys.TAB)
            cum.send_keys(Keys.ENTER)
        except:
            print("ERROR -> shitty coder")
            driver.quit()
            kill()
            quit()
    #There is an additional option on creditial prompt
    elif guest == False:
        #This will push us into order review 
        try:
            cum = driver.find_element_by_tag_name("body")
            cum.send_keys(Keys.TAB)
            cum.send_keys(Keys.TAB)
            cum.send_keys(Keys.TAB)
            cum.send_keys(Keys.TAB)
            cum.send_keys(Keys.TAB)
            cum.send_keys(Keys.TAB)
            cum.send_keys(Keys.ENTER)
        except:
            print("ERROR -> shitty coder")
            driver.quit()
            kill()
            quit()


    print("Saved and proceeding to order review\n")
    time.sleep(2)


    try:
        #This is to verify we are at the correct screen before clicking place order 
        WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, ("#orderreview .text-color-white"))))
        orderReviewMSG = driver.find_element_by_css_selector("#orderreview .text-color-white")

        if orderReviewMSG.is_displayed():
            print("Successfully arrived at confirmation page!")
        else:
            print("Problem. Not at Order Review Screen")
    except:
        print("HOLD IT ")
        #This is to verify we are at the correct screen before clicking place order 
        WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, ("#orderreview"))))
        orderReviewMSG = driver.find_element_by_css_selector("#orderreview")

        if orderReviewMSG.is_displayed():
            print("Successfully arrived at confirmation page!")
        else:
            print("Problem. Not at Order Review Screen")
        time.sleep(5)



def verifyCheckout(driver):

    print("Waiting to verify order has been placed ... ")
    
    currentURL = driver.current_url
    time.sleep(10)
    
    expectedURL = 'https://www.nike.com/checkout#orderconfirmation'
    currentURL = driver.current_url

    #Looking for a error code 
    try:
        tooManyReq = driver.find_element_by_xpath('//*[@id="checkout-wrapper"]/div/div/div[2]/div/div/div/div/div/div/p/span')
        print("Checkout failed, due to {0} error -> too many purchases too quickly or with the same card".format(tooManyReq.text))
        time.sleep(2222222)
        return False
    except:
        pass

    #Checking to see if we are taken to confirmation screen 
    if expectedURL != currentURL:
        print("Expected url not met! There must be an error.")
        return False 

    else: 
        print("Expect url met! - Additional check - ...")

        try: 
            order = driver.find_element_by_css_selector('.lh24-sm.u-uppercase')
            thanks = driver.find_element_by_css_selector('.fs34-md')

            if order.is_displayed() or thanks.is_displayed():
                print("Confirmed that we the order has been placed. Check screenshot")
                return True
            else: 
                print("That is strange. The expected URL is present but the expected elements are not ")
                return True 
        except:
            print("That is strange. The expected URL is present but the expected elements are not ")
            return True



#This function will manager the cart and checkout process 
def checkoutProcess(driver):

    #Check the internet connection 

    #Retrive fields for login 
    email = lines[4]
    password = lines[5]

    #Reaping our current url for checking 
    siteCheck = False 
    expectedURL = 'https://www.nike.com/checkout'
    expectedURL2 = 'https://www.nike.com/us/en/checkout'
    currentURL = driver.current_url 

    #Enter login info
    try: 

        #Halt until login form is pressent 
        WebDriverWait(driver, 4).until(EC.presence_of_element_located((By.CSS_SELECTOR, '#tunnelPage'))) 
        
        try:
            #Find the email element
            emailField = driver.find_element_by_name("emailAddress")
            print("email: " + str(email))
            emailField.send_keys(email)
        except:
            #Retry if not immediately present 
            print("Waiting for email field to load...")
            time.sleep(1)
            emailField = driver.find_element_by_name("emailAddress")
            print("email: " + str(email))
            emailField.send_keys(email)

        try:
            #Find the password element
            passField = driver.find_element_by_name("password")
            print("password: " + str(password))
            print("+++++++++++++++++++++++++++++++++++++")
            passField.send_keys(password)

        except:
            #Retry if not immediately present 
            print("Waiting for password field to load...")
            time.sleep(1)
            passField = driver.find_element_by_name("password")
            print("password: " + str(password))
            print("+++++++++++++++++++++++++++++++++++++")
            passField.send_keys(password)

        try:
            #Attempting to checkout under member checkout  
            memberCheckout = driver.find_element_by_css_selector("*[value='MEMBER CHECKOUT']")
            memberCheckout.click()
        except:
            #Retry if not immediately present 
            print("Waiting for member checout button to load...")
            time.sleep(1)
            memberCheckout = driver.find_element_by_css_selector("*[value='MEMBER CHECKOUT']")
            memberCheckout.click()

    except: 
        print("Failed checkout caused by NoSuchElementException")
        kill()
        driver.quit()
        quit()
    
    #Rather than checking for a login error message, I am checking to see if the page 
    #changes to one of the accepted checkout pages upon pressing of the membercheckout button
    #if not then we shall proceed to guest checkout 

    #driver.implicitly_wait(2)    
    time.sleep(4)   #THIS IS ESSENTIAL TO AVOID RACE CONDITION CAUSING ERRORS
    #try:
        #Checking for Checkout 
    #    wait = WebDriverWait(driver, 2)
        #checkout_page = wait.until(expected_conditions.presence_of_element_located((By.cssSelector, 'h1.ncss-brand')))
    #    print("Landed on checkout page.")
    #except TimeoutException:
     #   None

    #Update current webpage display 
    currentURL = driver.current_url 
    print("\nWe have arrived at: " + str(currentURL))


    #Some cases, when logging in, I get an error message displyed 
    screen = driver.find_element_by_id('app-container').get_attribute('class')
    #Check to see if the screen is greyed out 
    if screen == 'no-scroll':
        print("\tI detected that there is an alert displayed on screen")
        try:
            #Checking for a particular error message 
            errorDisplay = driver.find_element_by_css_selector('.p6-sm')
            click = driver.find_element_by_tag_name('button')

            #Locate the OK button to bypass 
            if click.text == 'OK':
                click.click()
                print("\tI was able to bypass the message :)")

        except:
            print("\tI failed to bypass the error :c")

    #If we get to this point, our login details have failed, so we will use guest checkout 
    if (currentURL != expectedURL) and (currentURL != expectedURL2):

        print("\tSeems to be an error with login details.")
        print("\tI am not at the anticipated web page.")
        print("\tGoing ahead with guest checkout \\_(ツ)_/\n")

        #Attempt to checkout as a guest 
        try:
            button = driver.find_element_by_id("qa-guest-checkout-mobile")
            button.click()

        #If the element is not clickable wait 
        except:
            button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#qa-guest-checkout')))
            button.click()

        time.sleep(1)
        print("Successfully heading to guest-checkout")
            
        #driver.implicitly_wait(2)
        currentURL = driver.current_url
        
        #Verify that we succeeded in guest checkout page 
        try:    
            assert currentURL == expectedURL, "current url still does not match expected url option 1"
            print("""
                    I have verified that we are in one of the expected checkouts :) 
                    as the current url is {}
                    """.format(currentURL))
            siteCheck = True 
        except:
            assert currentURL == expectedURL2, "current url still does not match expected url option 2"
            print("""
                    I have verified that we are in one of the expected checkouts :) 
                    as the current url is {}
                    """.format(currentURL))
            siteCheck = True 
        finally: 
            #If we still have not gotten to guest checkout, there is a bigger problem 
            if siteCheck == False:
                print("Attempted to checkout as a guest and failed. :c")
                driver.quit()
                kill()
                quit()

        time.sleep(2)
        try:
            #Call to do final input and processing 
            deliveryOptions(driver) 
            shippingOptions(driver)
            paymentOptions(driver, True)

            print("Ready to checkout!")
            try:

                placeOrder = driver.find_element_by_css_selector('.d-lg-ib')
                placeOrder.click()
            except:

                placeOrder = driver.find_element_by_css_selector('#place-order > div > button')
                placeOrder.click()

            time.sleep(2)
            return None

        except:
            print(":C")
            None


    else: 
        #We have arrived at member checkout
        print("\tArrived at membercheckout, no issues...\n")
        time.sleep(2)
        try:
            #Call to do final input and processing
            #This check is here to account for the bug inside the function 
            #that is only present when in membercheckout
            if deliveryOptions(driver) == True:
                pass
            else:
                shippingOptions(driver)
            #shippingOptions(driver)
            paymentOptions(driver, False)

            print("Ready to checkout!")

            try:
                placeOrder = driver.find_element_by_css_selector('.d-lg-ib')
                placeOrder.click()
            except:

                placeOrder = driver.find_element_by_css_selector('#place-order > div > button')
                placeOrder.click()

            time.sleep(2)   
            return None 

        except:
            print(":C")
            None

        
############################
##########  MAIN  ########## 
############################ 
#if __name__ == "__main__":
#    main()
#def main():
 
#Prompt users with the mandatory file            
printConfigPrompt()       
#Wait for user interaction before proceeding 
input()  
#Open the file and read the info                      
lines = []
lines = openfile()             

#Setting time info for countdown 
today = arrow.utcnow()              
finaltime = lines[0]
todaydeadline = today.replace(hour = int(finaltime), minute = int(00), second = int(00))  

#Retrieve the url needed  
url = lines[2]    
sizeList = []       #Used to store the AVAILABLE sizes 
sizeType = -1       #Used to store the sizing STYLE used on site 
sizeME = lines[1]   #Used to store the desired size as int 

print("Url to be used: " + url + "\n")
print("Release time = " + str(todaydeadline)) 
print("Current time = " + str(today))
print("\n")

#Check internet connection before calculating remaining time 
while (checkinternet() == False):   #verify an active connection 
    print("Unable to resolve internet connection\n")
    time.sleep(2)
    checkinternet()
else: 
    pass

#If the shoe has not dropped, wait + buffer 3 seconds
if today < todaydeadline:
    waitUntil(todaydeadline)
    time.sleep(3)
else: 
    pass

 #Handle the initial setup 
driver = openURL(url)   
#Proceed with inputting fields   
checkoutProcess(driver)
#Verify that the order has been placed 
if verifyCheckout(driver) == True:  
#Generate screenshot on success
    shotScreen(driver)  
    print("We have successfully placeed the order.")

else:
    print("There was an issue placing the order.")

driver.quit()
kill()
quit()
