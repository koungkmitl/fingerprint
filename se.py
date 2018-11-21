from pyfingerprint.pyfingerprint import PyFingerprint
import time
import sys
from tinydb import TinyDB, Query

"""
Powered by Kim Lee

compareCharacteristics to compare buf1 and buf2 | return accuracy score. if == 0: bad
downloadCharacteristics to retrn list and store list to tinyDB | return list and store list
uploadCharacteristics to upload | return true is it right
"""

try:
    f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)

    if ( f.verifyPassword() == False ):
        raise ValueError('The given fingerprint sensor password is wrong!')

    db = TinyDB('db.json')
    query = Query()
except Exception as e:
    print('The fingerprint sensor could not be initialized!')
    print('Exception message: ' + str(e))
    exit(1)

def enrollFinger():
    stdId = input('Mode 1) Input your student identification: ')

    queryResult = db.search(query.stdId == stdId)
    if stdId == '' or len(stdId) != 8 or queryResult:
        print('Unprocessable Entity: student identification\n')
        sys.exit()

    print('Waiting for finger...\n')

    while f.readImage() == False:
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)

    print('Remove finger...\n')
    time.sleep(2)

    print('Waiting for same finger again...\n')

    ## Wait that finger is read again
    while f.readImage() == False:
        pass

    ## Converts read image to characteristics and stores it in charbuffer 2
    f.convertImage(0x02)

    ## Compares the charbuffers
    if f.compareCharacteristics() == 0:
        raise Exception('Fingers do not match')

    ## Creates a template
    f.createTemplate()
    finger = f.downloadCharacteristics()

    # insert to database
    db.insert({'finger': finger, 'stdId': stdId})
    print('Finish without problem')

def repeatFinger():
    stdId = input('Mode 2) Input your student identification: ')

    if stdId == '' or len(stdId) != 8:
        print('student identification is bad format\n')
        sys.exit()

    queryResult = db.search(query.stdId == stdId)

    if not queryResult:
        print('Not found student identification')
        sys.exit()
    
    print('Waiting for finger...\n')

    while f.readImage() == False:
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)

    print('Remove finger...\n')
    time.sleep(2)

    print('Waiting for same finger again...\n')

    ## Wait that finger is read again
    while f.readImage() == False:
        pass

    ## Converts read image to characteristics and stores it in charbuffer 2
    f.convertImage(0x02)

    ## Compares the charbuffers
    if f.compareCharacteristics() == 0:
        raise Exception('Fingers do not match')

    ## Creates a template
    f.createTemplate()
    finger = f.downloadCharacteristics()

    db.update({'finger': finger}, query.stdId == stdId)
    print('Finish without problem')

def study():
    print('Mode 3) Waiting for finger...\n')

    while ( f.readImage() == False ):
        pass

    ## Converts read image to characteristics and stores it in charbuffer 1
    f.convertImage(0x01)

    queryResult = db.all()
    for query in queryResult:
        f.uploadCharacteristics(charBufferNumber=0x02, characteristicsData=query['finger'])
        if f.compareCharacteristics() == 0:
            pass
        else:
            print('Found !! ' + str(query['stdId']) + '\n')
            time.sleep(2)
            break

txt = 'Select input \n  1) enroll new finger\n  2) verify finger\n  3) study\n\nSelect 1 or 2 or 3 '

state = input(txt)

try:
    if state == '1':
        while True: enrollFinger()
    elif state == '2':
        repeatFinger()
    elif state == '3':
        while True: study()
    else:
        raise KeyboardInterrupt('Input not match')
except Exception as e:
    print('Operation failed!')
    print('Exception message: ' + str(e))
    exit(1)
hello
