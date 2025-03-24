import numpy as np
import pygame


def main():
    # 初始化pygame
    pygame.init()
    pygame.mixer.init()

    # 数字和小写字母到摩斯密码的映射
    morse_code = {
        '0': '-----', '1': '.----', '2': '..---', '3': '...--', '4': '....-',
        '5': '.....', '6': '-....', '7': '--...', '8': '---..', '9': '----.',
        'a': '.-', 'b': '-...', 'c': '-.-.', 'd': '-..', 'e': '.', 
        'f': '..-.', 'g': '--.', 'h': '....', 'i': '..', 'j': '.---',
        'k': '-.-', 'l': '.-..', 'm': '--', 'n': '-.', 'o': '---',
        'p': '.--.', 'q': '--.-', 'r': '.-.', 's': '...', 't': '-',
        'u': '..-', 'v': '...-', 'w': '.--', 'x': '-..-', 'y': '-.--',
        'z': '--..'
    }

    # 设置参数
    frequency = 800  # 音调频率(Hz)
    unit_duration = 0.1  # 一个时间单位（秒）
    dot_duration = unit_duration  # 短音持续时间
    dash_duration = 3 * unit_duration  # 长音持续时间
    symbol_space = unit_duration  # 符号间隔
    letter_space = 3 * unit_duration  # 字母间隔

    # 采样率
    sample_rate = 44100

    # 生成音效函数
    def generate_tone(duration):
        t = np.linspace(0, duration, int(sample_rate * duration), False)
        tone = np.sin(frequency * 2 * np.pi * t)
        audio = tone * 32767 / np.max(np.abs(tone))
        audio = audio.astype(np.int16)
        # 创建立体声
        stereo_audio = np.column_stack([audio, audio])
        return pygame.sndarray.make_sound(stereo_audio)

    # 预先生成音效
    dot_sound = generate_tone(dot_duration)
    dash_sound = generate_tone(dash_duration)

    # 用户输入
    user_input = input("请输入数字或字母: ")

    # 将输入转换为小写
    user_input = user_input.lower()

    # 验证输入是否只包含数字或小写字母
    if not all(char.isdigit() or ('a' <= char <= 'z') for char in user_input):
        print("请只输入数字或字母!")
        return

    print(f"播放 '{user_input}' 的摩斯密码")

    # 遍历每个字符
    for i, char in enumerate(user_input):
        if char in morse_code:
            morse = morse_code[char]
            print(f"字符 {char} 的摩斯密码: {morse}")

            # 播放该字符的摩斯密码
            for symbol in morse:
                if symbol == '.':
                    # 播放短音
                    dot_sound.play()
                    pygame.time.wait(int(dot_duration * 1000))
                elif symbol == '-':
                    # 播放长音
                    dash_sound.play()
                    pygame.time.wait(int(dash_duration * 1000))

                # 符号间隔
                pygame.time.wait(int(symbol_space * 1000))

            # 如果不是最后一个字符，加上字母间隔
            if i < len(user_input) - 1:
                pygame.time.wait(int(letter_space * 3000))

    # 退出pygame
    pygame.quit()


if __name__ == "__main__":
    main()
