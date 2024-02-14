import cv2
import mss
import numpy as np
from configparser import ConfigParser
from keyboard import is_pressed
from pyautogui import keyDown, keyUp, press
from time import sleep
import datetime
import chime

# Set up chime
chime.theme('zelda')

# Load configuration
config = ConfigParser()
config.read('config.ini')

# Configuration parameters
starting_delay_seconds = float(config["DEFAULT"]['starting_delay_seconds'])
arrow_middle_offset = float(config["DEFAULT"]['arrow_middle_offset'])
target_range_left_offset = float(config["DEFAULT"]['target_range_left_offset'])
target_range_right_offset = float(config["DEFAULT"]['target_range_right_offset'])
debug = config.getboolean("DEFAULT", "debug")
take_screen_shot = config.getboolean("DEFAULT", "take_screen_shot")

# Load images
MINIGAME_ARROW = cv2.imread("./assets/minigame_arrow.png", 0)
NORMAL_SPACEBAR = cv2.imread("./assets/normal_spacebar1.png", 0)
GLOW_SPACEBAR = cv2.imread("./assets/glow_spacebar.png", 0)

# Print banner
print("""
██      ██████  ███████ ████████      █████  ██████  ██   ██ 
██     ██    ██ ██         ██        ██   ██ ██   ██ ██  ██  
██     ██    ██ ███████    ██        ███████ ██████  █████   
██     ██    ██      ██    ██        ██   ██ ██   ██ ██  ██  
███████ ██████  ███████    ██        ██   ██ ██   ██ ██   ██                                                                                                                                                
""")
print("Program has started... looking for excavation minigames. Press the '=' key to quit anytime!")

def annoy():
    """Play an annoying sound."""
    chime.info()

def automate_space():
    """Press and release the spacebar."""
    # keyDown('space')
    # sleep(0.01)
    # keyUp('space')
    press('space')
    annoy()


def search_targets(sct):
    """Search for target zones within the excavation bar."""
    monitor = {"left": 740, "top": 720, "width": 420, "height": 20}
    excavation_bar = sct.grab(monitor)
    excavation_bar_rgb = np.array(excavation_bar)
    excavation_bar_gray = cv2.cvtColor(excavation_bar_rgb, cv2.COLOR_BGR2GRAY)
    _, bar_bw = cv2.threshold(excavation_bar_gray, 70, 255, cv2.THRESH_BINARY)
    contours, _ = cv2.findContours(bar_bw, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    targets = []
    for target in contours:
        if cv2.contourArea(target) >= 100:
            M = cv2.moments(target)
            x = int(M['m10'] / M['m00'])
            targets.append([x - target_range_left_offset, x + target_range_right_offset])
    return targets

def main():
    """Main function to control the automation."""
    targets = []
    searched = False
    count = 1
    while not is_pressed('='):
        count += 1
        with mss.mss() as sct:
            # Grab the screen image
            monitor = {"left": 740, "top": 720, "width": 420, "height": 150}
            spacebar_img_rgb = np.array(sct.grab(monitor))
            spacebar_img_gray = cv2.cvtColor(spacebar_img_rgb, cv2.COLOR_BGR2GRAY)

            # Check if the game has started
            normal_res = cv2.matchTemplate(spacebar_img_gray, NORMAL_SPACEBAR, cv2.TM_CCOEFF_NORMED)
            glow_res = cv2.matchTemplate(spacebar_img_gray, GLOW_SPACEBAR, cv2.TM_CCOEFF_NORMED)
            _, n_confidence, _, _ = cv2.minMaxLoc(normal_res)
            _, g_confidence, _, _ = cv2.minMaxLoc(glow_res)

            if n_confidence >= 0.8 or g_confidence >= 0.8:
                # Game started
                if not targets:
                    sleep(starting_delay_seconds)

                # Search for arrow and targets
                arrow_monitor = {"left": 740, "top": 740, "width": 420, "height": 30}
                arrow_rgb = np.array(sct.grab(arrow_monitor))
                arrow_gray = cv2.cvtColor(arrow_rgb, cv2.COLOR_BGR2GRAY)

                timestamp_str = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
                arrow_monitor_str = "monitor-{left}x{top}_{width}x{height}".format(**monitor)
                arrow_gray_output = "sct-arrow-gray-{monitor}_{timestamp}.png".format(monitor=arrow_monitor_str, timestamp=timestamp_str)


                if not searched:
                    searched = True
                    targets = search_targets(sct)
                    if debug: print("Targets found!", targets)

                arrow_res = cv2.matchTemplate(arrow_gray, MINIGAME_ARROW, cv2.TM_CCOEFF_NORMED)
                _, arrow_confidence, _, arrow_loc = cv2.minMaxLoc(arrow_res)

                if arrow_confidence >= 0.75:
                    location = arrow_loc[0] + arrow_middle_offset
                    for idx, target in enumerate(targets):
                        if debug: print('Target', target, '. location', location)
                        if location <= target[1] and location >= target[0]:
                            if take_screen_shot: cv2.imwrite(arrow_gray_output, arrow_gray)
                            targets.remove(targets[idx])
                            automate_space()
                            print("PRESSING SPACE\n")
            else:
                targets = []
                searched = False

if __name__ == "__main__":
    main()