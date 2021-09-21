
import cv2
import numpy as np
import time
import sys
import os


def int2byte(bigint,inttype):
    return np.uint8([ ii for ii in inttype([bigint]).tobytes()])

def byte2bit(byte,bit,offset=0,revserse=False):
    '''
    byte bit: np.uint8 array
    '''
    length=len(byte)
    for bi in range(8):
        bit[offset+bi:offset+8*length:8]=((byte&(1<<bi))>>bi)
    if revserse:
        bit[offset:offset+8*length]=bit[offset:offset+8*length][::-1]

width=1920
height=1080
use_width=1920-64
use_height=1080
case=0
if case==0:
    d=2
    color=1
if case==1:
    d=4
    color=3
byte_per_frame=int(np.ceil(use_height*use_width/d**2/8))*color-(4+4+8+4+4)


if 1:
    from pathlib import Path
    home = str(Path.home())
    path='~/e/extensions.zip'.replace('~',home)

filesize=os.path.getsize(path)
fcount=int(np.ceil(filesize/byte_per_frame))
print('filesize',filesize,'fcount',fcount)

filesizeB=int2byte(filesize,np.int64)

# sys.exit(0)

canvas = np.zeros((height, width, color), dtype="uint8")
if '-f' in sys.argv:
    cv2.namedWindow("canvas", cv2.WND_PROP_FULLSCREEN)          
    cv2.setWindowProperty("canvas", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
cv2.imshow('canvas', canvas)
cv2.waitKey(10000)





to_check_count=fcount
fps_set=4
fps_delay=int(np.ceil(1000/fps_set))
fpscount=0
eof=False


t1=time.time()
lastt=t1
# count=0 # only for file, may be a loop or minus number
# while 1:

# for count in [1,45,777]: # only display missing frame in last turn
for count in range(fcount): # display all frame
    startt=time.time()
    xor_file_part=np.uint8([0,0,0,0])
    xor_head_part=np.uint8([255,0,85,170]) # to avoid pure black or white pass the check
    countB=int2byte(count,np.int32)

    filepart = np.fromfile(path,dtype='uint8',count=byte_per_frame,offset=byte_per_frame*count)
    # filepart = np.random.randint(0,256,size=(byte_per_frame,),dtype="uint8")
    effective_byte = byte_per_frame
    if filepart.size<byte_per_frame:
        effective_byte = filepart.size
        filepart.resize(byte_per_frame)
        eof=True
    effective_byteB = int2byte(effective_byte,np.int32)

    # calculate xor
    for ii in range(0,byte_per_frame,4):
        xor_file_part^=filepart[ii:ii+4]
    xor_head_part^=countB
    xor_head_part^=effective_byteB
    xor_head_part^=filesizeB[0:4]
    xor_head_part^=filesizeB[4:8]

    # fill data
    rawdata = np.zeros((use_height//d)*(use_width//d)*color,dtype="uint8")

    byte2bit(countB,rawdata,(0)*8,revserse=True)
    byte2bit(effective_byteB,rawdata,(4)*8,revserse=True)
    byte2bit(filesizeB,rawdata,(4+4)*8,revserse=True)
    byte2bit(xor_head_part,rawdata,(4+4+8)*8,revserse=True)
    byte2bit(filepart,rawdata,(4+4+8+4)*8)
    byte2bit(xor_file_part,rawdata,(4+4+8+4+byte_per_frame)*8)

    rawframe=rawdata.reshape(use_height//d, use_width//d, color)*255

    for ii in range(d):
        for jj in range(d):
            canvas[ii:use_height:d,jj:use_width:d,:]=rawframe

    cv2.imshow('canvas', canvas)
    # cv2.imshow('canvas', np.random.randint(0,2,size=(height//d, width//d),dtype="uint8")*255)

    # # update count
    # count+=1

    # update fps information
    fpscount+=1
    if fpscount%10==0:
        t2=time.time();print(fpscount,t2-t1,fpscount/(t2-t1))
    currentt=time.time()
    costt=int((currentt-startt)*1000)
    # wait fps_delay-costt to make fps <= fps_set
    if cv2.waitKey(max(1,fps_delay-costt)) & 0xFF==27: # esc
        break
    if count==to_check_count or eof:
        break

t2=time.time();print(fpscount,t2-t1,fpscount/(t2-t1))


canvas = np.zeros((height, width, color), dtype="uint8")
cv2.imshow('canvas', canvas)

cv2.waitKey(0)
cv2.destroyAllWindows()

