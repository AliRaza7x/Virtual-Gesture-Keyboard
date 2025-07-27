import cv2
from cvzone.HandTrackingModule import HandDetector
from pynput.keyboard import Controller
from time import sleep
import webbrowser

# Setup
cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

detector = HandDetector(detectionCon=0.8, maxHands=1)
keyboard = Controller()

# Keys Layout (per row)
keys = [
    ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P"],
    ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";"],
    ["Z", "X", "C", "V", "B", "N", "M", ",", ".", "/", "BACKSPACE"],
    ["SPACE", "ENTER", "GOOGLE", "YOUTUBE", "GEMINI"]
]

finalText = ""
clickDelay = False  # debounce flag

class Button:
    def __init__(self, pos, text, size):
        self.pos = pos
        self.text = text
        self.size = size

buttonList = []
start_x, start_y = 50, 50
gap = 15  # spacing between buttons

for row_index, row in enumerate(keys):
    x_cursor = start_x
    y = start_y + row_index * (70 + gap)
    for key in row:
        size = {
            "SPACE": [200, 60], "ENTER": [120, 60],
            "GOOGLE": [130, 60], "YOUTUBE": [130, 60],
            "GEMINI": [130, 60], "BACKSPACE": [160, 60]
        }.get(key, [70, 70])
        buttonList.append(Button([x_cursor, y], key, size))
        x_cursor += size[0] + gap

def drawAll(img, buttons):
    for button in buttons:
        x, y = button.pos
        w, h = button.size
        cv2.rectangle(img, (x, y), (x + w, y + h), (240, 240, 240), cv2.FILLED)
        cv2.rectangle(img, (x, y), (x + w, y + h), (100, 100, 100), 2)

        fontScale = 0.7 if len(button.text) > 8 else 0.9 if len(button.text) > 4 else 1.2
        text_size = cv2.getTextSize(button.text, cv2.FONT_HERSHEY_SIMPLEX, fontScale, 2)[0]
        text_x = x + (w - text_size[0]) // 2
        text_y = y + (h + text_size[1]) // 2
        cv2.putText(img, button.text, (text_x, text_y),
                    cv2.FONT_HERSHEY_SIMPLEX, fontScale, (30, 30, 30), 2)
    return img

while True:
    success, img = cap.read()
    img = cv2.flip(img, 1)
    hands, img = detector.findHands(img)
    img = drawAll(img, buttonList)

    if hands:
        lmList = hands[0]["lmList"]
        lm8 = lmList[8][:2]
        lm12 = lmList[12][:2]

        for button in buttonList:
            x, y = button.pos
            w, h = button.size

            if x < lm8[0] < x + w and y < lm8[1] < y + h:
                cv2.rectangle(img, (x, y), (x + w, y + h), (180, 255, 180), cv2.FILLED)
                cv2.putText(img, button.text, (x + 10, y + int(h / 2) + 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 1, (50, 50, 50), 2)

                length, _, _ = detector.findDistance(lm8, lm12)

                if length < 35 and not clickDelay:
                    key = button.text
                    if key == "BACKSPACE":
                        finalText = finalText[:-1]
                    elif key == "SPACE":
                        finalText += " "
                        keyboard.press(" ")
                    elif key == "ENTER":
                        query = finalText.strip().replace(" ", "+")
                        if query:
                            webbrowser.open(f"https://www.google.com/search?q={query}")
                            finalText = ""  # clear after search
                    elif key == "GOOGLE":
                        webbrowser.open("https://www.google.com")
                    elif key == "YOUTUBE":
                        webbrowser.open("https://www.youtube.com")
                    elif key == "GEMINI":
                        webbrowser.open("https://gemini.google.com")
                    else:
                        finalText += key
                        keyboard.press(key)

                    clickDelay = True
                    sleep(0.3)

        # Reset debounce when fingers separate
        if detector.findDistance(lm8, lm12)[0] > 50:
            clickDelay = False

    # Typing area
    cv2.rectangle(img, (50, 420), (1200, 470), (250, 250, 250), cv2.FILLED)
    cv2.putText(img, finalText[-60:], (60, 455), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (50, 50, 50), 2)

    cv2.imshow("Virtual Gesture Keyboard", img)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break
