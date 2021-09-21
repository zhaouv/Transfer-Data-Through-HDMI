# Transfer-Data-Through-HDMI

Transfer data from a network-isolated system.  
(Of course, USB storage devices are also prohibited)

... to be translated

# 通过HDMI传输数据

从网络隔离的系统中获取数据.  
(USB存储设备也无法使用)

分成以下几种设定

是否允许接hdmi/dp线等
+ 是:通过采集卡传输图像  
  速度高且稳定, 不需要做位置识别之类的额外处理, 只需要对抗一下采集卡的压缩
+ 否:通过相机摄屏  
  要考虑对准以及颜色校准等等

是否允许插自带的键盘鼠标
+ 是:通过被识别为hid设备的芯片来高速输入  
  通过CH340+CH9329伪装键鼠, 可以把复杂的纠错/压缩算法输入进去, 例如直接把二维码生成的算法放进去
+ 否:只能手动敲代码进去  
  此情况下内网端的代码必须简洁

作为合理的假设的话, 应该只要求内网有浏览器,  
发送端应该是js脚本, 开发阶段内网也暂时用python3+numpy+cv2  
同时先只考虑允许接hdmi使用采集卡的情况

## 协议

暂定使用 1920-64,1080 的区域, 右边用来放鼠标, (为了方便直接切掉了64宽度的一整条)

采集端的帧率需要大于输出端, 暂定为4帧/s

每个点重复成22的格子 ~ [11 22 44 88]

每个点储存1比特的信息 ~ [1 3 6 9 12 15 18 21 24]

开头4字节当前第几帧 再4字节本帧的有效字节数 再8字节表明总字节数 再4字节head部分的xor 然后是数据部分 有效长度之后再补4字节用来算数据部分的xor

`((1920-64)/2)*(1080/2)*1/8-(4+4+8+4+4)=62616`

|字节数|4|4|8|4|62616|4|
|-|-|-|-|-|-|-|
|内容|当前帧数|本帧有效字节数|文件总字节数|协议头的校验|文件内容|文件内容的校验|

## 实现

目前简略实现了 22的格子储存1比特 和 44的格子储存3比特 ,最便宜的 hdmi in + hdmi out + usb3.0 的 RMB129的采集卡压缩的比较多, 只能到这种程度了, 而且fps只能到5. 44的格子储存3比特 的组合的话每帧的信息是 22的格子储存1比特 的3/4.

[发送端](psend1.py)  
[接收端](precieve1.py)  

## 效果

247秒正确传输了一个60448768字节的文件

```
turn 1
...
done frame 965
1270 246.32172799110413 5.155858601502933
not pass the xor_head_part check
1271 246.43009567260742 5.157649257615742
missing frame: [1, 2, 3, 4]

the mouse cover some pixels at the start

turn 2
50 5.202116966247559 9.611471699773503
done frame 1
done frame 2
done frame 3
done frame 4
not pass the xor_head_part check
57 6.628857135772705 8.598767303702902
missing frame: [0, 5, 6, ...]

filesize 60448768 fcount 966
...
950 237.2980456352234 4.003404231404199
960 239.79769849777222 4.003374536177705
966 241.49949431419373 4.000008375765883

xxx% ssh xxx "md5sum ~/e/extensions.zip"
abbfda1a505eedbd2bea255fb60bffe6  /home/xxx/e/extensions.zip
xxx% md5 dev.test.zip 
MD5 (dev.test.zip) = abbfda1a505eedbd2bea255fb60bffe6

60448768/247 - 238kByte/s

```

