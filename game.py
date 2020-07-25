import keyboard as kbd
import cv2
import numpy as np
import imutils
import math

SPACE = 'space'
UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'
STANDBY = 'stdby'

THRESHOLD = 50
THRESHOLD_1 =320
prev_key = STANDBY


def capture():
    #capture frame

    cap = cv2.VideoCapture(0)
    cap.set(3,1920)
    cap.set(4,1080)
   
    while(True):
        ret, frame = cap.read()
        if ret:
            left_pos, right_pos,up_pos,down_pos,l = coords(frame)
            SPEED = relative_speed(left_pos, right_pos,up_pos,down_pos,scale_factor=1)
            DIST = relative_dist(left_pos, right_pos, scale_factor = 1)
            #press_key(DOWN)
            if l == -1 :
                print("wait....")
            elif l == 1 :
                print("going backward")
                press_key(DOWN) 
            else:

                if  SPEED is not None:
                    if abs(SPEED) > THRESHOLD_1:
                        print(SPEED)
                        print("UP")
                        kbd.release(DOWN)
                        press_key(UP)
                    
                else:   
                        print("Down")
                        press_key(DOWN)


                 


                if DIST is not None  :
                    if abs(DIST) < THRESHOLD :
                        print("STANDBY_UP")                                             
                        press_key(UP)
                    elif DIST < 0 :
                        print("turning left ")
                        print(DIST)

                        press_key(LEFT)
                    else:
                        print("turning right ")
                        print(DIST)
                        press_key(RIGHT)
              

                
                   
                
                    
               

            
            if cv2.waitKey(1) == 27: 
                break
    cap.release() 
    # Destroy all the windows 
    cv2.destroyAllWindows() 

def coords(img):
    
    #code to extract bounding boxes
    #return centroid coords
    im=img
    img=img[252:750,400:1080]
    im=cv2.rectangle(im,(1080,252),(400,750),(0,255,0),2)
    blur = cv2.GaussianBlur(img, (5,5), 0)


    B,G,R = blur[:,:,0],blur[:,:,1],blur[:,:,2]
    img_HSV = cv2.cvtColor(blur.copy(), cv2.COLOR_BGR2HSV)
    H,S,V=cv2.split(img_HSV)
    S=S/255
    mask = np.zeros((blur.shape))

    img_YCrCb = cv2.cvtColor(blur, cv2.COLOR_BGR2YCrCb)
    Y,Cr,Cb=cv2.split(img_YCrCb)
    rr = (R>95)
    gg = (G>40)
    bb = (B>20)
    x = (R>G)
    y = (R>B)
    rb = abs(R-G)
    rb = (rb>15)
    
    an = np.logical_and(rr,gg)
    an = np.logical_and(an,bb)
    an = np.logical_and(an,x)
    an = np.logical_and(an,y)
    an = np.logical_and(an,rb)
    an = an.astype('uint8')*255
    cv2.imshow('img',img)
    cv2.imshow('mask',an)

    kernel = cv2.getStructuringElement(cv2.MORPH_CROSS, (8, 8))
    hsv_d = cv2.dilate(an, kernel)
    mask = cv2.GaussianBlur(hsv_d,(7,7),0)
    
    contours= cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(contours)
    cnts = sorted(cnts, key=cv2.contourArea, reverse=True)
    skin=cv2.bitwise_and(img,img,mask=mask)
    #cv2.imshow('image',im)
    cv2.imshow("hsv_d image",hsv_d)
    #cv2.imshow("skin image",skin)
    l=0
    pos = []
    for c in cnts:
        M = cv2.moments(c)
        area=int(M["m00"])
        if area > 20000:
            x,y,w,h = cv2.boundingRect(c)
            cv2.rectangle(img,(x,y),(x+w,y+h),(0,255,0),2)
            pos.append((x+w/2, y+h/2))
    
    if len(pos)==2:
        (x1, y1), (x2, y2) = pos[0], pos[1]
        
        if x1 < x2:
            left_pos = y1
            right_pos = y2
            up_pos = x1
            down_pos = x2
            l=2
        else:
            left_pos = y2
            right_pos = y1
            up_pos = x2
            down_pos = x1
            l=2
             
    elif len(pos)==1:
        print("length  =  1")
        l=1
        left_pos = None
        right_pos = None
        up_pos = None
        down_pos = None

    else:

        print("NONE")
        left_pos = None
        right_pos = None
        up_pos = None
        down_pos = None
        l=-1
    return  right_pos,left_pos,up_pos,down_pos,l

def relative_dist(left_pos, right_pos, scale_factor):
    DIST = None
    if right_pos is not None and left_pos is not None:
        DIST = (right_pos - left_pos) * scale_factor
    return DIST

def relative_speed(left_pos, right_pos,up_pos,down_pos,scale_factor=1):
    speed=None
    if up_pos is not None and down_pos is not None:
        speed = math.sqrt((up_pos - down_pos)**2 + (right_pos - left_pos)**2 )*scale_factor
    return speed

def press_key(key):
    global prev_key
    if prev_key != STANDBY:
        kbd.release(prev_key)
    prev_key = key
    if key != STANDBY:
        kbd.press(key)
    
    
def main():
    print('Waiting to start...')
    #kbd.wait(SPACE)
    capture()
     
if __name__=='__main__':
    main()
    
    
    
    
    
    
    
    
    
  