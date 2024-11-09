import cv2
import mediapipe as mp
from pycaw.pycaw import AudioUtilities
from pycaw.utils import IAudioEndpointVolume

# 获取音频设备
devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, 1, None)
volume = interface.QueryInterface(IAudioEndpointVolume)

# 初始化手部模型
mp_hands = mp.solutions.hands
hands = mp_hands.Hands(static_image_mode=False, max_num_hands=1, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# 上一次食指指尖y坐标
prev_index_y = None

# 打开摄像头
cap = cv2.VideoCapture(0)

# 增大音量
def increase_volume(step=0.05):
    current = volume.GetMasterVolumeLevelScalar()
    new_volume = min(current + step, 1.0)  # 最大音量为1
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    print(f"音量增大到: {new_volume * 100:.2f}%")

# 减小音量
def decrease_volume(step=0.05):
    current = volume.GetMasterVolumeLevelScalar()
    new_volume = max(current - step, 0.0)  # 最小音量为0
    volume.SetMasterVolumeLevelScalar(new_volume, None)
    print(f"音量减小到: {new_volume * 100:.2f}%")

while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        break

    # 左右翻转
    frame = cv2.flip(frame, 1)

    # 将 BGR 图像转换为 RGB
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    results = hands.process(rgb_frame)

    # 检测到手部
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            # 获取食指指尖坐标
            index_finger_tip = hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_TIP]

            # 获取食指指尖y坐标
            index_y = index_finger_tip.y

            # 判断滑动方向
            if prev_index_y is not None:
                if index_y < prev_index_y - 0.05:
                    print("上滑")
                    increase_volume()
                elif index_y > prev_index_y + 0.05:
                    print("下滑")
                    decrease_volume()

            # 更新记录的y坐标
            prev_index_y = index_y

            # 可视化手部关键点
            mp_drawing.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)

    # 显示图像
    cv2.imshow("Gestures control volume", frame)

    # ESC 键退出
    if cv2.waitKey(1) & 0xFF == 27:
        break

# 释放资源
cap.release()
cv2.destroyAllWindows()
hands.close()
