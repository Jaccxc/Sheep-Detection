import os
import glob

pth = glob.glob('C:\\Users\\User\\Desktop\\sheep_image\\*')

day = 0
night = 0

for entity in pth:
    hour = int(entity[39:41])

    if hour < 6 or hour > 18:
        night+=1

    else: 
        day+=1

print(f'Total images: {day+night}, Day split: {day}, Night split: {night}')