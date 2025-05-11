import os
import sys
import time
import argparse
import cv2
from pyk4a import PyK4A, Config, ColorResolution, DepthMode

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
    print(f"设备 {device_index} 已采集 {frame_idx} 帧图像")
