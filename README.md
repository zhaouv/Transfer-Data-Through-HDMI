# Transfer-Data-Through-HDMI

Imagine a computer setup where the main unit is locked in a cabinet, and only the mouse, keyboard, and a monitor cable extend to the desktop through a small opening. The computer is not connected to the internet. How can the data from this computer be copied out?

For scenarios where the transmission cable can be unplugged, such as when using a non-customized monitor or when the monitor is not embedded in a cabinet, data can be rapidly transmitted using a video capture card.

To achieve this, open the browser's developer tools console on the computer and type the following code from [psend1.html](./psend1.html). Run [precieve1.py](./precieve1.py) on the video capture card to complete the process.

# 通过HDMI传输数据

假设有台这样的电脑摆在面前, 主机锁在柜子里, 只有鼠标键盘和一个显示器的线通过小孔拉到了桌面上, 电脑也没有连接到互联网, 如何把其中的数据复制出来.

对于没有定制显示器或者显示器没有嵌入到柜子中, 能够把传输线拔下来的情况, 通过视频采集卡能够高速的传输数据出来.

在这个电脑打开浏览器的开发者工具的console, 把[psend1.html](./psend1.html)中的如下部分敲进去执行, 视频采集卡运行[precieve1.py](./precieve1.py)即可完成.  

```js
var width = 1920;
var height = 1080;
var useWidth = 1920 - 64;
var useHeight = 1080;
var useLeft = 0;
var useTop = 0;
var fpsSet = 4;
if (1) {
    var d = 2;
    var color = 1;
}
if (0) {
    var d = 4;
    var color = 3;
}

var devicePixelRatio = window.devicePixelRatio || 1;

function int2byte(number, length) {
    var uint8Array = new Uint8Array(length);
    for (var i = 0; i < length; i++) {
        uint8Array[i] = Number((BigInt(number) >> BigInt(i * 8)) & BigInt(0xFF));
    }
    return uint8Array;
}

function byte2bit(byte, bit, offset = 0, reverse = false) {
    for (var ni = 0; ni < byte.length; ni++) {
        var bytei = byte[ni];
        for (var bi = 0; bi < 8; bi++) {
            bit[offset + ni * 8 + bi] = (bytei >> bi) & 1;
        }
    }
    if (reverse) {
        bit.subarray(offset, offset + 8*byte.length).reverse();
    }
}

fileInput = document.createElement('input');
fileInput.type = 'file';
document.body.appendChild(fileInput);

fileInput.addEventListener('change', handleFileSelect);

canvas = document.createElement('canvas');
canvas.width = width;
canvas.height = height;
canvas.style.width = `${width/devicePixelRatio}px`;
canvas.style.height = `${height/devicePixelRatio}px`;
canvas.style.backgroundColor = 'black';
document.body.appendChild(canvas);

function toggleFullScreen() {
    if (!document.fullscreenElement) {
        canvas.requestFullscreen().catch(err => {
            alert(`Error attempting to enable full-screen mode: ${err.message}`);
        });
    } else {
        document.exitFullscreen();
    }
}

canvas.addEventListener('dblclick', toggleFullScreen);

context = canvas.getContext('2d');

function renderFrame(count) {
    console.log('renderFrame',count)
    startt = Date.now();
    xorFilePart = new Uint8Array([0, 0, 0, 0]);
    xorHeadPart = new Uint8Array([255, 0, 0b01010101, 0b10101010]);

    countB = int2byte(count, 4);
    filePart = fileContent.slice(bytePerFrame * count, bytePerFrame * (count + 1));

    effectiveByte = filePart.length;
    if (filePart.length < bytePerFrame) {
        filePart = new Uint8Array(bytePerFrame);
        filePart.set(fileContent.subarray(bytePerFrame * count));
        eof = true;
    }

    effectiveByteB = int2byte(effectiveByte, 4);

    filePart.forEach((v,i)=>xorFilePart[i%4]^=v);

    countB.forEach((v,i)=>xorHeadPart[i%4]^=v);
    effectiveByteB.forEach((v,i)=>xorHeadPart[i%4]^=v);
    fileSizeB.forEach((v,i)=>xorHeadPart[i%4]^=v);

    rawdata = new Uint8Array((useHeight / d) * (useWidth / d) * color);

    byte2bit(countB, rawdata, 0, true);
    byte2bit(effectiveByteB, rawdata, 4 * 8, true);
    byte2bit(fileSizeB, rawdata, (4 + 4) * 8, true);
    byte2bit(xorHeadPart, rawdata, (4 + 4 + 8) * 8, true);
    byte2bit(filePart, rawdata, (4 + 4 + 8 + 4) * 8);
    byte2bit(xorFilePart, rawdata, (4 + 4 + 8 + 4 + bytePerFrame) * 8);

    if (color==3) {
        rawframe = rawdata.map(v=>v*255);
    } else { //color==1
        rawframe = new Uint8Array((useHeight / d) * (useWidth / d) * 3);
        rawdata.forEach((v,i)=>rawframe[3*i]=rawframe[3*i+1]=rawframe[3*i+2]=v*255)
    }
    
    imageData = new Uint8ClampedArray(width * height * 4);
    for (var x = 0; x < useWidth / d; x++) {
        for (var y = 0; y < useHeight / d; y++) {
            var frameIndex = (y * (useWidth / d) + x)*3;
            for (var ii = 0; ii < d; ii++) {
                for (var jj = 0; jj < d; jj++) {
                    var pixelIndex = ((useTop + jj + y*d) * width + useLeft + ii + x*d)*4;
                    imageData[pixelIndex] = rawframe[frameIndex];
                    imageData[pixelIndex + 1] = rawframe[frameIndex + 1];
                    imageData[pixelIndex + 2] = rawframe[frameIndex + 2];
                    imageData[pixelIndex + 3] = 255;
                }
            }
        }
    }

    context.clearRect(0, 0, width, height);
    context.putImageData(new ImageData(imageData, width, height), 0, 0);

    fpsCount++;
    if (fpsCount % 10 === 0) {
        t2 = Date.now();
        console.log(fpsCount, (t2 - t1)/1000, 1000*fpsCount / (t2 - t1));
    }

    currentt = Date.now();
    costt = currentt - startt;

    setTimeout(function () {
        if (count === fcount || eof) {
            t2 = Date.now();
            console.log(fpsCount, (t2 - t1)/1000, 1000*fpsCount / (t2 - t1));
            return;
        }

        renderFrame(count + 1);
    }, Math.max(1, fpsDelay - costt));
}

function handleFileSelect(event) {
    var fileInput = event.target;
    var file = fileInput.files[0];

    if (!file) {
        return;
    }

    var reader = new FileReader();
    reader.onload = function (e) {
        fileContent = new Uint8Array(e.target.result);
        showFileContent(fileContent);
    };

    reader.readAsArrayBuffer(file);
}

function showFileContent(fileContent) {
    bytePerFrame = Math.ceil((useHeight * useWidth) / (d ** 2 * 8)) * color - (4 + 4 + 8 + 4 + 4);

    fcount = Math.ceil(fileContent.length / bytePerFrame);
    console.log('filesize', fileContent.length, 'fcount', fcount);

    fileSizeB = int2byte(fileContent.length,8);
    
    fpsDelay = Math.ceil(1000 / fpsSet);
    fpsCount = 0;
    eof = false;

    toggleFullScreen()
    setTimeout(() => {
        t1 = Date.now();
        renderFrame(0);
    }, 5000);

}
```

