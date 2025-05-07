import os
import time
import argparse
import threading
import json
from datetime import datetime
from pyk4a import PyK4A
from multi_kinect_manager import MultiKinectManager


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=str, default='output', help='Base output folder')
    parser.add_argument('--duration', type=int, default=10, help='Capture duration (seconds)')
    parser.add_argument('--fps', type=int, default=30, help='Frames per second')
    parser.add_argument('--max_frames', type=int, default=None, help='Maximum number of frames')
    parser.add_argument('--enable-fpv', action='store_true', help='Enable first person view camera')
    parser.add_argument('--fpv-camera-id', type=int, default=0, help='FPV camera device ID')
    args = parser.parse_args()
    
    manager = MultiKinectManager(
        base_output_folder=args.output,
        duration=args.duration,
        fps=args.fps,
        max_frames=args.max_frames,
        enable_fpv=args.enable_fpv,
        fpv_camera_id=args.fpv_camera_id
    )
    manager.start_synchronized_capture()

    # 数据整理
    