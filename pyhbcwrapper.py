import ctypes, time
from ctypes import CDLL, byref, c_void_p, c_long,c_int, c_bool, c_char,c_char_p, c_double, POINTER, byref, create_string_buffer


class PyHBCWraperr:
    def __init__(self):
        self.lib = CDLL("./ClipXApi.dll")
        self.VOID = c_void_p
        self.handle = c_void_p()
        self.line = (c_double*7)()
        self.time = c_double()
        self.fx = c_double()
        self.fy = c_double()
        self.fz = c_double()
        self.tx = c_double()
        self.ty = c_double()
        self.tz = c_double()
        self.buf = ctypes.create_string_buffer(b'\0'*11)

    
    def connect(self):  
        self.lib.ClipX_Connect.argtypes = [c_char_p]
        self.lib.ClipX_Connect.restype = self.VOID
        self.handle = self.lib.ClipX_Connect('192.168.1.22'.encode('utf-8'))

    def sdoRead(self):
        self.lib.ClipX_SDORead.argtypes = [self.VOID, c_int, c_int, c_char*12, c_int]
        return self.lib.ClipX_SDORead(self.handle, 0x4428, 8, self.buf, 12)#0x4428,8

    def sdoWrite(self, index, subindex, value):
        self.lib.ClipX_SDOWrite.argtypes = [self.VOID, c_int, c_int, c_char_p]
        return self.lib.ClipX_SDOWrite(self.handle, index, subindex, value.encode('utf-8'))

    def startMeasurement(self):
        self.lib.ClipX_startMeasurement.argtypes = [self.VOID]
        self.lib.ClipX_startMeasurement.restype = c_int
        return self.lib.ClipX_startMeasurement(self.handle)

    def availableLines(self):
        self.lib.ClipX_AvailableLines.argtypes = [self.VOID]
        self.lib.ClipX_AvailableLines.restype = c_int
        return self.lib.ClipX_AvailableLines(self.handle)

    def readNextLine(self):
        self.lib.ClipX_ReadNextLine.argtypes = [self.VOID, ctypes.c_double*7]
        self.lib.ClipX_ReadNextLine.restype = c_int
        self.lib.ClipX_ReadNextLine(self.handle, self.line)
        return self.line[1], self.line[2], self.line[3], self.line[4], self.line[5], self.line[6]

    def readNextBlock(self):
        self.lib.ClipX_ReadNextBlock.argtypes = [
            self.VOID, 
            c_int, 
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),
            POINTER(c_double),]
        self.lib.ClipX_ReadNextBlock.restype = c_int
        self.lib.ClipX_ReadNextBlock(self.handle, 1, byref(self.time), byref(self.fx), byref(self.fy), byref(self.fz), byref(self.tx), byref(self.ty), byref(self.tz))
        return float(self.fx.value), float(self.fy.value), float(self.fz.value), float(self.tx.value), float(self.ty.value), float(self.tz.value)
        


    def stopMeasurements(self):
        self.lib.ClipX_stopMeasurement.argtypes = [self.VOID]
        self.lib.ClipX_stopMeasurement.restype = c_int
        return self.lib.ClipX_stopMeasurement(self.handle)

    def disconnect(self):
        self.lib.ClipX_Disconnect.argtypes = [self.VOID]
        self.lib.ClipX_Disconnect.restype = c_int
        return self.lib.ClipX_Disconnect(self.handle)

    def isConnected(self):
        self.lib.ClipX_isConnected.argtypes = [self.VOID]
        self.lib.ClipX_isConnected.restype = c_bool
        return self.lib.ClipX_isConnected(self.handle)


if __name__ == "__main__":
    a = PyHBCWraperr()
    print("Connect:")
    a.connect()
    print("Handle:")
    print(a.handle)
    print("SDORead:")
    a.sdoRead()
    print("SDOWrite:")
    print(a.sdoWrite(0x4428, 8, '10'))
    print("Start Measurement:")
    print(a.startMeasurement())
    time.sleep(2)
    print("Available Lines:")
    print(a.availableLines())
    print("Read Next Line:")
    fx, fy, fz, tx, ty, tz = a.readNextLine()
    print(f"Fy: {fy}, Fz: {fz}")
    
    print("Read Next Block:")
    linesRead = 0
    while True:
        if a.availableLines() > 0:
            fx, fy, fz, tx, ty, tz = a.readNextLine()
            print(f"Fy: {fy}, Fz: {fz}")
            linesRead +=1
        if linesRead == 30:
            print("[SYSTEM]: Trying to tare ... ")
            time.sleep(0.1)
            res = a.sdoWrite(0x4411, 11)
            print(f"[SYSTEM]: Tare result: {res}")
        if linesRead == 150: 
            break

    print(f"Lines Readen {linesRead}")