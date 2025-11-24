'''简简单单的截图工具'''

import cv2
import time
from whimbox.interaction.interaction_core import itt
from whimbox.common.path_lib import *
from whimbox.common.utils.img_utils import process_with_hsv_limit
os.startfile(ROOT_PATH + '\\' + "..\\tools\\snapshot")
while 1:
    input('enter to capture') 
    # time.sleep(0.2)
    cap = itt.capture()
    # cap = cv2.cvtColor(cap, cv2.COLOR_BGRA2GRAY)
    # _, cap = cv2.threshold(cap, 210, 255, cv2.THRESH_BINARY)
    # lower = [0, 0, 175]
    # upper = [20, 255, 255]
    # cap = process_with_hsv_limit(cap, lower, upper)
    cv2.imwrite(ROOT_PATH + '\\' + "..\\tools\\snapshot\\" + str(time.time()) + ".png", cap) # type: ignore