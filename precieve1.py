import numpy as np
import cv2
import time
import sys
import os

def int2byte(bigint,inttype):
    return np.uint8([ ii for ii in inttype([bigint]).tobytes()])

def byte2int(byte,inttype):
    return int(np.frombuffer(byte.tobytes(),dtype=inttype))

def bit2int(a):
    return int(a.tobytes().replace(b"\x00",b'0').replace(b"\x01",b'1').decode(),2)

def byte2bit(byte,bit,offset=0,revserse=False):
    '''
    byte bit: np.uint8 array
    '''
    length=len(byte)
    for bi in range(8):
        bit[offset+bi:offset+8*length:8]=((byte&(1<<bi))>>bi)
    if revserse:
        bit[offset:offset+8*length]=bit[offset:offset+8*length][::-1]

def bit2byte(bit,byte,offset=0,revserse=False):
    '''
    byte bit: np.uint8 array
    without checking value of bit all in [0,1]
    '''
    length=len(bit)//8
    if revserse:
        bit=bit[::-1]
    for bi in range(8):
        byte[offset:offset+length]^=bit[bi::8]<<bi


# cap = cv2.VideoCapture(0,cv2.CAP_AVFOUNDATION)
cap = cv2.VideoCapture(0)
good = True

good &= cap.set(cv2.CAP_PROP_FRAME_WIDTH,1920)
print(good)
good &= cap.set(cv2.CAP_PROP_FRAME_HEIGHT,1080)
print(good)
print(cap.get(cv2.CAP_PROP_FPS))
good &= cap.set(cv2.CAP_PROP_FPS,10) 
print(cap.get(cv2.CAP_PROP_FPS))
print(good)

def single(frame):
    d=2
    x=96
    y=48
    for ii in range(d):
        for jj in range(d):
            print(frame[y+jj,x+ii,:])

width=1920
height=1080
use_width=1920-64
use_height=1080
use_left=0
use_top=0
case=0
if case==0:
    d=2
    color=1
if case==1:
    d=4
    color=3
byte_per_frame=int(np.ceil(use_height*use_width/d**2/8))*color-(4+4+8+4+4)

path='dev.test.zip'

class g:
    state=0
    count=0
    data_frame_count=0
    frame_status={}  
    filesize = -1
    fcount = 0

def eachframe(frame):
    g.count += 1
    tosum = np.zeros((use_height//d, use_width//d, color),dtype='int')
    for ii in range(d):
        for jj in range(d):
            if color==1:
                for kk in range(3):
                    tosum+=frame[ii+use_top:use_height+use_top:d,jj+use_left:use_width+use_left:d,kk:kk+1]
            elif color==3:
                tosum+=frame[ii+use_top:use_height+use_top:d,jj+use_left:use_width+use_left:d,:]
            else:
                raise RuntimeError('color should be 1 or 3')
    retpic = (tosum/(d*d*3/color)).astype("uint8")
    retpic //= 128
    # cv2.imshow('dev_view',retpic*255)
    retpic=retpic.reshape(-1)
    
    if g.state==0:
        if np.sum(retpic)!=0:
            g.state=1
        else:
            return
    if g.state==1:
        rawbits=retpic
        # check head part xor
        headpart = np.zeros(20,dtype=np.uint8)
        bit2byte(rawbits[0:32],headpart,0,revserse=True)
        bit2byte(rawbits[32:64],headpart,4,revserse=True)
        bit2byte(rawbits[64:128],headpart,4+4,revserse=True)
        bit2byte(rawbits[128:160],headpart,4+4+8,revserse=True)
        if not all(headpart[0:4]^headpart[4:8]^headpart[8:12]^headpart[12:16]^headpart[16:20]==[255,0,85,170]):
            print('not pass the xor_head_part check')
            g.state=2
            return
        g.data_frame_count+=1

        # get protocal vars

        # frame_index = bit2int(rawbits[0:32])
        # effective_byte = bit2int(rawbits[32:64])
        # g.filesize = bit2int(rawbits[64:128])
        frame_index = byte2int(headpart[0:4],np.int32)
        effective_byte = byte2int(headpart[4:8],np.int32)
        filesize_ = byte2int(headpart[8:16],np.int64)

        if g.data_frame_count==1:
            g.filesize = filesize_
            g.fcount=int(np.ceil(g.filesize/byte_per_frame))
            if not os.path.exists(path) or os.path.getsize(path) != g.filesize:
                with open(path,'wb') as fid:
                    fid.seek(g.filesize-1)
                    fid.write(b'\x00')
        
        if g.frame_status.get(frame_index):
            # alreadly recieve this frame
            return

        if frame_index<0 or frame_index>=g.fcount:
            print('invaid frame_index')
            return

        filepart=np.zeros(byte_per_frame,dtype="uint8")
        xor_file_part=np.uint8([0,0,0,0])
        bit2byte(rawbits[160:160+byte_per_frame*8],filepart)
        bit2byte(rawbits[160+byte_per_frame*8:160+byte_per_frame*8+4*8],xor_file_part)
        for ii in range(0,byte_per_frame,4):
            xor_file_part^=filepart[ii:ii+4]
        if np.sum(xor_file_part)!=0:
            print('not pass the xor_file_part check',frame_index)
            g.frame_status[frame_index]=False
            return

        # write to file
        with open(path,'rb+') as fid:
            fid.seek(frame_index*byte_per_frame)
            fid.write(filepart[:effective_byte].tobytes())

        g.frame_status[frame_index]=True
        print('done frame',frame_index)


    if g.state==2:
        return



fpscount = 0
t1=time.time()
while good:
    startt=time.time()
    good, frame = cap.read()
    # cv2.imshow('dev_view',frame)
    if '-s' in sys.argv and fpscount==50:
        single(frame)
        break
    eachframe(frame)
    fpscount+=1
    if fpscount%10==0:
        t2=time.time();print(fpscount,t2-t1,fpscount/(t2-t1))
    currentt=time.time()
    costt=int((currentt-startt)*1000)
    # max(1,250-costt)
    if cv2.waitKey(1) & 0xFF==27: # esc
        break
    if g.state==2:
        break
t2=time.time();print(fpscount,t2-t1,fpscount/(t2-t1))

# cv2.waitKey(0)
cv2.destroyAllWindows()

print('missing frame:',[ii for ii in range(g.fcount) if not g.frame_status.get(ii)])
