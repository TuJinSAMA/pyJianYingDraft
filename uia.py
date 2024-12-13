import subprocess
from time import sleep

import pyautogui


def export():
    app_name = f'/Applications/VideoFusion-macOS.app'
    subprocess.Popen(['open', app_name])
    sleep(5)
    # 使用 AppleScript 检查窗口
    script = '''
    tell application "System Events"
        set appRunning to (name of processes) contains "VideoFusion-macOS"
    end tell
    return appRunning
    '''
    try:

        app_running = subprocess.check_output(['osascript', '-e', script])

        if app_running.strip() != b'true':
            raise RuntimeError("没有成功启动剪映")
        screenWidth, screenHeight = pyautogui.size()
        print(screenWidth, screenHeight)
        currentMouseX, currentMouseY = pyautogui.position()
        print(currentMouseX, currentMouseY)
        pyautogui.click(x=-1168, y=435)
        sleep(5)
        pyautogui.click(x=-158, y=-81)
        sleep(3)
        pyautogui.click(x=-704, y=730)
        print(pyautogui.onScreen(currentMouseX, currentMouseY))
    except subprocess.CalledProcessError:
        print("检查应用状态时发生错误。")
    except Exception as e:
        print(f"导出草稿时发生错误: {e}")


if __name__ == '__main__':
    export()
