from pynput import keyboard, mouse
import pyautogui
import pytesseract
from PIL import Image
from googletrans import Translator
import tkinter as tk

# 번역기 초기화
translator = Translator()

# 마우스 드래그 영역 저장
start_x, start_y = None, None
end_x, end_y = None, None
dragging = False
hotkey_active = False

# 현재 눌린 키를 추적
current_keys = set()

# 마우스 이벤트 처리
def on_click(x, y, button, pressed):
    global start_x, start_y, end_x, end_y, dragging
    if hotkey_active:  # 단축키가 활성화된 상태에서만 동작
        if pressed and button == mouse.Button.left:
            start_x, start_y = x, y
            dragging = True
        elif not pressed and button == mouse.Button.left and dragging:
            end_x, end_y = x, y
            dragging = False
            process_selection()

# 선택된 영역 처리
def process_selection():
    global start_x, start_y, end_x, end_y
    
    # 영역 크기 계산
    left = min(start_x, end_x)
    top = min(start_y, end_y)
    width = abs(end_x - start_x)
    height = abs(end_y - start_y)
    
    if width > 0 and height > 0:
        # 화면 캡처
        screenshot = pyautogui.screenshot(region=(left, top, width, height))
        screenshot.save("temp_screenshot.png")
        
        # OCR로 텍스트 추출
        text = pytesseract.image_to_string(Image.open("temp_screenshot.png"))
        
        if text.strip():
            # 영어 -> 한국어 번역
            translated = translator.translate(text, src='en', dest='ko').text
            
            # 번역된 텍스트를 화면에 표시
            show_translated_text(translated, left, top, width, height)

# 번역된 텍스트를 화면에 표시
def show_translated_text(text, x, y, width, height):
    root = tk.Tk()
    root.overrideredirect(True)  # 창 테두리 제거
    root.geometry(f"{width}x{height}+{x}+{y}")
    root.attributes("-alpha", 0.8)  # 투명도 설정
    
    label = tk.Label(root, text=text, wraplength=width-10, justify="left", bg="black", fg="white")
    label.pack(expand=True, fill="both")
    
    # 5초 후 창 닫기
    root.after(5000, root.destroy)
    root.mainloop()

# 키보드 이벤트 처리
def on_press(key):
    global hotkey_active
    try:
        current_keys.add(key)
        # Ctrl+Shift+T가 눌렸는지 확인
        if (keyboard.Key.ctrl_l in current_keys or keyboard.Key.ctrl_r in current_keys) and \
           (keyboard.Key.shift in current_keys) and \
           (key == keyboard.KeyCode.from_char('t')):
            hotkey_active = True
            print("단축키가 눌렸습니다. 영역을 드래그하세요...")
    except AttributeError:
        pass

def on_release(key):
    global hotkey_active
    try:
        current_keys.discard(key)
        # Ctrl 또는 Shift가 떼어지면 단축키 비활성화
        if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r, keyboard.Key.shift):
            hotkey_active = False
    except KeyError:
        pass

# 프로그램 시작
if __name__ == "__main__":
    print("단축키 Ctrl+Shift+T를 눌러 프로그램을 시작하세요.")
    
    # 키보드 리스너 시작
    keyboard_listener = keyboard.Listener(on_press=on_press, on_release=on_release)
    keyboard_listener.start()
    
    # 마우스 리스너 시작
    mouse_listener = mouse.Listener(on_click=on_click)
    mouse_listener.start()
    
    # 프로그램 종료를 기다림
    keyboard_listener.join()
    mouse_listener.join()