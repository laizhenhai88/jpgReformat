import struct
import shutil
import os
import zipfile
import time
from collections import defaultdict

path = 'd.jpg'
keys_count = 0
v = None

def typeAna(t):
    if t == 1:
        return (1,'byte')
    if t == 2:
        return (1,'char')
    if t == 3:
        return (2,'int')
    if t == 4:
        return (4,'long')
    if t == 5:
        return (8,'long/long')

def anaJpg(_path):
    global path,v
    path = _path

    img = tree(0)
    Total_Size = os.path.getsize(path)
    print('Total_Size:', Total_Size)
    v = open(path,"rb")

    img['type'] = b'root'
    # size包括type+size+data
    img['size'] = Total_Size + 4
    # value_size包括size+data
    img['value_size'] = Total_Size + 2
    # filepoint从type后开始，因为有的type没有size也没有data，奇葩
    img['filepoint'] = -2

    imgInfo(img)

    v.close()
    return img

def tree(deep):
    t = defaultdict()
    t['children'] = []
    t['deep'] = deep
    return t

def ana(node):
    global keys_count,v
    # 开始解析
    if node['type'] in [b'moov',b'trak',b'mdia',b'meta']:
        # 需要继续展开的
        imgInfo(node)
        return

    print('\033[1;35;40m', end='')
    if node['type'] in ['app1']:
        size, = struct.unpack('!H',v.read(2))
        print(node['deep']*4*' ', 'size', size)
        s4, = struct.unpack('4s',v.read(4))
        if s4 == b'Exif':
            print(node['deep']*4*' ', s4)
            v.seek(2,1)
            start = v.tell()
            print('tiff start', v.tell())
            # MM
            print(node['deep']*4*' ', struct.unpack('2s',v.read(2)))
            # 42
            print(node['deep']*4*' ', struct.unpack('!H',v.read(2)))
            # 8
            print(node['deep']*4*' ', 'offset', struct.unpack('!I',v.read(4)))
            # IFD
            while(True):
                ifd = []
                count, = struct.unpack('!H',v.read(2))
                print(node['deep']*4*' ', 'DE count', count)
                for i in range(count):
                    print()
                    print(node['deep']*4*' ', 'DE - ', i+1)
                    tag, = struct.unpack('!H',v.read(2))
                    print(node['deep']*4*' ', 'tag', hex(tag))
                    t, = struct.unpack('!H',v.read(2))
                    print(node['deep']*4*' ', 'type', t, typeAna(t)[1])
                    count, = struct.unpack('!I',v.read(4))
                    print(node['deep']*4*' ', 'count', count)
                    if typeAna(t)[0]*count > 4:
                        point, = struct.unpack('!I',v.read(4))
                        print(node['deep']*4*' ', 'point', count)
                        ifd.append((t, count))
                    else:
                        # 占用的字节数少于4,则数据直接存于此
                        print(node['deep']*4*' ', 'value', struct.unpack('4s',v.read(4)))
                nextIfd, = struct.unpack('!I',v.read(4))
                print(node['deep']*4*' ', 'next ifd offset', nextIfd)
                for i in ifd:
                    t,count = i
                    if t == 1 or t == 2:
                        print(node['deep']*4*' ', 'value', struct.unpack('%ds'%(count),v.read(count)))
                    if t == 3:
                        print(node['deep']*4*' ', 'value', struct.unpack('!%dH'%(count),v.read(count*2)))
                    if t == 4:
                        print(node['deep']*4*' ', 'value', struct.unpack('!%dI'%(count),v.read(count*4)))
                    if t == 5:
                        print(node['deep']*4*' ', 'value', struct.unpack('!I',v.read(4)), '/', struct.unpack('!I',v.read(4)))

                if nextIfd == 0:
                    break
                else:
                    v.seek(start+nextIfd,0)
            print(v.tell(), node['filepoint'] + node['value_size'])


            v.seek(node['filepoint'] + node['value_size'],0)
        else:
            v.seek(-4,1)
            print(node['deep']*4*' ', struct.unpack('%ds' % (node['value_size']-2),v.read(node['value_size']-2)))
    elif node['type'] in ['dri']:
        size, = struct.unpack('!H',v.read(2))
        print(node['deep']*4*' ', 'size', size)
        # print(node['deep']*4*' ', struct.unpack('%ds' % (node['value_size']-2),v.read(node['value_size']-2)))
        print(node['deep']*4*' ', struct.unpack('!H',v.read(2)))
    elif node['type'] in [b'mvhd']:
        print(node['deep']*4*' ', 'version', struct.unpack('B',v.read(1)))
        print(node['deep']*4*' ', 'flag', struct.unpack('3B',v.read(3)))
        time_int, = struct.unpack('!I',v.read(4))
        # time保存的是0时区的时间
        print(node['deep']*4*' ', 'creation time:[北京时间]', time.strftime('%Y-%m-%d %X',time.gmtime(time_int -2082844800 + 8*60*60)))
        time_int, = struct.unpack('!I',v.read(4))
        print(node['deep']*4*' ', 'modification time:[北京时间]', time.strftime('%Y-%m-%d %X',time.gmtime(time_int -2082844800 + 8*60*60)))
        ts, = struct.unpack('!I',v.read(4))
        print(node['deep']*4*' ', 'time scale', ts)
        d, = struct.unpack('!I',v.read(4))
        print(node['deep']*4*' ', 'duration', d, '时间s:', d/ts)
        print(node['deep']*4*' ', 'rate', struct.unpack('!H',v.read(2))[0], '.', struct.unpack('!H',v.read(2))[0])
        print(node['deep']*4*' ', 'volumn', struct.unpack('B',v.read(1))[0], '.', struct.unpack('B',v.read(1))[0])
        print(node['deep']*4*' ', 'reserved', struct.unpack('10B',v.read(10)))
        print(node['deep']*4*' ', 'matrix', struct.unpack('9I',v.read(36)))
        print(node['deep']*4*' ', 'preview time', struct.unpack('!I',v.read(4)))
        print(node['deep']*4*' ', 'preview duration', struct.unpack('!I',v.read(4)))
        print(node['deep']*4*' ', 'poster time', struct.unpack('!I',v.read(4)))
        print(node['deep']*4*' ', 'selection time', struct.unpack('!I',v.read(4)))
        print(node['deep']*4*' ', 'selection duration', struct.unpack('!I',v.read(4)))
        print(node['deep']*4*' ', 'current time', struct.unpack('!I',v.read(4)))
        print(node['deep']*4*' ', 'next track id', struct.unpack('!I',v.read(4)))
    else:
        # b'wide',b'mdat',b'udta',b'free',b'tapt',b'edts',b'hdlr',b'minf',b'tref'
        v.seek(node['value_size'],1)
        print(node['deep']*4*' ', 'pass...')

    print('\033[0m', end='')

