import os
import time
import argparse
import threading
import json
from datetime import datetime
from pyk4a import PyK4A
from kinect_capture import capture
from fpv_camera import capture_fpv  # 导入新的FPV摄像头采集函数


class MasterClock:
    """主时钟，用于全局同步"""
    def __init__(self):
        self.start_time = None
        
    def set_start_time(self):
        self.start_time = time.time()

class MultiKinectManager:
    def __init__(self, base_output_folder="output", duration=10, fps=30, max_frames=None, enable_fpv=True, fpv_camera_id=0):
        """多Kinect设备同步管理器"""
        self.base_output_folder = base_output_folder
        self.duration = duration
        self.fps = fps
        self.max_frames = max_frames
        self.devices = []
        self.enable_fpv = enable_fpv  # 是否启用第一人称摄像头，默认启用
        self.fpv_camera_id = fpv_camera_id  # 第一人称摄像头ID
        
    def detect_devices(self):
        """检测连接的Kinect设备数量"""
        devices = []
        device_id = 0
        
        while True:
            try:
                k4a = PyK4A(device_id=device_id)
                k4a.open()
                devices.append(device_id)
                k4a.close()
                device_id += 1
            except Exception as e:
                break
                
        print(f"检测到 {len(devices)} 台Kinect设备")
        return devices
        
    def start_synchronized_capture(self):
        """严格同步的多设备采集"""
        self.devices = self.detect_devices()
        if not self.devices:
            print("未检测到任何Kinect设备，退出程序")
            return
            
        # 创建基本输出目录
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")  # 年月日_时分秒
        session_folder = os.path.join(self.base_output_folder, f"session_{timestamp}")
        os.makedirs(session_folder, exist_ok=True)
        
        # 准备同步启动的事件
        start_event = threading.Event()
        threads = []
        
        # 准备所有设备的采集线程
        for device_id in self.devices:
            device_folder = os.path.join(session_folder, f"kinect_{device_id}")
            
            # 创建一个函数来包装capture调用，实现同步等待
            def capture_with_sync(device_id=device_id, output_folder=device_folder):
                # 等待同步信号
                print(f"设备 {device_id} 已准备就绪，等待同步...")
                start_event.wait()
                # 调用已有的capture函数
                capture(
                    device_index=device_id, 
                    output_folder=output_folder,
                    duration=self.duration,
                    fps=self.fps,
                    max_frames=self.max_frames
                )
            
            thread = threading.Thread(target=capture_with_sync)
            threads.append(thread)
            thread.start()
        
        # 如果启用了第一人称摄像头
        if self.enable_fpv:
            fpv_folder = os.path.join(session_folder, "fpv_camera")
            
            # 创建一个函数来包装第一人称摄像头采集，实现同步等待
            def fpv_capture_with_sync(camera_id=self.fpv_camera_id, output_folder=fpv_folder):
                # 等待同步信号
                print(f"第一人称摄像头 ID={camera_id} 已准备就绪，等待同步...")
                start_event.wait()
                # 调用第一人称摄像头采集函数
                capture_fpv(
                    camera_id=camera_id,
                    output_folder=output_folder,
                    duration=self.duration,
                    fps=self.fps,
                    max_frames=self.max_frames
                )
            
            fpv_thread = threading.Thread(target=fpv_capture_with_sync)
            threads.append(fpv_thread)
            fpv_thread.start()
            
        # 给设备初始化时间
        print("等待所有设备准备就绪...")
        time.sleep(2.0)
        
        # 同时触发所有线程开始采集
        start_event.set()
        device_count = len(self.devices) + (1 if self.enable_fpv else 0)
        print(f"所有 {device_count} 台设备开始同步采集...")
        
        # 等待所有线程完成
        for thread in threads:
            thread.join()
            
        # 保存会话信息
        session_info = {
            "timestamp": timestamp,
            "kinect_count": len(self.devices),
            "kinect_ids": self.devices,
            "fpv_camera_enabled": self.enable_fpv,
            "fpv_camera_id": self.fpv_camera_id if self.enable_fpv else None,
            "duration": self.duration,
            "fps": self.fps,
            "max_frames": self.max_frames
        }
        
        with open(f"{session_folder}/session_info.json", 'w') as f:
            json.dump(session_info, f, indent=2)
            
        print(f"所有设备采集完成，数据保存在: {session_folder}")
        return session_folder
