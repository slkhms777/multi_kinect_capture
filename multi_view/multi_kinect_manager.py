import datetime
import os
import sys
import time
import json
import threading
import argparse
import cv2
from pyk4a import PyK4A, Config, ColorResolution, DepthMode


class MultiKinectManager:
    def __init__(self, base_output_folder="output", duration=10, fps=30, max_frames=None):
        """多Kinect设备同步管理器"""
        self.base_output_folder = base_output_folder
        self.duration = duration
        self.fps = fps
        self.max_frames = max_frames
        self.devices = []
        
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
    

    def capture(device_index, output_folder="output", duration=10, fps=30, max_frames=None):
        # 确保输出目录存在
        os.makedirs(output_folder, exist_ok=True)
        
        k4a = PyK4A(
            Config(
                color_resolution=ColorResolution.RES_1080P,
                depth_mode=DepthMode.NFOV_UNBINNED,
                camera_fps=fps,
            ),
            device_id=device_index
        )
        k4a.start()
        start_time = time.time()
        frame_idx = 0
        frame_interval = 1.0 / fps  # 计算帧间隔时间
        
        while True:
            # 检查是否达到最大帧数
            if max_frames is not None and frame_idx >= max_frames:
                break
                
            # 检查是否达到最大时长
            if time.time() - start_time >= duration:
                break
                
            # 计算下一帧的理想时间
            next_frame_time = start_time + frame_idx * frame_interval
            
            # 等待到达下一帧的时间
            current_time = time.time()
            if current_time < next_frame_time:
                time.sleep(next_frame_time - current_time)
                
            # 获取并保存帧
            capture = k4a.get_capture()
            if capture.color is not None:
                filename = f"{output_folder}/color_{frame_idx:06d}.jpg"
                cv2.imwrite(filename, capture.color)
            if capture.depth is not None:
                filename = f"{output_folder}/depth_{frame_idx:06d}.png"
                cv2.imwrite(filename, capture.depth)
                
            frame_idx += 1
            
        k4a.stop()
        print(f"Kinect {device_index} 已采集 {frame_idx} 帧图像")
    
        
    def start_synchronized_capture(self):
        """严格同步的多设备采集"""
        self.devices = self.detect_devices()
        if not self.devices:
            print("未检测到任何Kinect设备，退出程序")
            return
        
        # 准备同步启动的事件
        start_event = threading.Event()
        threads = []
        
        # 准备所有设备的采集线程
        for device_id in self.devices:
            device_folder = os.path.join(self.base_output_folder, f"kinect_{device_id}")
            os.makedirs(device_folder, exist_ok=True)
            
            # 创建一个函数来包装capture调用，实现同步等待
            def capture_with_sync(device_id=device_id, output_folder=device_folder):
                # 等待同步信号
                print(f"设备 {device_id} 已准备就绪，等待同步...")
                start_event.wait()
                # 调用已有的capture函数
                self.capture(
                    device_index=device_id, 
                    output_folder=output_folder,
                    duration=self.duration,
                    fps=self.fps,
                    max_frames=self.max_frames
                )
            
            thread = threading.Thread(target=capture_with_sync)
            threads.append(thread)
            thread.start()
        
        # 给设备初始化时间
        print("等待所有 Kinect 设备准备就绪...")
        time.sleep(2.0)
        # 同时触发所有线程开始采集
        start_event.set()
        device_count = len(self.devices)
        print(f" {device_count} 台 Kinect 设备开始同步采集...")
        for thread in threads:
            thread.join()
        print("所有 Kinect 设备采集完成")
        