## Protocol

For instance, using a region of 1920-64,1080, with the right side reserved for the mouse (64 width is removed for convenience):

The frame rate on the capture end needs to be greater than the output end, set at 4 frames/s.

Each point is duplicated into a 2x2 grid, storing 1 bit of information.

The protocol starts with 4 bytes indicating the current frame number, followed by 4 bytes for the effective byte count in the current frame, then 8 bytes indicating the total byte count, followed by 4 bytes for the XOR of the header section. After that comes the data section, and after the effective length, 4 more bytes are appended to calculate the XOR of the data section.

`((1920-64)/2)*(1080/2)*1/8-(4+4+8+4+4)=62616`

| Byte Count | 4 | 4 | 8 | 4 | 62616 | 4 |
|------------|---|---|---|---|-------|---|
| Content    | Current Frame | Effective Byte Count | Total Byte Count | Header XOR | File Content | Content XOR |

## 协议

例如使用 1920-64,1080 的区域, 右边用来放鼠标, (为了方便直接切掉了64宽度的一整条)

采集端的帧率需要大于输出端, 暂定为4帧/s

每个点重复成2x2的格子, 储存1比特的信息

开头4字节当前第几帧, 再4字节本帧的有效字节数, 再8字节表明总字节数, 再4字节head部分的xor, 然后是数据部分, 有效长度之后再补4字节用来算数据部分的xor

`((1920-64)/2)*(1080/2)*1/8-(4+4+8+4+4)=62616`

|字节数|4|4|8|4|62616|4|
|-|-|-|-|-|-|-|
|内容|当前帧数|本帧有效字节数|文件总字节数|协议头的校验|文件内容|文件内容的校验|

## Implementation

Currently, a simplified implementation has been done for storing 1 bit in a 2x2 grid and 3 bits in a 4x4 grid. The cheapest HDMI in + HDMI out + USB 3.0 capture card, priced at RMB129, has considerable compression, reaching this level, and the fps can only go up to 5. For the combination of storing 3 bits in a 4x4 grid, each frame's information is 3/4 of storing 1 bit in a 2x2 grid.

[Transmission End (JavaScript)](psend1.html) or [Transmission End (Python for debugging)](psend1.py)  
[Reception End](precieve1.py)

## 实现

