import pygame
import time
import os

# 1. 初始化检查
print("=== Pygame音频调试 ===")
print(f"当前工作目录: {os.getcwd()}")
print(f"音频文件存在: {os.path.exists('1.mp3')}")

# 2. 强制指定音频驱动（关键步骤！）
os.environ['SDL_AUDIODRIVER'] = 'alsa'  # 对于Linux系统
# os.environ['SDL_AUDIODRIVER'] = 'directsound'  # Windows系统
# os.environ['SDL_AUDIODRIVER'] = 'coreaudio'   # Mac系统

# 3. 分步初始化Pygame
try:
    pygame.init()
    print(f"Pygame初始化成功，版本: {pygame.version.ver}")
    
    # 4. 特殊混音器设置
    pygame.mixer.quit()  # 先重置混音器
    pygame.mixer.pre_init(
        frequency=44100,  # 标准CD音质
        size=-16,         # 16位采样
        channels=2,       # 立体声
        buffer=1024       # 缓冲区大小
    )
    pygame.mixer.init()
    print(f"混音器初始化: {pygame.mixer.get_init()}")
    
    # 5. 加载音频文件
    if not os.path.exists("1.mp3"):
        raise FileNotFoundError("1.mp3文件不存在")
    
    print("尝试加载音频...")
    try:
        sound = pygame.mixer.Sound("1.mp3")  # 方法1：适合短音效
        # pygame.mixer.music.load("1.mp3")    # 方法2：适合长音乐
    except pygame.error as e:
        print(f"加载失败，尝试转换格式...")
        os.system("ffmpeg -y -i 1.mp3 1.wav 2>/dev/null")  # 转换为WAV
        sound = pygame.mixer.Sound("1.wav")
    
    # 6. 播放测试
    print("开始播放...")
    sound.play()
    # pygame.mixer.music.play()  # 如果用music.load
    
    # 7. 保持程序运行
    while pygame.mixer.get_busy():
        print("播放中...", end="\r")
        time.sleep(0.1)
    
    print("\n✅ 播放完成！")
    
except Exception as e:
    print(f"❌ 发生错误: {str(e)}")
finally:
    pygame.quit()
