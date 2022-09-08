import shutil
import random
import glob

src = 'C:\\Users\\User\\Desktop\\sheep_image\\'
dst = 'C:\\Users\\User\\Desktop\\training_goat\\'

all_data = glob.glob(src + '*')

day = 0
night = 0


for entity in all_data:
    hour = int(entity[39:41])
    filename = entity[34:51]
    full_pth = dst + filename
    
    state = None

    rnd = random.randint(0, 10000)

    if hour < 6 or hour > 18:
        if rnd <= 120:
            shutil.copyfile(src+filename, dst+filename)
            night += 1

    else: 
        if rnd <= 57:
            shutil.copyfile(src+filename, dst+filename)
            day += 1
    
    

print(f'Total image: {day+night}, Day split: {day}, Night split: {night}')
            

    

        

    

    


    
