import pygetwindow as gw
import pyautogui
import time


def capture_window(window_title,output_folder,step):
    """对指定标题的窗口进行截图"""
    try:
        # 获取所有窗口
        windows = gw.getAllTitles()

        # 检查是否存在指定标题的窗口
        if window_title in windows:
            window = gw.getWindowsWithTitle(window_title)[0]  # 获取窗口
            window.activate()  # 激活窗口
            time.sleep(1)  # 等待窗口激活

            # 截图
            screenshot = pyautogui.screenshot()
            screenshot.save(f"{output_folder}/{window_title}_screenshot_{step}.png")  # 保存截图
            print(f"{window_title} 窗口截图已保存。")
        else:
            print(f"未找到窗口: {window_title}")
    except Exception as e:
        print(f"发生错误: {e}")