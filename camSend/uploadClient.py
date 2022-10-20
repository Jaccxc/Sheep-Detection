from ftplib import FTP
import glob
import os
import datetime

HOST = 'jacc.tw'
PORT = 2121
USR = 'username'
PWD = 'password'

ftp = FTP()
ftp.connect(HOST, PORT)
ftp.login(USR, PWD)

while(1):
    data = glob.glob('record/raw*.mp4')
    if data == []:
        print('No file now')
        break

    #print(data)
    #print(os.path.basename(data[0]))
    
    fullPath = data[0]
    fileName = os.path.basename(fullPath)
    renameFullPath = 'record/' + 'cache' + fileName[3:]

    startTime  = datetime.datetime.now()
    file = open(f'{fullPath}','rb')                  # file to send
    ftp.storbinary(f'STOR {fileName}', file)     # send the file
    file.close()
    endTime = datetime.datetime.now()

    elapsed = endTime - startTime

    print('=================================================')
    print(f'Data transmitted : {fileName}')
    print(f'Renaming to: {renameFullPath}')
    print(f'Start time: {startTime}, End time: {endTime}')
    print(f'Total time elapsed: {elapsed}')
    print('=================================================')
    
    os.rename(fullPath, renameFullPath)
    

                                   # close file and FTP
ftp.quit()