# Utils: project-wide utilities and logging wrappers.
# Logging convention: TAG must be the current class name constant; msg must be a str()-able object.
# Call template: Utils.LogD(self.TAG, ("%s: + " % (sys._getframe().f_code.co_name)))
# Severity levels (high to low): LogE(0) / LogI(1) / LogD(2) / LogV(3); controlled by gLogLevel.

from enum import Enum
import inspect

gLogLevel = 1

class Utils(object):
    mLogLevel = 3
    __instance = None

    def __init__(self):
        pass

    def LogE(TAG, msg):
        if gLogLevel >= 0:
            print("[ERROR  ]: " + TAG + ":" + inspect.stack()[1][3] + ":" + "".join(map(str, msg)))

    def LogI(TAG, msg):
        if gLogLevel >= 1:
            print("[INFO   ]: " + TAG + ":" + inspect.stack()[1][3] + ":" + "".join(map(str, msg)))

    def LogD(TAG, msg):
        if gLogLevel >= 2:
            print("[DEBUG  ]: " + TAG + ":" + inspect.stack()[1][3] + ":" + "".join(map(str, msg)))

    def LogV(TAG, msg):
        if gLogLevel >= 3:
            print("[VERBOSE]: " + TAG + ":" + inspect.stack()[1][3] + ":" + "".join(map(str, msg)))

class MsgType(Enum):
    LeftButton = 0x8000
    WheelMouse = LeftButton + 1
    HoverMove = LeftButton + 2

    KeyShift = 0x8100
    KeyCtrl = KeyShift + 1

class ComMsg(object):

    def __init__(self, type, value):
        self.mType = type
        self.mValue = value

    def getMsg(self):
        return self.mType, self.mValue

    def getType(self):
        return self.mType

    def getValue(self):
        return self.mValue