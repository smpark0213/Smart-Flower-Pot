

import os
import time
import paho.mqtt.client as mqtt
import cv2
import pytesseract
import re
import ffmpeg

rtsp_url = "rtsp://arkpi.local:8554/unicast"
tmp_img_file = './currentimg.jpg'
broker_ip = 'arkpi.local'
topic = 'ocrrequest'
publish_topic = 'plantdetect'
mqtt_port = 1883
is_ocr_enabled = False


def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connect ok!")
    else:
        print("Bad connection returned code = ", rc)


def on_disconnect(client, userdata, flags, rc=0):
    print("Disconncted! rc = " + str(rc))


def on_subscribe(client, userdata, mid, granted_qos):
    print("Subscribed to " + str(mid) + " " + str(granted_qos))


def on_message(client, userdata, msg):
    global is_ocr_enabled

    print(msg.topic, str(msg.payload.decode("utf-8")))
    payload = msg.payload.decode()

    if msg.topic == topic and payload == 'true':
        is_ocr_enabled = True
        run_ocr()
    elif msg.topic == topic and payload == 'false':
        is_ocr_enabled = False


def run_ocr():
    global is_ocr_enabled, cap
    print('run ocr', is_ocr_enabled)

    try:
        start_time = time.time()
        crttime = time.time()
        while crttime - start_time <= 5000:
            if os.path.isfile(tmp_img_file):
                os.remove(tmp_img_file)

            stream.output(tmp_img_file, update=1, vframes=1).run()

            if os.path.isfile(tmp_img_file):
                frame = cv2.imread(tmp_img_file)

                img_result = cv2.resize(frame, dsize=(400, 300), interpolation=cv2.INTER_AREA)
                img_result = cv2.cvtColor(img_result, cv2.COLOR_BGR2GRAY)

                i = 0
                j = 300
                result = None
                while i < 400 and j > 150:
                    print(i)
                    new_img = img_result[150:j, i:400]
                    new_img = cv2.threshold(new_img, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
                    new_img = cv2.adaptiveThreshold(new_img, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 10)
                    new_img = cv2.medianBlur(new_img, 1)

                    i += 20
                    j -= 20

                    # 띄어쓰기 지우고 소문자화
                    text = pytesseract.image_to_string(new_img,
                                                       lang='eng',
                                                       config='--oem 1 --psm 8').strip().lower()

                    # 영어 이외에 모든 문자 제거
                    text = re.sub('[^a-zA-Z]', '', text)
                    print(text)

                    if 'planta' in text:
                        result = 'planta'
                        break
                    elif 'plantb' in text:
                        result = 'plantb'
                        break
                    elif 'plantc' in text:
                        result = 'plantc'
                        break
                if result:
                    client.publish(publish_topic, result, qos=2)
                    break

                crttime = time.time()
            else:
                print('frame error')
                break
        print("closed")
    except Exception as e:
        print(e)
    finally:
        cv2.destroyAllWindows()
        print('OK')
        is_ocr_enabled = False


if __name__ == '__main__':
    stream = ffmpeg.input(rtsp_url)

    client = mqtt.Client(client_id='ocrserver')

    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    client.connect(broker_ip, mqtt_port)

    client.subscribe(topic)
    client.loop_forever()

