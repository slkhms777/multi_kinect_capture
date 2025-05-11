import os
import time
import cv2

class FPVCamera:
    def __init__(self, camera_id=0, output_folder="output", duration=10, fps=30, max_frames=None):
        """
        初始化FPVCamera对象
        
        参数:
        camera_id: 摄像头ID，默认为0
        output_folder: 输出目录
        duration: 采集持续时间(秒)
        fps: 帧率
        max_frames: 最大采集帧数
        """
        self.camera_id = camera_id
        self.output_folder = output_folder
        self.duration = duration
        self.fps = fps
        self.max_frames = max_frames

    def capture(self):

        # 确保输出目录存在
        os.makedirs(self.output_folder, exist_ok=True)
        
        # 初始化摄像头
        cap = cv2.VideoCapture(self.camera_id)
        if not cap.isOpened():
            print(f"错误: 无法打开第一人称摄像头")
            return
        
        # 设置摄像头分辨率和帧率 (可能不是所有摄像头都支持)
        cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        cap.set(cv2.CAP_PROP_FPS, self.fps)
        
        start_time = time.time()
        frame_idx = 0
        frame_interval = 1.0 / self.fps  # 计算帧间隔时间
        
        while True:
            # 检查是否达到最大帧数
            if self.max_frames is not None and frame_idx >= self.max_frames:
                break
                
            # 检查是否达到最大时长
            if time.time() - start_time >= self.duration:
                break
                
            # 计算下一帧的理想时间
            next_frame_time = start_time + frame_idx * frame_interval
            
            # 等待到达下一帧的时间
            current_time = time.time()
            if current_time < next_frame_time:
                time.sleep(next_frame_time - current_time)
                
            # 获取并保存帧
            ret, frame = cap.read() # bool, numpy.ndarray
            if ret:
                filename = f"{self.output_folder}/fpv_{frame_idx:06d}.jpg"
                cv2.imwrite(filename, frame)
                frame_idx += 1
            else:
                print("警告: 无法读取第一人称摄像头帧")
                time.sleep(0.1)  # 短暂休眠避免CPU占用过高
        cap.release()
        print(f"第一人称摄像头已采集 {frame_idx} 帧图像")