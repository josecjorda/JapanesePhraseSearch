#Make sure bing chat allows page context
#Using Seleinum to break down a text in Japanese using bing chat on a pdf, google translate
#Using autogui for being able to click outside of html elements
#Only works on second monitor
#pdf stored on my pc I supposed I could just add it to here but don't want to for now since I'm adjusting my notes
import cv2
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import pyautogui
import pyperclip
from PIL import ImageGrab
from functools import partial
import time
import tkinter as tk
from tkinter import ttk
import os, sys
#Used to work search all monitors
ImageGrab.grab = partial(ImageGrab.grab, all_screens=True)

#Selenium (windows, tabs, and html) commands
#Time to wait for next command is given at end of function
#-----------------------------------------------------
#Set up for browser window and tabs
def browserSetup(trans_file):
    #Create browser window
    driver = webdriver.Edge()

    #Open pdf tab
    driver.get(trans_file)
    pdf = driver.current_window_handle
    driver.implicitly_wait(30) #Gives time to load

    #open google translate tab
    driver.switch_to.new_window('tab')
    driver.get("https://translate.google.com/?sl=ja&tl=en&op=translate")
    gt = driver.current_window_handle

    #open deepL tab
    driver.switch_to.new_window('tab')
    driver.get("https://www.deepl.com/translator#ja/en/")
    deepL = driver.current_window_handle

    driver.implicitly_wait(30) #Gives time to load

    return driver, pdf, gt, deepL

#Open browser on second monitor
def openOnSecondMonitor(driver, sm_loc):
    try:
        driver.minimize_window()
        driver.set_window_position(sm_loc[0], sm_loc[1])
        driver.maximize_window()
    except:
        driver.maximize_window()
        driver.minimize_window()
        driver.set_window_position(sm_loc[0], sm_loc[1])
        driver.maximize_window()
    time.sleep(5) #Give time to load
    return

#Inputs phrase into Google Translate
def inputGoogleTranslate(driver, phrase, handle):
    #Switch to google translate tab
    driver.switch_to.window(handle)
    #Input phrase
    input_box = driver.find_element(By.CLASS_NAME ,"er8xn")
    input_box.clear()
    input_box.send_keys(phrase)
    time.sleep(5) #Give time to load
    #Get translation
    #translation = driver.find_element_by_class_name("tlid-translation")
    #print(translation.text)
    return

#-----------------------------------------------------
#Autogui (outside of html) commands
#Time to wait for next command is given at end of function
#-----------------------------------------------------
#Opens Bing Chat Side Bar
def openBingChat(driver):
    bing_icon_location = pyautogui.locateOnScreen(resource_path("images/bing_icon.PNG"))
    time.sleep(1) #Give time to load
    pyautogui.click(bing_icon_location, button='left')
    time.sleep(7) #Give time to load
    #Make sure bing chat is in precise mode
    preciseBingMode(driver)

#Sets bing chat to precise mode
def preciseBingMode(driver):
    bing_icon_location = pyautogui.locateOnScreen(resource_path("images/preciseBingMode.PNG"), confidence=0.8)
    time.sleep(1) #Give time to load
    pyautogui.click(bing_icon_location, button='left')
    time.sleep(5) #Give time to load

#Clears Bing Chat
def clearBingChat(driver):
    bing_icon_location = pyautogui.locateOnScreen(resource_path("images/clearChat.PNG"))
    time.sleep(5) #Give time to load
    pyautogui.click(bing_icon_location, button='left')
    time.sleep(5) #Give time to load
    pass

#Inputs phrase into Bing Chat
def inputBingChat(driver, phrase, handle, prompt):
    msg = prompt + phrase
    pyperclip.copy(msg) #pyautogui doesn't work with japanese so a workaround is to use pyperclip and paste into text box
    driver.switch_to.window(handle)
    bing_icon_location = pyautogui.locateOnScreen(resource_path("images/bingChat.PNG"))
    pyautogui.click(bing_icon_location, button='left')
    time.sleep(1) #Give time to load
    pyautogui.hotkey('ctrl', 'v')
    time.sleep(1) #Give time to load
    pyautogui.press('enter')
    return

