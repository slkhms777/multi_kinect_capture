import sys
import time
import argparse
from pyk4a import PyK4A, Config, ColorResolution, DepthMode

def capture(device_index=0, output_folder="output", duration=10, fps=30):
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
    while time.time() - start_time < duration:
        capture = k4a.get_capture()
        if capture.color is not None:
            # 保存彩色图像
            filename = f"{output_folder}/color_{frame_idx:06d}.jpg"
            cv2.imwrite(filename, capture.color)
        if capture.depth is not None:
            # 保存深度图像
            filename = f"{output_folder}/depth_{frame_idx:06d}.png"
            cv2.imwrite(filename, capture.depth)
        frame_idx += 1
    k4a.stop()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--index', type=int, default=0, help='Kinect device index')
    parser.add_argument('--output', type=str, default='output', help='Output folder')
    parser.add_argument('--duration', type=int, default=10, help='Capture duration (seconds)')
    parser.add_argument('--fps', type=int, default=30, help='Frames per second')
    args = parser.parse_args()
    capture(device_index=args.index, output_folder=args.output, duration=args.duration, fps=args.fps)