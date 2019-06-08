
# SNAKES GAME
# Use ARROW KEYS to play, SPACE BAR for pausing/resuming and Esc Key for exiting

import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
from random import randint
import cv2
import numpy as np
import math
from multiprocessing import Process
import sys
import time




def gesture():
    output_var = "1"
    cap = cv2.VideoCapture(0)
    while(cap.isOpened()):
        # read image
        ret, img = cap.read()

        # get hand data from the rectangle sub window on the screen
        cv2.rectangle(img, (300,300), (100,100), (0,255,0),0)
        crop_img = img[100:300, 100:300]

        # convert to grayscale
        grey = cv2.cvtColor(crop_img, cv2.COLOR_BGR2GRAY)

        # applying gaussian blur
        value = (35, 35)
        blurred = cv2.GaussianBlur(grey, value, 0)

        # thresholdin: Otsu's Binarization method
        _, thresh1 = cv2.threshold(blurred, 127, 255,
                                   cv2.THRESH_BINARY_INV+cv2.THRESH_OTSU)

        # show thresholded image
        #cv2.imshow('Thresholded', thresh1)

        # check OpenCV version to avoid unpacking error
        (version, _, _) = cv2.__version__.split('.')

        if version == '3':
            image, contours, hierarchy = cv2.findContours(thresh1.copy(), \
                   cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)
        else:
            contours, hierarchy = cv2.findContours(thresh1.copy(),cv2.RETR_TREE, \
                   cv2.CHAIN_APPROX_NONE)

        # find contour with max area
        cnt = max(contours, key = lambda x: cv2.contourArea(x))

        # create bounding rectangle around the contour (can skip below two lines)
        x, y, w, h = cv2.boundingRect(cnt)
        cv2.rectangle(crop_img, (x, y), (x+w, y+h), (0, 0, 255), 0)

        # finding convex hull
        hull = cv2.convexHull(cnt)

        areahull = cv2.contourArea(hull)
        areacnt = cv2.contourArea(cnt)
        arearatio=((areahull-areacnt)/areacnt)*100
        # drawing contours
        drawing = np.zeros(crop_img.shape,np.uint8)
        cv2.drawContours(drawing, [cnt], 0, (0, 255, 0), 0)
        cv2.drawContours(drawing, [hull], 0,(0, 0, 255), 0)

        # finding convex hull
        hull = cv2.convexHull(cnt, returnPoints=False)



        # finding convexity defects
        defects = cv2.convexityDefects(cnt, hull)
        count_defects = 0
        cv2.drawContours(thresh1, contours, -1, (0, 255, 0), 3)

        # applying Cosine Rule to find angle for all defects (between fingers)
        # with angle > 90 degrees and ignore defects
        for i in range(defects.shape[0]):
            s,e,f,d = defects[i,0]

            start = tuple(cnt[s][0])
            end = tuple(cnt[e][0])
            far = tuple(cnt[f][0])

            # find length of all sides of triangle
            a = math.sqrt((end[0] - start[0])**2 + (end[1] - start[1])**2)
            b = math.sqrt((far[0] - start[0])**2 + (far[1] - start[1])**2)
            c = math.sqrt((end[0] - far[0])**2 + (end[1] - far[1])**2)

            # apply cosine rule here
            angle = math.acos((b**2 + c**2 - a**2)/(2*b*c)) * 57

            # ignore angles > 90 and highlight rest with red dots
            if angle <= 90:
                count_defects += 1
                cv2.circle(crop_img, far, 1, [0,0,255], -1)
            #dist = cv2.pointPolygonTest(cnt,far,True)

            # draw a line from start to end i.e. the convex points (finger tips)
            # (can skip this part)
            cv2.line(crop_img,start, end, [0,255,0], 2)
            #cv2.circle(crop_img,far,5,[0,0,255],-1)
        output_var = 0
        # define actions required
        if count_defects == 1:
            output_var = 2
            #cv2.putText(img,"2", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            f = open("data.txt", "w")
            f.write("2")
            f.close()

        elif count_defects == 2:
            output_var = 3
            str = "3"
            #cv2.putText(img, str, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            f = open("data.txt", "w")
            f.write("3")
            f.close()

        elif count_defects == 3:
            output_var = 4
            #cv2.putText(img,"4", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            f = open("data.txt", "w")
            f.write("4")
            f.close()

        elif count_defects == 4:
            output_var = 5
            #cv2.putText(img,"5", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
            f = open("data.txt", "w")
            f.write("5")
            f.close()

        elif count_defects == 0:
             if areacnt<2000:
                    output_var = "Put hand in box"
                    cv2.putText(img,'Put hand in the box',(5, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, 2)
                    f = open("data.txt", "w")
                    f.write("Put hand in box")
                    f.close()

             else:
                    if arearatio<12:
                        output_var = "0"
                        #cv2.putText(img,'0',(50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
                        f = open("data.txt", "w")
                        f.write("0")
                        f.close()

                    elif arearatio<17.5:
                        output_var = "Best of luck"
                        #cv2.putText(img,'Best of luck',(50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
                        f = open("data.txt", "w")
                        f.write("Best of luck")
                        f.close()

                    else:
                        output_var = "1"
                        #cv2.putText(img,'1',(50, 50), cv2.FONT_HERSHEY_SIMPLEX, 2, 2)
                        f = open("data.txt", "w")
                        f.write("1")
                        f.close()

        # show appropriate images in windows
        cv2.imshow('Gesture', img)
        all_img = np.hstack((drawing, crop_img))
        #cv2.imshow('Contours', all_img)
        k = cv2.waitKey(10)
        if k == 27:
            cv2.destroyAllWindows()
            break


def game():
 curses.initscr()
 win = curses.newwin(20, 60, 0, 0)
 win.keypad(1)
 curses.noecho()
 curses.curs_set(0)
 win.border(0)
 win.nodelay(1)

 key = KEY_RIGHT                                                    # Initializing values
 score = 3
 counter = 0

 snake = [[4,10], [4,9], [4,8]]                                     # Initial snake co-ordinates
 food = [10,20]                                                     # First food co-ordinates

 win.addch(food[0], food[1], '*')                                   # Prints the food

 while key != 27:
     f = open("data.txt", "r")
     s = f.read()
     if s=="3":
         key=KEY_LEFT
     elif s=="2":
         key=KEY_RIGHT
     elif s=="4":
         key=KEY_UP
     elif s=="5":
         key=KEY_DOWN                                                                # While Esc key is not pressed
     win.border(0)
     win.addstr(0, 2, 'Score : ' + str(counter) + ' ')                # Printing 'Score' and
     win.addstr(0, 27, ' SNAKE ')                                   # 'SNAKE' strings
     win.timeout(int(150 - (len(snake)/5 + len(snake)/10)%120))          # Increases the speed of Snake as its length increases

     prevKey = key                                                  # Previous key pressed
     event = win.getch()
     key = key if event == -1 else event


     if key == ord(' '):                                            # If SPACE BAR is pressed, wait for another
         key = -1                                                   # one (Pause/Resume)
         while key != ord(' '):
             key = win.getch()
         key = prevKey
         continue

     if key not in [KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, 27]:     # If an invalid key is pressed
         key = prevKey

    # Calculates the new coordinates of the head of the snake. NOTE: len(snake) increases.
    # This is taken care of later at [1].
     snake.insert(0, [snake[0][0] + (key == KEY_DOWN and 1) + (key == KEY_UP and -1), snake[0][1] + (key == KEY_LEFT and -1) + (key == KEY_RIGHT and 1)])
     time.sleep(.300)
    # If snake crosses the boundaries, make it enter from the other side
     if snake[0][0] == 0: snake[0][0] = 18
     if snake[0][1] == 0: snake[0][1] = 58
     if snake[0][0] == 19: snake[0][0] = 1
     if snake[0][1] == 59: snake[0][1] = 1

    # Exit if snake crosses the boundaries (Uncomment to enable)
    #if snake[0][0] == 0 or snake[0][0] == 19 or snake[0][1] == 0 or snake[0][1] == 59: break

    # If snake runs over itself
     if snake[0] in snake[1:]:
         score -= 1
         last = snake.pop()                                          # [1] If it does not eat the food, length decreases
         win.addch(last[0], last[1], ' ')

     if score <= 1: break

     if snake[0] == food:                                            # When snake eats the food
         food = []
         score += 1
         counter += 1
         while food == []:
             food = [randint(1, 18), randint(1, 58)]                 # Calculating next food's coordinates
             if food in snake: food = []
         win.addch(food[0], food[1], '*')
     else:
         last = snake.pop()                                          # [1] If it does not eat the food, length decreases
         win.addch(last[0], last[1], ' ')
     win.addch(snake[0][0], snake[0][1], '#')

 curses.endwin()
 print("\nMaximum Eat : " + str(counter))
 print("THE END\n")

if __name__=='__main__':
  p1 = Process(target = game)
  p1.start()
  p2 = Process(target = gesture)
  p2.start()
