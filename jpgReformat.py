# coding=utf-8
# 在线查看 https://exif.tuchong.com
import os
from sys import argv
import random
import shutil
import itertools
import uuid
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageColor
from props import readprops
import piexif
from props import readprops
import struct

print('读取 image')
if not os.path.exists('image'):
    print('image 文件夹不存在')
    exit(0)

print('清理dist')
if os.path.exists('dist'):
    shutil.rmtree('dist')
os.mkdir('dist')

props = readprops('reformat.props')

tSize = (160,120)
finalSize = (960,1280)
exif = piexif.load(open('exif.bin','rb').read())
# 根据props修改信息
exif['0th'][305] = struct.pack('%ds'%(len(props['productVersion'])),bytes(props['productVersion'],'utf-8'))
exif['0th'][306] = struct.pack('19s',bytes(props['time_str'].replace('-',':'),'utf-8'))
exif['Exif'][36867] = struct.pack('19s',bytes(props['time_str'].replace('-',':'),'utf-8'))
exif['Exif'][36868] = struct.pack('19s',bytes(props['time_str'].replace('-',':'),'utf-8'))
pt = props['productType'] + ' front camera 2.15mm f/2.4'
exif['Exif'][42036] = struct.pack('%ds'%(len(pt)),bytes(pt,'utf-8'))

def handleDir(sub):
    currDir = os.path.join('image', sub)
    for file in os.listdir(currDir):
        if file.find('.') == 0:
            print('pass hidden file %s' % file)
            continue
        if os.path.isdir(os.path.join(currDir,file)):
            os.mkdir(os.path.join('dist', sub, file))
            handleDir(os.path.join(sub, file))
        else:
            im = Image.open(os.path.join('image', sub, file))
            im_t = im.transpose(Image.ROTATE_90)
            im_t.thumbnail(tSize)
            im_t.save('im_t.jpg','jpeg')
            tbin = open('im_t.jpg','rb').read()
            exif['thumbnail'] = tbin

            im = im.resize(finalSize)
            im = im.transpose(Image.ROTATE_90)
            im.save(os.path.join('dist', sub, str(uuid.uuid4()) + '.jpg'), 'jpeg', exif=piexif.dump(exif))
            os.remove('im_t.jpg')

handleDir('')
