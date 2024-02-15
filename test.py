import time
import pyautogui
import pydirectinput

# for i in range(10):
#     keyDown('space')
#     sleep(0.01)
#     keyUp('space')
#     sleep(1)

time.sleep(5) 

pydirectinput.typewrite("Hello world") 
time.sleep(0.5) 

pydirectinput.press('space')
time.sleep(1) 

pydirectinput.typewrite("Hello world") 
