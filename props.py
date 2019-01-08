# coding=utf-8
import codecs
def readprops(file):
    # 参数设置
    props = {}
    fopen = codecs.open(file, 'r', 'utf-8')
    for line in fopen:
        line = line.strip()
        if line.find('=') > 0 and not line.startswith('#'):
            strs = line.split('=')
            props[strs[0].strip()] = strs[1].strip()
    return props
