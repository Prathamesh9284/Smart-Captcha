import pyautogui
import time

time.sleep(3)

username_coords = (869, 380)
password_coords = (870, 458)
submit_coords = (937, 534)

pyautogui.moveTo(username_coords[0], username_coords[1], duration=1)
pyautogui.click()
pyautogui.write('your_username', interval= 0.1)

pyautogui.moveTo(password_coords[0], password_coords[1], duration=0.5)
pyautogui.click()
pyautogui.write('your_password', interval= 0.1)

pyautogui.moveTo(submit_coords[0], submit_coords[1], duration=0.75)
pyautogui.click()
