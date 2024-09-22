import time
import pyautogui

def move_forward(duration):
    print(f"Moving forward for {duration} seconds")
    pyautogui.keyDown('w')
    time.sleep(duration)  #持续duration秒
    pyautogui.keyUp('w')

def mine(duration):
    print("Mining")
    pyautogui.mouseDown(button='left')  # 按下左键
    time.sleep(duration)      #预设，持续5秒
    pyautogui.mouseUp(button='left')

def turn(x, y):
    print(f"Turning with mouse by {x} pixels horizontally and {y} pixels vertically")
    pyautogui.move(x, y) #正数向右向下，负数向左向上

def turn_and_move_forward(duration, x, y):
    turn(x, y)
    move_forward(duration)
