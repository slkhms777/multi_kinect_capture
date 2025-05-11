import threading
import time
import keyboard

from .multi_kinect_manager import MultiKinectManager
from .fpv_manager import FPVCamera

class MultiViewManager:
    def __init__(self, 
                 base_output="output", 
                 fpv_output="output/fpv", 
                 duration=10, 
                 fps=30, 
                 max_frames=None):
        self.kinect_manager = MultiKinectManager(
            base_output_folder=base_output,
            duration=duration,
            fps=fps,
            max_frames=max_frames
        )
        self.fpv_camera = FPVCamera(
            camera_id=0,
            output_folder=fpv_output,
            duration=duration,
            fps=fps,
            max_frames=max_frames
        )

    def start_all_capture(self):
        # Kinect和FPV分别用线程启动，保证同步
        kinect_thread = threading.Thread(target=self.kinect_manager.start_synchronized_capture)
        fpv_thread = threading.Thread(target=self.fpv_camera.capture)
        kinect_thread.start()
        fpv_thread.start()
        kinect_thread.join()
        fpv_thread.join()
        print("多视角采集完成")

    def wait_and_listen(self):
        print("按下A键开始多视角同步采集...")
        keyboard.wait('a')
        print("开始采集！")
        self.start_all_capture()

# 用法示例（可在主程序中调用）
if __name__ == "__main__":
    manager = MultiViewManager(
        base_output="output",
        fpv_output="output/fpv",
        duration=10,
        fps=30,
        max_frames=None
    )
    manager.wait_and_listen()