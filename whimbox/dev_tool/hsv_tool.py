'''可视化的HSV阈值调节工具'''
import cv2  
import numpy as np  
from whimbox.common.utils.img_utils import *
from whimbox.ui.ui_assets import *

# 滑动条的回调函数，获取滑动条位置处的值  
def empty(a):  
    h_min = cv2.getTrackbarPos("Hue Min", "TrackBars")  
    h_max = cv2.getTrackbarPos("Hue Max", "TrackBars")  
    s_min = cv2.getTrackbarPos("Sat Min", "TrackBars")  
    s_max = cv2.getTrackbarPos("Sat Max", "TrackBars")  
    v_min = cv2.getTrackbarPos("Val Min", "TrackBars")  
    v_max = cv2.getTrackbarPos("Val Max", "TrackBars")  
    # print(h_min, h_max, s_min, s_max, v_min, v_max)  
    return h_min, h_max, s_min, s_max, v_min, v_max  
    
# 创建一个窗口，放置6个滑动条  
cv2.namedWindow("TrackBars")  
cv2.resizeWindow("TrackBars", 640, 300)  
init_data = {
    'h_min': 0,
    'h_max': 179,
    's_min': 0,
    's_max': 25,
    'v_min': 240,
    'v_max': 255,
}
cv2.createTrackbar("Hue Min", "TrackBars", init_data['h_min'], 179, empty)  
cv2.createTrackbar("Hue Max", "TrackBars", init_data["h_max"], 179, empty)  
cv2.createTrackbar("Sat Min", "TrackBars", init_data['s_min'], 255, empty)  
cv2.createTrackbar("Sat Max", "TrackBars", init_data["s_max"], 255, empty)  
cv2.createTrackbar("Val Min", "TrackBars", init_data['v_min'], 255, empty)  
cv2.createTrackbar("Val Max", "TrackBars", init_data['v_max'], 255, empty)  

if __name__ == "__main__" and True:    
    from whimbox.common.path_lib import *
    # file_path = "D:\\workspaces\\python\\Whimbox\\whimbox\\assets\\imgs\\Windows\\General\\AreaClickSkip.png"
    # img = cv2.imread(file_path)
    img =cv2.imread(os.path.join(ROOT_PATH, "..", "tools", "snapshot", "1763610947.9422815.png"))
    img = cv2.cvtColor(img, cv2.COLOR_BGRA2GRAY)
    lower = 230
    upper = 255
    # mask = process_with_hsv_limit(img, lower, upper)
    _, img = cv2.threshold(img, lower, upper, cv2.THRESH_BINARY)
    cv2.imshow("img_gray", img)
    cv2.waitKey(0)
    cv2.imwrite(os.path.join(ROOT_PATH, "..", "tools", "snapshot", "1763610947.9422815_gray.png"), img)

if __name__ == "__main__" and False:
    from whimbox.interaction.interaction_core import itt
    from whimbox.ui.ui_assets import *
    from whimbox.common.utils.posi_utils import *
    from whimbox.common.path_lib import *
    # org = cv2.imread(os.path.join(ROOT_PATH, "..", "tools", "snapshot", "1763610947.9422815.png"))
    # org = cv2.imread("D:\\workspaces\\python\\Whimbox\\whimbox\\assets\\imgs\\Windows\\General\\AreaClickSkip.png")
    # img = org.copy()
    while True:
        # img = crop(org, AreaClickSkip.position)
        img = itt.capture()
        # 调用回调函数，获取滑动条的值  
        h_min, h_max, s_min, s_max, v_min, v_max = empty(0)  
        lower = np.array([h_min, s_min, v_min])  
        upper = np.array([h_max, s_max, v_max])  
        # lower = [0, 80, 240]
        # upper = [30, 110, 255]
        mask = process_with_hsv_limit(img, lower, upper)
        # px_count = cv2.countNonZero(mask)
        # print(f"px_count: {px_count}")
        # if px_count > 200:
            # print("get!")
        cv2.imshow("mask", mask)
        cv2.waitKey(1)

if __name__ == "__main__" and False:
    from whimbox.interaction.interaction_core import itt
    from whimbox.ui.ui_assets import *
    from whimbox.common.utils.posi_utils import *
    from whimbox.common.path_lib import *
    while True:
        img = itt.capture(AreaAbilityButton.position)
        # img = cv2.imread(os.path.join(ROOT_PATH, "tools", "snapshot", "1759020866.2830987.png"))
        # img = crop(img, AreaMaterialTrackNear.position)
        img_copy = img.copy()
        imgHSV = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)  
        # 调用回调函数，获取滑动条的值  
        h_min, h_max, s_min, s_max, v_min, v_max = empty(0)  
        lower = np.array([h_min, s_min, v_min])  
        upper = np.array([h_max, s_max, v_max])  
        # lower = np.array([17, 140, 130])
        # upper = np.array([20, 180, 200])
        mask = cv2.inRange(imgHSV, lower, upper)
        cv2.imshow("mask", mask)
        cv2.waitKey(1)

        circles = cv2.HoughCircles(
            mask,
            cv2.HOUGH_GRADIENT,
            dp=1.2,          # 累加器分辨率（可调 1.0~1.5）
            minDist=22,      # 圆心最小间距，建议≈ 2*minRadius - 些许
            param1=120,      # Canny高阈值
            param2=10,       # 累加器阈值，越小越容易出圆（可调 8~18）
            minRadius=16,
            maxRadius=18
        )

        if circles is not None:
            circles = np.uint16(np.around(circles[0, :]))
            for (x, y, r) in circles:
                # 确保转换为 Python int 类型
                cv2.circle(img_copy, (int(x), int(y)), int(r), (0, 0, 255), 2)
                cv2.circle(img_copy, (int(x), int(y)), 2, (0, 0, 255), 3)
        cv2.imshow("img", img_copy)
        cv2.waitKey(1)

        # cv2.imshow("Mask", mask) 
        # key =cv2.waitKey(1)
        # if key == 27:  # ESC键退出
        #     img = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR)
        #     save_image(img, f'D:\\workspaces\\python\\Whimbox\\tools\\hsv_tool\\jump2.png')
        #     break
    
if __name__ == "__main__" and False:
    from whimbox.interaction.interaction_core import itt
    from whimbox.ui.ui_assets import *
    from whimbox.common.utils.posi_utils import *
    from whimbox.map.map import *
    while True:
        cap = itt.capture()
        minimap_img = nikki_map._get_minimap(cap, MINIMAP_RADIUS)
        lower = [13, 90, 160]
        upper = [15, 200, 255]
        minimap_hsv = process_with_hsv_limit(minimap_img, lower, upper)
        minimap_blur = cv2.GaussianBlur(minimap_hsv, (3, 3), 1)
        cv2.imshow("minimap_blur", minimap_blur)
        cv2.waitKey(1)
        circles = cv2.HoughCircles(
            minimap_blur,
            cv2.HOUGH_GRADIENT,
            dp=1,          # 累加器分辨率（可调 1.0~1.5）
            minDist=10,      # 圆心最小间距，建议≈ 2*minRadius - 些许
            param1=100,      # Canny高阈值
            param2=9,       # 累加器阈值，越小越容易出圆（可调 8~18）
            minRadius=14,
            maxRadius=16
        )
        if circles is not None:
            for circle in circles[0, :]:
                x, y, r = np.uint16(np.around(circle))
                cv2.circle(minimap_img, (x, y), r, (0, 0, 255), 2)
                cv2.circle(minimap_img, (x, y), 2, (0, 0, 255), 3)
            cv2.imshow("minimap_img", minimap_img)
            cv2.waitKey(1)