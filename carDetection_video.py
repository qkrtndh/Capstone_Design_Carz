import cv2
import numpy as np
import time
import os

def live_capture():
    #기본 정보 읽어오기, 세팅

    #분할이미지 저장경로 지정
    save_path="d:\\carz_operated\\cuted_img"
    #경로 없는 경우 생성
    if not os.path.exists(save_path):
        os.mkdir(save_path)

    cnt = 0
    net = cv2.dnn.readNet("custom_final2.weights","custom.cfg")
    classes = []
    with open("custom.names", "r") as f:
        classes = [line.strip() for line in f.readlines()]
    layer_names = net.getLayerNames()
    output_layers = [layer_names[i[0]-1]for i in net.getUnconnectedOutLayers()]
    colors = np.random.uniform(0, 255, size=(len(classes), 3))
    #세팅 끝
    flag = 0                                                    #인식 여부 확인 변수    
    videosignal = cv2.VideoCapture(0)                           #웹캠에서 비디오 읽어오기
    while True:
        ret, frame = videosignal.read()
        height, width, channels = frame.shape                         #입력받은 이미지의 높이 너비 읽어오기
        blob = cv2.dnn.blobFromImage(frame, 0.00392, (416, 416), (0, 0, 0), True, crop=False) #입력받은 이미지 yolo연산을 위해 크기 조정
        net.setInput(blob)
        outs = net.forward(output_layers)
        class_ids=[]
        confidences=[]
        boxes=[]
        for out in outs:                    #outs = 감지된 모든 개체에 대한 정보
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.9:
                    center_x = int(detection[0]*width)  #찾은 객체의 가운데 x 좌표
                    center_y = int(detection[1]*height) #찾은 객체의 가운데 y 좌표
                    w = int(detection[2]*width)         #찾은 객체의 너비
                    h = int(detection[3]*height)        #찾은 객체의 높이
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)
                    boxes.append([x, y, w, h])          #표시할 박스의 x,y좌표와 높이 너비 boxes에 저장
                    confidences.append(float(confidence))   #각각 박스의 정확도를 confidences에 저장
                    class_ids.append(class_id)


    
            indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)    #노이즈 제거
            #crop_img=[]
            for i in range(len(boxes)):
                if i in indexes:
                    x,y,w,h = boxes[i]
                    crop_img=frame[y+1:y+h, x+1:x+w]
                    cv2.rectangle(frame, (x,y), (x+w, y+h), (0,0,255),1)  #번호판에 사각형 표시
            #cv2.imshow("detect", frame)                     #화면에 영상 계속 표사
            if flag < 5 and len(boxes)>0:
               
                croped_img_path="d:\\carz_operated\\cuted_img\\" + str(flag) + ".jpg"
                cv2.imwrite(croped_img_path, crop_img)#번호판 부분만 저장
                if flag < 5:
                    time.sleep(1)
                    print(str(flag)+"번째 1초뒤 저장") 
                flag += 1                                    #인식했다는 표시
            if flag==5:
                cv2.destroyAllWindows()
                break
        if flag==5:
            break
    return croped_img_path