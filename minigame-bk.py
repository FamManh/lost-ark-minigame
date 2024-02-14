# Explain the purpose of the program
# This program is designed to automate the excavation minigame in the game called "Old School Runescape".
# The program will search for the spacebar assets to determine whether the game has started. If the game has started,
# the program will search for the arrow assets to determine the location of the arrow. If the arrow is within the target
# range, the program will press the spacebar to complete the minigame. The program will continue to search for the spacebar
# assets until the user presses the '=' key to quit the program.


import cv2 as cv2
import mss as mss
import numpy as np
from configparser import ConfigParser
from keyboard import is_pressed
from matplotlib import pyplot  as plt
from pyautogui import keyUp, keyDown
from time import sleep
import datetime
import winsound
import chime
chime.theme('zelda')


# chime.success()
# chime.warning()
# chime.error()
# chime.info()
# chime.notify_exceptions()


DEBUG_ENABLED = False

config = ConfigParser()
config.read('config.ini')

starting_delay_seconds = float(config["DEFAULT"]['starting_delay_seconds'])
arrow_middle_offset = float(config["DEFAULT"]['arrow_middle_offset'])
target_range_left_offset = float(config["DEFAULT"]['target_range_left_offset'])
target_range_right_offset = float(config["DEFAULT"]['target_range_right_offset'])

MINIGAME_ARROW = cv2.imread("./assets/minigame_arrow.png", 0)
NORMAL_SACEBAR = cv2.imread("./assets/normal_spacebar1.png", 0)
GLOW_SPACEBAR = cv2.imread("./assets/glow_spacebar.png", 0)

print("""
██      ██████  ███████ ████████      █████  ██████  ██   ██ 
██     ██    ██ ██         ██        ██   ██ ██   ██ ██  ██  
██     ██    ██ ███████    ██        ███████ ██████  █████   
██     ██    ██      ██    ██        ██   ██ ██   ██ ██  ██  
███████ ██████  ███████    ██        ██   ██ ██   ██ ██   ██                                                                                                                                                
""")
print("Program has started... looking for excavation minigames. Press the '=' key to quit anytime!")

def annoy():     
    # winsound.Beep(100, 200)     
    chime.info()

    # chime.success()    

def automate_space() -> None:
    keyDown('space')
    # sleep(0.01)
    keyUp('space')

def search_targets() -> list:
    """
    Search for the target zones within the excavation bar by returning the x-ranges
    for each individual zones. Add offsets to account for latency between the program and
    the game. 
    """

    monitor = {"left": 740, "top": 720, "width": 420, "height": 20}
    # output = "sct-{top}x{left}_{width}x{height}.png".format(**monitor)

    excavation_bar = sct.grab(monitor)
    excavation_bar_rgb = np.array(excavation_bar)
    excavation_bar_gray = cv2.cvtColor(excavation_bar_rgb, cv2.COLOR_BGR2GRAY)

    _, bar_bw = cv2.threshold(excavation_bar_gray, 70, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(bar_bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    targets = []
    for target in contours:
        timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        monitor_str = "monitor-{left}x{top}_{width}x{height}".format(**monitor)
        output = "target-{monitor}_{timestamp}.png".format(monitor=monitor_str, timestamp=timestamp_str)
        # mss.tools.to_png(excavation_bar.rgb, excavation_bar.size, output=output)

        if cv2.contourArea(target) >= 100:
            M = cv2.moments(target)
            x = int(M['m10']/M['m00'])
            targets.append(
                [
                    x-target_range_left_offset, 
                    x+target_range_right_offset
                ]
            )
    return targets

targets = []
searched = False
count = 1
while is_pressed('=') == False:
    count += 1
    with mss.mss() as sct:
        
        monitor = {"left": 740, "top": 720, "width": 420, "height": 150}
        spacebar_img_rgb = np.array(sct.grab(monitor))
        spacebar_img_gray = cv2.cvtColor(spacebar_img_rgb, cv2.COLOR_BGR2GRAY)


        # Determine whether the game have started  by searching for the spacebar assets.
        normal_res = cv2.matchTemplate(spacebar_img_gray, NORMAL_SACEBAR, cv2.TM_CCOEFF_NORMED)
        glow_res = cv2.matchTemplate(spacebar_img_gray, GLOW_SPACEBAR, cv2.TM_CCOEFF_NORMED)
        # print(normal_res, glow_res)

        _, n_confidence, _, max_loc = cv2.minMaxLoc(normal_res)
        _, g_confidence, _, max_loc = cv2.minMaxLoc(glow_res)

        if n_confidence >= 0.8 or g_confidence >= 0.8:
            # Format the monitor and timestamp
            monitor_str = "monitor-{left}x{top}_{width}x{height}".format(**monitor)

            # Combine the monitor and timestamp to create the output filename
            # output = "sct-{top}x{left}_{width}x{height}x{}.png".format(**monitor)
            timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            output = "sct-{monitor}_{timestamp}.png".format(monitor=monitor_str, timestamp=timestamp_str)
            sct_img = sct.grab(monitor)

            # mss.tools.to_png(sct_img.rgb, sct_img.size, output=output)

        if n_confidence >= 0.8 or g_confidence >= 0.8:
            print("Game has started...", n_confidence, g_confidence)
            # Let the game load before we do anything
            if not targets:
                print("Game has started... waiting for the game to load")
                sleep(starting_delay_seconds)

            arrow_monitor = {"left": 740, "top": 740, "width": 420, "height": 30}
            arrow_rgb = np.array(sct.grab(arrow_monitor))
            arrow_gray = cv2.cvtColor(arrow_rgb, cv2.COLOR_BGR2GRAY)
            arrow_monitor_str = "monitor-{left}x{top}_{width}x{height}".format(**monitor)

            # save arrow_gray to image
            arrow_gray_output = "sct-arrow-gray-{monitor}_{timestamp}.png".format(monitor=arrow_monitor_str, timestamp=timestamp_str)


            if not searched:
                searched = True
                targets = search_targets()
                print("Targets found!", targets)

            arrow_res = cv2.matchTemplate(arrow_gray, MINIGAME_ARROW, cv2.TM_CCOEFF_NORMED)
            # print('arrow_res', arrow_res)
            _, arrow_confidence, _, arrow_loc = cv2.minMaxLoc(arrow_res)
            # print('arrow_confidence', arrow_confidence, arrow_loc)

            location = arrow_loc[0] + arrow_middle_offset
            if arrow_confidence >= 0.75:

                # Offset to the middle of arrow coordinate.
                location = arrow_loc[0] + arrow_middle_offset
                # print('location', location)
                for idx, target in enumerate(targets):
                    print('COUNT: ', count, ' ====== target', target, ' .location', location)
                    if location <= target[1] and location >= target[0]:
                        cv2.imwrite(arrow_gray_output, arrow_gray)
                        annoy()
                        targets.remove(targets[idx])
                        automate_space()
                        print("PRESSING SPACE\n")
        else:
            targets = []
            searched = False
