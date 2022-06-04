import cv2
from pytesseract import image_to_string
import pytesseract

pytesseract.pytesseract.tesseract_cmd=R'C:\Program Files\Tesseract-OCR\tesseract.exe'

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)


def videoDetector():
    if cap.isOpened():
        while True:
            ret, video = cap.read()
            if ret:
                video = cv2.resize(video, dsize=(400, 300), interpolation=cv2.INTER_AREA)

                gray = cv2.cvtColor(video, cv2.COLOR_BGR2GRAY)
                gray = cv2.resize(gray, dsize=(400, 300), interpolation=cv2.INTER_AREA)

                threshold = cv2.threshold(gray, 255, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                img_result = cv2.resize(threshold, dsize=(400, 300), interpolation=cv2.INTER_AREA)

                img_result = cv2.medianBlur(img_result, ksize=5)
                cv2.imshow("windiow", img_result)
                text = image_to_string(img_result, lang='eng', config='--psm 1 -c preserve_interword_spaces=1')
                text = text.upper()
                textArr = text.split('\n')
                # print(textArr)

                print("Text = " + str(textArr))

                if cv2.waitKey(1) != -1:
                    break
            else:
                print("no frame")
                break
    else:
        print("can't open camera")


videoDetector()

cv2.waitKey(0)
cv2.destroyAllWindows()
