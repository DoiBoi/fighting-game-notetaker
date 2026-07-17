# Source - https://stackoverflow.com/a/33399711
# Posted by fireant, modified by community. See post 'Timeline' for change history
# Retrieved 2026-07-05, License - CC BY-SA 4.0

import cv2

vidcap = cv2.VideoCapture('demo.mp4')
success, image = vidcap.read()
interval = 180
count = 0
start = 6900
success = True
while success and count <= 12800:
    if count >= start:
        cv2.imwrite("frames/frame%d.jpg" % count, image)     # save frame as JPEG file
        success, image = vidcap.read()

        for i in range(interval - 1):
            vidcap.read()
            # print(f"Skipped frame {count+i}")

        print('Read a new frame: ', success)
    else:
        for i in range(interval):
            vidcap.read()
            # print(f"Skipped frame {count+i}")

    count += interval
