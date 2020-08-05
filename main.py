#!/usr/bin/env python

from gpiozero import LED, Button
from time import sleep
from re import search
from multiprocessing.pool import Pool
import subprocess
import sys
import os
import signal
import mmap

ledGreen = LED(18)
ledRed = LED(17)
button = Button(3)
powerButton = Button(2)

readyToProgramState = False

def isReadyToProgram():
    global readyToProgramState
    return readyToProgramState

def setReadyToProgramState(state):
    global readyToProgramState
    readyToProgramState = state

def getBinFilesFromDir(dir):
    imageFiles = []
    for file in os.listdir(dir):
        if file.endswith(".bin"):
            imageFiles.append(file)
    return imageFiles

def isValidNumOfBinFiles(files):
    if len(files) == 0:
        return False
    if len(files) > 1:
        return False
    return True

def deleteFilesInCurrentDir(files):
    for file in files:
        os.remove(file)

def ledsBlink(leds, secondDelay):
    ledsOn(leds)
    sleep(secondDelay)
    ledsOff(leds)
    sleep(secondDelay)

def ledsOn(leds):
    for led in leds:
        led.on()

def ledsOff(leds):
    for led in leds:
        led.off()

def programmingLedsRun():
    leds = [ledGreen, ledRed]
    for _ in range(0, 600):
        ledsBlink(leds, 0.1)

def tryGetMountedSda():
    proc = subprocess.Popen(['ls', '/media'], stdout=subprocess.PIPE)
    output = proc.stdout.read()
    mountedSda = []
    for i in range(1, 5):
        sdaString = "sda" + str(i)
        if search(sdaString, output):
            mountedSda.append(i)
        ledsBlink([ledRed], 0.1)
    return mountedSda

def tryMountSda():
    mountedSdaIdx = []
    for i in range(1, 5):
        sdaxStr = "sda" + str(i)
        proc = subprocess.Popen(['pmount', sdaxStr], stderr=subprocess.PIPE)
        output = proc.stderr.read()
        if not search("Error", output):
            mountedSdaIdx.append(i)
        ledsBlink([ledRed], 0.1)
    return mountedSdaIdx

def mountSda(index):
    sdaxStr = "sda" + str(index)
    subprocess.call(['pmount', sdaxStr])
    ledsBlink([ledRed], 0.1)

def unmountSda(index):
    sdaxStr = "sda" + str(index)
    subprocess.call(['pumount', sdaxStr])
    ledsBlink([ledRed], 0.1)

def tryGetBinFilesFromUSBDrive():
    mountedSda = tryGetMountedSda()
    archive = {}
    if not len(mountedSda):
        mountedSda = tryMountSda()
    if len(mountedSda):
        for i in mountedSda:
            sdaxDir = "/media/" + "sda" + str(i)
            files = getBinFilesFromDir(sdaxDir)
            if len(files):
                for file in files:
                    if i not in archive:
                        archive[i] = [file]
                    else:
                        archive[i].append(file)
        # unmount all usb drive
        for i in mountedSda:
            unmountSda(i)
    return archive

def loadBinToFlash(binFile):
    result = False
    print("[LOADING] " + binFile)
    pool = Pool(processes=1)
    pool.apply_async(programmingLedsRun)
    programCmd = 'program ' + binFile + ' verify reset exit 0'
    command = 'sudo openocd -l temp.txt -f board/vertexcom-cm3.cfg -c "' + programCmd + '"'
    subprocess.call(command, shell=True)
    with open('temp.txt') as f:
        s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        if s.find('Verified OK') != -1:
            result = True
        f.close()
    pool.terminate()
    pool.join()
    if result == True:
        ledsOn([ledGreen])
        ledsOff([ledRed])
        print("[DONE] " + binFile + " succesfully loaded")
    else:
        ledsOn([ledRed])
        ledsOff([ledGreen])
        f = open('temp.txt', 'r')
        temp_contents = f.read()
        print(temp_contents)
        f.close()
        print("[ERROR] " + binFile + " failed to  load")
    subprocess.call("sudo rm temp.txt", shell = True)
    sleep(0.2)

def buttonPressedHandler(button):
    if isReadyToProgram():
        currentDir = os.getcwd()
        binFiles = getBinFilesFromDir(currentDir)
        sleep(0.5)
        act = button.is_active
        # check whether or not the button is pressed for 5 seconds
        sleep_count = 1
        while sleep_count < 10:
            sleep_count += 1
            sleep(0.5)
            act = button.is_active
            if not act:
                break
        if act:
            ledsOff([ledGreen])
            archiveFiles = tryGetBinFilesFromUSBDrive()
            if len(archiveFiles) != 0:
                print("[UPDATE] *.bin file in " + str(currentDir))
                deleteFilesInCurrentDir(binFiles)
                setReadyToProgramState(False)
            else:
                ledsOn([ledGreen])
                print("[WARNING] no usb-drive is detected to update the *.bin file or *.bin file doesn't exist on usb-drive")
        else:
            loadBinToFlash(binFiles[0])

def powerButtonPressedHandler(button):
    sleep(3)
    act = button.is_active
    if act:
        for _ in range(10):
            ledsBlink([ledRed, ledGreen], 0.1)
        ledsOff([ledRed, ledGreen])
        subprocess.call("sudo shutdown -h now", shell=True)
        sys.exit()

def main():
    while True:
        currentDir = os.getcwd()
        binFiles = getBinFilesFromDir(currentDir)
        if isValidNumOfBinFiles(binFiles):
            ledsOn([ledGreen])
            setReadyToProgramState(True)
            print("[READY] " + str(binFiles[0]))
            while isReadyToProgram():
                if button.is_pressed:
                    buttonPressedHandler(button)
                    sleep(0.1)
                elif powerButton.is_pressed:
                    powerButtonPressedHandler(powerButton)
            ledsOff([ledGreen])
        else:
            if len(binFiles) > 0:
                print("[WARNING] multiple *.bin file in current directory, delete all")
                deleteFilesInCurrentDir(binFiles)
            archiveFiles = tryGetBinFilesFromUSBDrive()
            if len(archiveFiles):
                for i in archiveFiles:
                    mountSda(i)
                    for file in archiveFiles[i]:
                        fileToCopy = "/media/sda" + str(i) + "/" + str(file)
                        subprocess.call(['cp', fileToCopy, '.'])
                    unmountSda(i)
            binFiles = getBinFilesFromDir(currentDir)
            if len(binFiles) == 0:
                print("[WARNING] *.bin file does not exist")


def exitGracefully(signum, frame):
    signal.signal(signal.SIGINT, original_sigint)
    print("\nYou pressed Ctrl+C!\n")
    try:
        if raw_input("Are You sure want to exit? (y/n)> ").lower().startswith('y'):
            sys.exit(1)

    except KeyboardInterrupt:
        print("Exiting anyway")
        sys.exit(1)

    signal.signal(signal.SIGINT, exitGracefully)


if __name__ == "__main__":
    original_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, exitGracefully)
    main()
