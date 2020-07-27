'''
1. sort by time taken
2. filter out bad photos near start/end of flight
3. rename into something sensible (ren *.JPG *.jpg)
4. add exif data and compress

lon ~40 lat ~-79
https://xkcd.com/2170/
https://github.com/hMatoba/Piexif/blob/4ecc1cf66af51d0dafaa81bedc64de993feae31c/piexif/_exif.py yikes
'''

import piexif, piexif.helper, csv, math, os
from datetime import datetime, timedelta
from PIL import Image


os.chdir('D:\\pgh-skyglow-mapping\\exif')

with open('tracklog.csv', 'r') as inf:
    writer = csv.DictReader(inf)
    data = {row['time']:row for row in writer}

 
def dms2dd(dms):
    degrees, minutes, seconds = dms
    degrees = degrees[0] / degrees[1]
    minutes = minutes[0] / minutes[1]
    seconds = seconds[0] / seconds[1]
    dd = float(degrees) + float(minutes)/60 + float(seconds)/(60*60)
    return dd

def dd2dms(deg):
    d = int(deg)
    md = abs(deg - d) * 60
    m = int(md)
    sd = int(((md - m) * 60) * 10)
    return ((d,1), (m,1), (sd,10))

def hms2str(time):
    h, m, s = time
    h, m, s = (int(h[0] / h[1]), int(m[0] / m[1]), int(s[0] / s[1]))
    return '%02d:%02d:%02d' % (h, m, s)


for i in range(1,1608):
    exif_dict = piexif.load('in/image (%s).jpg' % i)
    im = Image.open('in/image (%s).jpg' % i)
    time = datetime.strptime(im._getexif()[36867], '%Y:%m:%d %H:%M:%S')
    time += timedelta(hours=4) # metadata time off by 4 hours for some reason idk
    timeStr = time.strftime('%H:%M:%S')
    while True:
        try:
            exif_dict['GPS'][piexif.GPSIFD.GPSLongitude] = dd2dms(abs(float(data[timeStr]['lon'])))
            exif_dict['GPS'][piexif.GPSIFD.GPSLatitude] = dd2dms(abs(float(data[timeStr]['lat'])))
            exif_dict['GPS'][piexif.GPSIFD.GPSLongitudeRef] = b'W'
            exif_dict['GPS'][piexif.GPSIFD.GPSLatitudeRef] = b'N'
            exif_dict['GPS'][piexif.GPSIFD.GPSAltitude] = (int(float((data[timeStr]['alt']))), 1)
            break
        except:
            print('+1 sec')
            time += timedelta(seconds=1)
            timeStr = time.strftime('%H:%M:%S')
    

    print(i,': ', time, ' ', data[timeStr]['alt'], ' ', (data[timeStr]['lon'], data[timeStr]['lat']))
    
    exif_bytes = piexif.dump(exif_dict)
    im.save('out/image (%s).jpg' % i, exif=exif_bytes)