#Inputs phrase into deepL
def inputDeepL(driver, phrase, handle):
    #Switch to deepL tab
    driver.switch_to.window(handle)

    #Input phrase
    input_box = driver.find_element(By.CLASS_NAME ,"lmt__textarea")
    input_box.send_keys(Keys.CONTROL, "a"); input_box.send_keys(Keys.DELETE) #Clear not working so this is a work around
    input_box.send_keys(phrase)
    #input_box.send_keys(phrase)
    time.sleep(5) #Give time to load
    #Get translation
    #translation = driver.find_element_by_class_name("lmt__target_textarea")
    #print(translation.text)
    return


#-----------------------------------------------------
#Tkinter (gui) commands
#Time to wait for next command is given at end of function
#-----------------------------------------------------
def guiSetup(window, driver, pdf, gt, deepL, sm_loc, bing_prompt):
    window.title("Japanese Phrase Search")
    window. geometry("500x500")

    #ttk label
    label_string = tk.StringVar(value = "Enter Japanese Phrase")
    label = ttk.Label(window, textvariable=label_string)
    label.pack()

    #ttk entry
    text = tk.StringVar()
    entry = ttk.Entry(window, textvariable=text)
    entry.pack()
    #Used to refresh bing chat every 20 phrases
    count = [0] # Need to make it immutable so it can just be changed in function

    #ttk button
    button = ttk.Button(window, text="Enter", command = lambda: inputPhrase(driver, pdf, gt, deepL, sm_loc, bing_prompt, count, text, label_string)) #lambda lets it run only once its pressed
    button.pack()

#Input Phrase
def inputPhrase(driver, pdf, gt, deepL, sm_loc, bing_prompt, count, text, label_string):
    phrase = text.get()
    if count[0] <= 20: #Refreshes bing chat every 20 phrases
        #Input
        openOnSecondMonitor(driver, sm_loc)
        inputBingChat(driver, phrase, pdf, bing_prompt)
        inputGoogleTranslate(driver, phrase, gt)
        inputDeepL(driver, phrase, deepL)
    else:
        #Reset
        count[0] = 0
        clearBingChat(driver)
        #Input
        openOnSecondMonitor(driver, sm_loc)
        inputBingChat(driver, phrase, pdf, bing_prompt)
        inputGoogleTranslate(driver, phrase, gt)
        inputDeepL(driver, phrase, deepL)
    time.sleep(15) #Give time to load
    #label_string.set("Enter Japanese Phrase")
    count[0] += 1
    text.set("")

#-----------------------------------------------------

#Pyinstaller For relative paths in single file
#-----------------------------------------------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)
#-----------------------------------------------------
def main():
    #Initializations
    bing_prompt = "Translate the following spoken phrase to english and explain each component used using bullet points: "
    # bing_prompt = "Translate the following spoken phrase to english and explain each component used using bullet points. Include the phonetics: "
    sm_loc = (2000, 0) #Second monitor location
    trans_file = "D:\The_Stuff\Focus\Everything\Extra\Attachments\Cure Dolly Textbook.pdf" #Pdf describes grammer of Japanese. Useful for edge to base answers off it
    #Creates browser window and tab handles
    driver, pdf, gt, deepL = browserSetup(trans_file)

    #Makes sure browser is open on second monitor
    openOnSecondMonitor(driver, sm_loc)
    #Open to pdf window and wait for loading
    driver.switch_to.window(pdf)
    #Opens bing sidbar
    openBingChat(driver)

    #Gui set up
    #Create window
    window = tk.Tk()
    #Set up window
    count = 0 #Used to refresh bing chat
    guiSetup(window, driver, pdf, gt, deepL, sm_loc, bing_prompt)
    #Loop to enter Japanese Phrases
    window.mainloop()
    
if __name__=="__main__":
    main()