def passFF():
    p, = struct.unpack('B',v.read(1))
    if p == 0xff:
        passFF()
    else:
        v.seek(-1,1)

def nextIsFF():
    p, = struct.unpack('B',v.read(1))
    v.seek(-1,1)
    return p == 0xff

def jfif_head(b):
    if b == 0xd8:
        return 'soi'
    if 0xe0 <= b and b <= 0xef:
        return 'app%d' % (b-0xe0)
    if b == 0xdb:
        return 'dqt'
    if b == 0xdd:
        return 'dri'
    if b == 0xda:
        return 'sos'
    if 0xc0 <= b and b <= 0xcf:
        return 'sof%d' % (b-0xc0)
    return hex(b)

# 深度优先
def imgInfo(node):
    while True:
        child = tree(node['deep']+1)
        node['children'].append(child)

        passFF()
        head, = struct.unpack('B',v.read(1))
        size = 0
        if not nextIsFF():
            size, = struct.unpack('!H',v.read(2))
            v.seek(-2,1)

        child['type'] = jfif_head(head)
        child['value_size'] = size
        child['size'] = child['value_size'] + 2
        child['filepoint'] = v.tell()
        print(node['deep']*4*' ','+', child['type'], child['size'])
        ana(child)
        if child['type'] == 'sos':
            break
        if v.tell() == node['filepoint'] + node['value_size']:
            break

if __name__=="__main__":
    anaJpg(path)
