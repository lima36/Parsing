#-*- coding:utf-8 -*-

import webbrowser, os
from tkinter import *
from tkinter import filedialog
import pandas as pd
import re
log_field = ['date', 'time', 't-velocity', 'r-velocity', 'position', 'destination', 'floor', 'action status', 'command']

# path="."
# webbrowser.open(os.path.realpath(path))

def listdir(dir):
    filenames = os.listdir(dir)
    for files in filenames:
        print(files)

#[w_],930952,-0.100000,0.000000,-0.100000,0.000000,1608802481956,
# 0.000000,0.000000,0.000000,0.000000,
# -1.098270,1.849469,34.961075,
# 350,
# 31,  31,209,
# 204,
# ActionSrv,
# 0.000000,0.000000,0.000000,
# -1.514800,1.980600,35.000000,
# 1,1,
# 0,0,

micom_info = ["nCount", "T_dTVel", "T_dRVel", "R_dTVel", "R_dRVel", "lgrpTime",
                "TransVel", "RotVel", "WheelVelLeft", "WheelVelRight",
                "Pose.fXM", "Pose.fYM", "Pose.fDeg",
                "IMU.nAngleZ",
                "MotorStatus0", "MotorStatus1",
                "RecvPacketIndex", "PreRecvPacketIndex",
                "TargetName",
                "Wheel.fDelX", "Wheel.fDelY", "Wheel.fDelThDeg",
                "Wheel.fX", "Wheel.fY", "Wheel.fThDeg",
                "LidarDetectState", "SonarDetectState",
                "ECUState1", "ECUState2",]

ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
regex = r'\[(\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6})\] <(\w*)> \[(.*)\](.*)'
action = r'\[(\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6})\] <(\w*)> \[(ExtInterfaceService)\]( Current Action Status .*)'
position = r'\[(\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6})\] <(\w*)> \[(w_)\],(.*)'
def filterInLogfile(filePath, regStr):
    timestamp = r'\[(\d{2}-\d{2} \d{2}:\d{2}:\d{2}.\d{6})\]'
    pActionStatus = None
    pPosition = None
    searchlist = []
    with open(filePath, 'r') as logFile:
        for line in logFile:
            line = ansi_escape.sub('', line)
            matchobj = re.search(regStr, line)
            if matchobj is not None:
                iActionStatus = re.search(action, line)
                iPosition = re.search(position, line)

                if iActionStatus is not None:
                    if iActionStatus.group(4) != pActionStatus:
                        print(line)
                        searchlist.append(line)
                    pActionStatus = iActionStatus.group(4)
                elif iPosition is not None:
                    position_infos = iPosition.group(4).split(",")
                    if pPosition is None:
                        print(line)
                        searchlist.append(line)
                    else:
                        for n in [1, 2, 3, 4, 6, 7, 8, 9, 10]:
                            if position_infos[n] != pPosition[n]:
                                print(line)
                                searchlist.append(line)
                                break
                    pPosition = iPosition.group(4)
    return searchlist


#[12-24 00:31:13.556897] <info> [joy_] Failure to open the joystick driver!!!
#[12-24 18:35:16.340704] <info> ActionMove2Goal :0, 21 || 17.9054,14.3492,17.9081,14.3408,18.005,14.3717,, 5.92039, 0.2005, 0.00284427, 1
def logFile2DataFrame(filePath):
    dfLog = pd.DataFrame(columns=['Timestamp', 'Level', 'Module', 'Message'])
    with open(filePath, 'r') as logFile:
        numRows = -1
        for line in logFile:
            line = ansi_escape.sub('', line)
            matchobj = re.search(regex, line)
            if matchobj is not None:
                timestamp = matchobj.group(1)
                level = matchobj.group(2)
                module = matchobj.group(3)
                message = matchobj.group(4)
                numRows += 1
                dfLog.loc[numRows] = [timestamp, level, module, message]
                print(numRows)
            else:
                # print (hex(int(line, base=16)))
                pass#print(line)
            # #     # Multiline message, integrate it into last record
            #     dfLog.loc[numRows, 'Message'] += line
    return dfLog


root = Tk()
root.geometry("800x600")
# root.filename = filedialog.askopenfilename(initialdir=".", title="choose log file", filetypes=(("log files", "*.log"), ("all files","*.*")))

def openDirectory():
    print("openDirectory")
    root.filename = filedialog.askopenfilename(initialdir=".", title="choose log file",
                                               filetypes=(("log files", "*.log"), ("all files", "*.*")))


def startParse():
    founds =filterInLogfile(root.filename, textReg.get().strip())#r"w_|eAction")

    for t in founds:
        logText.insert(END, t + "\n")
    # textExample.delete(0,"end")
    # textExample.insert(0, text)


textReg = Entry(root)
textReg.pack()

btnOpen = Button(root, height=1, width=10, text="Open", command=lambda:openDirectory())
btnOpen.pack()

btnSet = Button(root, height=1, width=10, text="Parsing", command=lambda:startParse())
btnSet.pack()

logText = Text(root, height=10, width=30)
logText.pack()

root.mainloop()

# pd_data = logFile2DataFrame(root.filename)
# print(pd_data['Module'])