目前简略实现了 2x2的格子储存1比特 和 4x4的格子储存3比特 ,最便宜的 hdmi in + hdmi out + usb3.0 的 RMB129的采集卡, 压缩的比较多, 只能到这种程度了, 而且fps只能到5. 4x4的格子储存3比特 的组合的话每帧的信息是 2x2的格子储存1比特 的3/4.

发送端[js](psend1.html) 或者 [py(用于调试)](psend1.py)  
[接收端](precieve1.py)  

## Results

Successfully transmitted a 60,448,768-byte file in 247 seconds.

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

## Disclaimer/免责声明

Please thoroughly read and understand the following disclaimer as it forms part of the legal agreement of your use of this project and its related files and content (collectively referred to as "the Resources").
When utilizing these Resources, you must abide by all applicable laws and best practices. It is solely your responsibility to ensure that your usage does not infringe any third party's rights, including but not limited to privacy, intellectual property, and any other ownership or legal rights.

请仔细阅读并理解以下免责声明条款，因为它们是您使用本项目及其相关文件和内容（统称为“资源”）的法律协议的一部分。
使用这些资源时，您必须遵守所有适用的法律和最佳实践。您独立负责确保您的使用方式不侵犯任何第三方的权利，包括但不限于隐私权、知识产权和任何其他所有权或法律权利。

### Lawful Use/**使用合规性**

You agree and undertake to use these Resources only for lawful purposes, and within the restrictions and guidelines set by applicable laws and regulations. You must ensure that your conduct with respect to the Resources is compliant with the laws of the country you reside in and/or the country from where you use these Resources. You must not use the Resources in a way that violates these laws or engage in conduct that is unethical. Your use of the provided Resources must align with all relevant laws and regulations of your jurisdiction. These Resources are meant purely for technical demonstration and must not be utilized for any illegal activity or acts infringing on the rights of others.

您同意并承诺，只将这些资源用于合法目的，并在适用法律、法规和实践中制定的限制和指导方针内使用这些资源。您必须确保您的行为遵守您所在国家/地区和/或您的使用这些资源的国家/地区适用的所有法律。您不得使用这些资源去违法这些法律或从事不道德的活动。在使用所提供的资源时，您必须确保您的行为符合您所在国家/地区的所有相关法律和法规。这些资源仅为技术展示，不得用于任何非法活动或侵犯他人权利的行为。

### **Limitation of Liability**/**责任限制**

The provision of code is simply for offering design reference and technical insight, and will not be responsible for any direct, indirect, incidental, special, punitive, or consequential damages that arise from the use of these Resources. You understand and agree that you are solely responsible for the consequences of your use of these Resources, whether good or bad.

提供代码只是在提供设计参考和技术分享，不对任何因使用这些资源而引发的直接、间接、附带、特殊、惩罚性或后果性损害负责。您理解并同意您自己负责使用这些资源的后果，无论是好是坏。

### As-Is Basis/**无担保**

The Resources are provided on an "AS IS" basis, without any form of warranty expressed or implied. If you encounter bugs or any other form of tech gremlins, consider it as part of the adventure. This technology was conceived in the pursuit of pushing the boundaries of visual transmission capabilities, born purely from a technical testing ground.

这些资源是按“原样”提供的，没有任何形式的明示或暗示担保。如果你们遇到bug或其他奇怪的技术缺陷，那就是命中注定🙂。这项技术是在探索视觉传输能力的边界时构思出来的，它的诞生完全出于一个技术试验。

### Your Code, Your Responsibility/**自己的代码自己负责**

This isn't a toolkit for digital dark arts. Remember with every keystroke, you wield the power to impact the real world with responsibilities attached. There's no Gandalf here to carry your burdens if you find yourself in a pickle. Whatever your decision on how to use this tech wizardry, you must bear the consequences, because crossing the streams can lead to a WOPR of a problem.

这不是一个犯罪的工具包。希望你记住，伴随着你的每一个字符，都是影响现实世界的潜力和责任。没有谁会为你的麻烦背锅。无论你决定怎么用这玩意，一切后果都归你管，走火入魔可不是件好事。

### **Your Actions, Your Response-Ability**/**你的行为，你的责任**

If you flirt with the legal red tape or turn this project into the genesis of an issue, it's on you to carry that Infinity Gauntlet. Always ensure that your actions are safe, lawful, and reasonable. Do not let your quest turn into a cautionary tale.

如果你不小心碰到了法律的红线，或者使得这个项目成为问题的根源，那么，你得自己担着。请务必确保你的所作所为是安全、正当、合理的。别让你的探险落得一个糟糕的结局。

### EOF/最后的忠告

Never forget the gravity of what you're doing - be aware of the potential consequences. Safety is the prime directive, and whatever tech enchantment you're conjuring, always respect and adhere to the law of the code... and the code of the law.

永远不要忘记你在做什么，了解可能的后果。安全永远是首要原则，无论你在致力于何种技术创新，都应当尊重并遵循法律。