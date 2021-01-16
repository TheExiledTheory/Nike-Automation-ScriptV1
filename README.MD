# Description: 

**Base URL of SNKRS web app https://www.nike.com/launch?s=upcoming**

Launch the script before the timed drop is set to release or after if necessary. The program will wait and after a few seconds of it becoming available it will launch a chrome/chromium browser and navigate to the site provided in the config file. It will then execute size selection and navigate to the cart and input login details along with shipping details and credit card information. If successful, it will screenshot the confitmation page and save it to the root directory of the script.

## Last successful test: 01/12/2021
    Distro Debian GNU/Linux 9
    Selenium 4.0.0.a1
    Python 3.8.6
    Chromium 83.0.4103.116
    Chromedriver 83.0.4103.14

# Instructions: 

    1. Check your current installation of Python3/Pip3 and Chrome and ChromeDriver:
        In terminal type:
            "python3 -V" 
            "pip3 --version"
            "chromium-browser --version" or "google-chrome --version"
            "chromedriver --version"

    Note: If you need to install GoogleChrome/ChromeDriver, it can be done so at the following

    Note: The version of GoogleChrome/Chromium need to match the the chrome
            "https://sites.google.com/a/chromium.org/chromedriver/downloads"  
            "https://www.slimjet.com/chrome/google-chrome-old-version.php"

    If you need to unzip/untar the folder after download use: 
            "sudo unzip filename" or "sudo tar -zxvf filename"

    2. Once you have everything downloaded you need to install and give permissions:
        Move the chrome .deb file to the root folder for this script:
            "sudo mv filename foldername"
        Depackage Google Chrome with:
            "dpkg -i filename" 
        Give the Chrome Driver appropriate permissions with:
            "sudo chmod +x filename" 

        Copy the Chrome Drive to /usr/bin and give it permissions with:
            "sudo cp filename /usr/bin/"
            "sudo chmod +x /usr/bin/filename"
        You can also use the following command just to be certain:
            "export PATH=$PATH:/path-to-extracted-file/" in terminal so tools can find it 

    3. Additional resources:
        Included in this repo are three pdf files that should aid you in getting setup, should the need araise...

    4. To run the script, use the following command:
            "sudo python3 filename.py"

    5. If you need to install any PYPI modules use:
            "pip3 install pause pyvirtualdisplay selenium arrow psutil time" etc.

If at any point the program crashes. The browser may not be closed correctly leaving a zombie in the process list. 
You can find them buy typing "top" and looking for "zombies" in the stats. You can see all the defunct or "zombie" 
processes by typing "ps -elf | grep Z" or just type "pgrep chrome" or "pgrep chromium" into terminal. 
To kill them use "kill $(pgrep chrome)" "kill $(pgrep chromium) or just type "kill PPID" if you want to kill a single specific process.

Zombie processes are caused by the parent program (script) being closed before it can read the status of the child process (web browser). The zombie process is infact dead so it is not consuming resources, however its entry from the OS process table. This is not bad but after a large enough number of these are left, you can run out of entries in the table.



## TO DO: 
    1. Multithreading to support multiple sessions/accounts/proxies 
    2. Support for multiple accounts 
    3. Support for proxies  
    4. Add a GUI interface 
    5. Add support for checkout through cart 
    6. Add a SMTP support to verify confirmation email 
    7. Add support for solving captcha (Not required atm)  
    8. Account for multiple size selections of a single shoe on a given page!
    
## DEPENDENCIES: 
    PYPI Modules                [Arrow, Selenium, Time, Psutil, Datetime, etc...]
    Chrome webdriver            [That corresponds to your version of installed Chrome]
    Python 3+                   [This script is written in Python 3]
    Linux flavor of choice      [This can also be used on Windows but the included files are for Linux] 

_If Nike updates any page elements that range from the size selection to the checkout page, the element variable will need to be updated to reflect that_
   
