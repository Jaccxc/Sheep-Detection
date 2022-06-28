import cv2
import os
import sys
import time
from flask import Flask, render_template, Response

app = Flask(__name__,
            static_url_path='/')  # 设置静态文件路径（我不准备用模板，所以HTML也是放在static文件夹中）
  # 初始化摄像头
#camera = cv2.VideoCapture(0)



@app.route('/')
def index():
    return app.send_static_file('index.html')



@app.before_first_request
def init_cam():
    global camera
    camera = cv2.VideoCapture(1)
    print("cam ready")


def gen(camera):
    #camera = cv2.VideoCapture(0)
    #camera.set(cv2.CAP_PROP_FRAME_WIDTH,1296)
    #camera.set(cv2.CAP_PROP_FRAME_HEIGHT,972)
    while True:
        ret, frame = camera.read()
        try:
            frame = cv2.imencode('.jpg', frame)[1].tobytes()  # opencv存储的图片数据不能用，所以需要进行转码
        except:
            camera.release()
            cv2.destroyAllWindows()
            print("\n\n RELEASED \n\n")
            try:
                sys.exit(0)
            except SystemExit:
                os._exit(0)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')


@app.route('/video_feed')
def video_feed():
    global camera
    return Response(gen(camera),
                    mimetype='multipart/x-mixed-replace; boundary=frame')


if __name__ == '__main__':
    try:
        app.run(host='0.0.0.0', debug=True, threaded=True)
    except KeyboardInterrupt:
        camera.release()
        print("\n\n RELEASED \n\n")
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
