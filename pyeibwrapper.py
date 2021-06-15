#   A PYTHON WRAPPER FOR THE EIB7.DLL C LIBRARY

import ctypes
import time
from sys import getsizeof
from pystructs import DataPacketSection


class PyEIBWrapper():
    """
    A python wrapper for the eib7.dll C library.

    ...

    Attributes
    ----------
    pathToDll: str
        a str containing the path to the eib7.dll file.
    lib: cyptes.CDLL
        the CDLL object used to call eib7.dll functions.
    hostname: str
        a utf-8 encoded str containing the Heidenhain ip.
    ip: unsigned long
        decimal representation of the IP (hostname).
    axis: int array[4]
        integer array of 4 positions. Axis handle.
    eib: integer
        handle for the device.
    timeout: long
        timeout period in ms. Default is 2000ms
    num: unsigned long
        number of valid handles within the axis set.
    firmware: str
        firmware version.
    sizeOfFirmware: int
        size in bytes of the str containing the firmware version
    status: unsigned short
        status word.
    pos: int64
        position value 
    pos_double
        position value converted to double
    timestampTicks: unsigned long
        ticks per microsecond (timestamp)
    timestampPeriod: unsigned long
        period of timestamp
    TIMESTAMP_PERIOD: const int
        1000 microseconds or 1ms
    packet: DataPacketSection[5]
        Array of structs. Each struct contains the data of one of 
        the packet's regions. There are 5 -> Global, 3 main axis, aux axis.
    timerTicks: unsigned long
        timer ticks per microsecond.
    TRIGGER_PERIOD: int
        trigger period in microseconds.
    timerPeriod: unsigned long
        timer trigger period.
    udpData: unsigned char[200]
        buffer for udp data packet
    entries: unsigned long
        entreis read from the FIFO
    field: void pointer
        pointer to a data field
    sz: unsigned long
        size of a data field


    Methods
    -------
    Explained one by one at the start of their definition.
    """

    def __init__(self, pathToDLL):
        """Constructor method. It requires the path to the eib7.dll.
        Then, the librariy's methods can be called through the 
        attribute self.lib

        Parameters
        ----------
        pathToDLL: str
            a str containing the path to the eib7.dll file.
        """
        self.pathToDLL = pathToDLL
        self.lib = ctypes.CDLL(pathToDLL)
        self.hostname = '192.168.1.2'.encode('utf-8')
        self.ip = ctypes.c_ulong()
        self.axis = (ctypes.c_int*4)()
        self.eib = ctypes.c_int()
        self.timeout = ctypes.c_long(2000)
        self.num = ctypes.c_ulong()
        self.firmware = ctypes.create_string_buffer(b'\0'*19)
        self.sizeOfFirmware = getsizeof(self.firmware)
        self.status = ctypes.c_ushort()
        self.pos = ctypes.c_int64()
        self.pos_double = ctypes.c_double()
        self.packet = (DataPacketSection*5)()
        self.timerTicks = ctypes.c_ulong()
        self.TRIGGER_PERIOD = 500000
        self.udpData = (ctypes.c_ubyte*200)()
        self.entries = ctypes.c_ulong()
        self.field = ctypes.c_void_p()
        self.sz = ctypes.c_ulong()

    def getHostIp(self):
        """It converts the IP string into a decimal representation.
        The IP value is stored into `self.ip`.

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0. 
        """
        self.lib.EIB7GetHostIP.argtypes = [
            ctypes.c_char_p, ctypes.POINTER(ctypes.c_ulong)]
        self.lib.EIB7GetHostIP.restype = ctypes.c_uint
        return self.lib.EIB7GetHostIP(self.hostname, ctypes.byref(self.ip))

    def openConnection(self):
        """Opens a TCP/IP connection to the Heidenhain hardware. 

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.lib.EIB7Open.argtypes = [ctypes.c_ulong, ctypes.POINTER(
            ctypes.c_int), ctypes.c_long, ctypes.c_char*20, ctypes.c_ulong]
        self.lib.EIB7Open.restype = ctypes.c_uint
        return self.lib.EIB7Open(self.ip, ctypes.byref(self.eib), self.timeout, self.firmware, self.sizeOfFirmware)

    def getAxis(self):
        """Returns one handle for every axis of the eib. Handles
        would be stored in the `self.axis` array. The number of axis
        with valid handles would be sotred in `self.num`.

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.lib.EIB7GetAxis.argtypes = [
            ctypes.c_int, ctypes.c_int*4, ctypes.c_int, ctypes.POINTER(ctypes.c_ulong)]
        self.lib.EIB7GetAxis.restype = ctypes.c_uint
        return self.lib.EIB7GetAxis(self.eib, self.axis, ctypes.c_int(4), ctypes.byref(self.num))

    def initAxis(self, positions):
        """Initializes an axis to the specified encoder settings.

        Params
        ------
        positions: int list
            list conatining the positions of the axis to be initialized. 
            For example:
                init all of the axis -> positions = [0,1,2,3]
                init only axis 1-> positions = [1]
        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        zero = ctypes.c_int(0)
        one = ctypes.c_int(1)
        self.lib.EIB7InitAxis.argtypes = [
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_int,
        ]
        for x in positions:
            if type(x) is not int or x > 3 or x < 0:
                print(
                    "Invalid input arguments. Positions should be integers between 0 and 3")
                exit(0x60000009)
            else:
                err = self.lib.EIB7InitAxis(
                    self.axis[x], one, zero, zero, zero, zero, zero, zero, one, zero, zero, zero, zero)
                if err != 0:
                    return err
        return 0

    def getPosition(self, axis_num):
        """Get the position of the axis number `axis_num`.
        `self.pos`, `self.status`values would be updated,
        with the current position and the current status word.

        Params
        ------
        axis_num: int
            the number of the axis that would be measured. 
            Axis must have been previously initialized with `self.initAxis()`.

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.lib.EIB7GetPosition.argtypes = [ctypes.c_int, ctypes.POINTER(
            ctypes.c_ushort), ctypes.POINTER(ctypes.c_int64)]
        self.lib.EIB7GetPosition.restype = ctypes.c_uint
        self.lib.EIB7GetPosition(self.axis[axis_num], ctypes.byref(
            self.status), ctypes.byref(self.pos))

    def getPositions(self):
        """Get the position of each axis.

        Params
        ------

        Returns
        -------
        unsigned int
            position of axis: ax
        unsigned int
            position of axis: ay
        unsigned int
            position of axis: az
        unsigned int
            position of axis: aw
        """
        self.getPosition(0)
        ax = self.pos.value
        self.getPosition(1)
        ay = self.pos.value
        self.getPosition(2)
        az = self.pos.value
        self.getPosition(3)
        aw = self.pos.value
        return ax, ay, az, aw

    def getPositionDouble(self):
        """Converts the current value of `self.pos` into a double.
        Value is stored in `self.pos_double`- 

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.lib.EIB7IncrPosToDouble.argtypes = [
            ctypes.c_int64, ctypes.POINTER(ctypes.c_double)]
        self.lib.EIB7IncrPosToDouble.restype = ctypes.c_uint
        return self.lib.EIB7IncrPosToDouble(self.pos, ctypes.byref(self.pos_double))

    def openConnectInit(self, positions):
        """Shortcut to get the Host IP, open the connection, get the axis handle,
        and initialize the axis just with one function. This steps are used in almost
        every situation such as polling or streaming mode.

        Params
        ------
        positions: int list
            list conatining the positions of the axis to be initialized. 
            For example:
                init all of the axis -> positions = [0,1,2,3]
                init only axis 1-> positions = [1]

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        err = self.getHostIp()
        if err != 0:
            return err
        err = self.openConnection()
        if err != 0:
            return err
        err = self.getAxis()
        if err != 0:
            return err
        err = self.initAxis(positions)
        return err

######## END OF THE POLLING MODE METHODS. STARTING WITH STREAMING METHODS ########

    def getTimestampTicks(self):
        """Get the clock ticks per microsecond of the Timestamp timer. 
        Value is stored at `self.timestampTicks`. 

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.TIMESTAMP_PERIOD = 1000
        self.timestampTicks = ctypes.c_ulong()
        self.lib.EIB7GetTimestampTicks.argtypes = [
            ctypes.c_int, ctypes.POINTER(ctypes.c_ulong)]
        self.lib.EIB7GetTimestampTicks.restype = ctypes.c_uint
        return self.lib.EIB7GetTimestampTicks(self.eib, ctypes.byref(self.timestampTicks))

    def setTimestampPeriod(self):
        """Set the Timestamp period in clock ticks. 

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.timestampPeriod = ctypes.c_ulong(
            self.timestampTicks.value * self.TIMESTAMP_PERIOD)
        self.lib.EIB7SetTimestampPeriod.argtypes = [
            ctypes.c_int, ctypes.c_ulong]
        self.lib.EIB7SetTimestampPeriod.restype = ctypes.c_uint
        return self.lib.EIB7SetTimestampPeriod(self.eib, self.timestampPeriod)

    def setTimestamp(self, positions, enable):
        """Enable or disable timestamps for the position values.

        Params
        ------
        positions: int list
            list conatining the positions of the axis to enable timestamps. 
            Axis must have been initialized previously.
            For example:
                enable all of the axis -> positions = [0,1,2,3]
                enable only axis 1-> positions = [1]
        enable: int
            enables or disables timestamp.
                enable = 1 -> enables timestamps
                enable = 0 -> disables timestamps
        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.lib.EIB7SetTimestamp.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.EIB7SetTimestamp.restype = ctypes.c_uint
        if enable != 0 and enable != 1:
            print("Input error. Enable should be 1(enable) or 0(disable)")
            exit(1)
        for x in positions:
            if type(x) is not int or x > 3 or x < 0:
                print("Input error. Positions should be integers between 3 and 0")
                exit(1)
            err = self.lib.EIB7SetTimestamp(self.axis[x], ctypes.c_int(enable))
            if err != 0:
                return err
        return 0

    def addDataPacketSection(self, region, items):
        """Configures a section of the data packet configuration.

        Params
        ------
        region: int
            int conatining the region to be configured. 
                0 -> global data
                1,2,3 -> each axis region
        items: int
            items to be added into the packet's region

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        if type(region) is not int or region > 4 or region < 0:
            print(
                "Input error. Region is not correct. It must be an integer between 0 and four")
            exit(1)

        self.lib.EIB7AddDataPacketSection.argtypes = [
            (DataPacketSection*5), ctypes.c_int, ctypes.c_int, ctypes.c_int]
        self.lib.EIB7AddDataPacketSection.restype = ctypes.c_uint
        return self.lib.EIB7AddDataPacketSection(self.packet, region, region, items)

    def configDataPacket(self):
        """Configures the data packet for the operation modes 
        "Soft Realtime", "Recording", "Streaming".

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.lib.EIB7ConfigDataPacket.argtypes = [
            ctypes.c_int, (DataPacketSection*5), ctypes.c_int]
        self.lib.EIB7ConfigDataPacket.restype = ctypes.c_uint
        return self.lib.EIB7ConfigDataPacket(self.eib, self.packet, 5)

    def getTimerTriggerTicks(self):
        """Get the clock ticks per microsecond of the Timer Trigger timer.
        The value is stored at `self.timerTicks`.

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.lib.EIB7GetTimerTriggerTicks.argtypes = [
            ctypes.c_int, ctypes.POINTER(ctypes.c_ulong)]
        self.lib.EIB7GetTimerTriggerTicks.restype = ctypes.c_uint
        return self.lib.EIB7GetTimerTriggerTicks(self.eib, ctypes.byref(self.timerTicks))

    def setTimerTriggerPeriod(self):
        """Set the Timer Trigger period in clock ticks.

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.timerPeriod = ctypes.c_ulong(
            self.TRIGGER_PERIOD*self.timerTicks.value)
        self.lib.EIB7SetTimerTriggerPeriod.argtypes = [
            ctypes.c_int, ctypes.c_ulong]
        self.lib.EIB7SetTimerTriggerPeriod.restype = ctypes.c_uint
        return self.lib.EIB7SetTimerTriggerPeriod(self.eib, self.timerPeriod)

    def axisTriggerSource(self, positions):
        """Set trigger source for the axis.

        Params
        ------
        positions: int list
            list conatining the positions of the axis to set the triggerSource. 
            Axis must have been initialized previously.
            For example:
                trigger all of the axis -> positions = [0,1,2,3]
                trigger only axis 1-> positions = [1]

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.lib.EIB7AxisTriggerSource.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.EIB7AxisTriggerSource.restype = ctypes.c_uint
        for x in positions:
            if type(x) is not int or x > 3 or x < 0:
                print("Input error. Positions should be integers between 3 and 0")
                exit(1)
            err = self.lib.EIB7AxisTriggerSource(
                self.axis[x], ctypes.c_int(12))
            if err != 0:
                return err
        return 0

    def masterTriggerSource(self):
        """Set master trigger source.

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """

        self.lib.EIB7MasterTriggerSource.argtypes = [
            ctypes.c_int, ctypes.c_int]
        self.lib.EIB7MasterTriggerSource.restype = ctypes.c_uint
        return self.lib.EIB7MasterTriggerSource(self.eib, ctypes.c_int(12))

    def selectMode(self, mode):
        """Selects the operation mode of the EIB (Polling, Soft Realtime, Streaming, Recording). 
        The master connection is required to switch the mode.

        Params
        ------
        mode: int
            mode selected. Available options:
                0 -> polling
                1 -> soft real-time
                2 -> streaming
                3 -> recording single
                4 -> recording roll

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """

        self.lib.EIB7SelectMode.argtypes = [ctypes.c_int, ctypes.c_int]
        self.lib.EIB7SelectMode.restype = ctypes.c_uint
        return self.lib.EIB7SelectMode(self.eib, ctypes.c_int(mode))

    def globalTriggerEnable(self, enable, source):
        """Enables or disables the trigger sources

        Params
        ------
        enable: int
            Enables or disables the global trigger source. 
                0 -> disable
                1-> enable
        source: long
            trigger source

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """

        self.lib.EIB7GlobalTriggerEnable.argtypes = [
            ctypes.c_int, ctypes.c_int, ctypes.c_long]
        self.lib.EIB7GlobalTriggerEnable.restype = ctypes.c_uint
        return self.lib.EIB7GlobalTriggerEnable(self.eib, ctypes.c_int(enable), ctypes.c_long(source))

    def readFIFOData(self):
        """Copy data from the soft-realtime FIFO to destination memory. If the FIFO contains less
        than cnt entries only the available entries will be copied. The functions waits for at
        least one entry if none are available, but for max. timeout ms. This function converts the
        6-Byte raw encoder positions into 8-Byte ENCODER_POSITION values.

        Returns
        -------
        int
            Error code. If it is successful it would return NO_ERROR = 0.
        """

        self.lib.EIB7ReadFIFOData.argtypes = [
            ctypes.c_int,
            (ctypes.c_ubyte*200),
            ctypes.c_int,
            ctypes.POINTER(ctypes.c_ulong),
            ctypes.c_int
        ]
        self.lib.EIB7ReadFIFOData.restype = ctypes.c_int
        return self.lib.EIB7ReadFIFOData(self.eib, self.udpData, ctypes.c_int(1), ctypes.byref(self.entries), ctypes.c_int(200))

    def clearFIFO(self):
        """Clear all data currently in the soft-realtime FIFO.

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """

        self.lib.EIB7ClearFIFO.argtypes = [ctypes.c_int]
        self.lib.EIB7ClearFIFO.restype = ctypes.c_uint
        return self.lib.EIB7ClearFIFO(self.eib)

    def getDataFieldPtr(self, region, tipo):
        """This call delivers the size and the pointer of a data field from the position data.
        This call works for converted data only.

        Params
        ------
        region: int
            an integer indexing the data packet region.
        tipo: int
            the field to look up.

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.lib.EIB7GetDataFieldPtr.argtypes = [
            ctypes.c_int,
            (ctypes.c_ubyte*200),
            ctypes.c_int,
            ctypes.c_int,
            ctypes.c_void_p,
            ctypes.POINTER(ctypes.c_ulong)
        ]
        self.lib.EIB7GetDataFieldPtr.restype = ctypes.c_uint
        return self.lib.EIB7GetDataFieldPtr(self.eib, self.udpData, region, tipo, ctypes.byref(self.field), ctypes.byref(self.sz))

    def configStreaming(self):
        """Megawrapper to init the soft-realtime streaming mode. It configs the 
        eib741 to start streaming data of all the axis. 

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.checkError(self.getTimestampTicks())
        print("[SYSTEM]: Timestamps gotten")
        self.checkError(self.setTimestampPeriod())
        print("[SYSTEM]: Timestamp period set")
        self.checkError(self.setTimestamp([0, 1, 2, 3], 1))
        print("[SYSTEM]: Timestamp set")
        self.checkError(self.addDataPacketSection(0, 1))
        print("[SYSTEM]: Global data section added into the packet")
        items = ctypes.c_int(0x0002 | 0x0004 | 0x0008)
        for x in range(1, 5):
            self.checkError(self.addDataPacketSection(x, items))
            print(f"[SYSTEM]: Axis {x} data section added into the packet")
        self.checkError(self.configDataPacket())
        print("[SYSTEM]: Data packet configured.")
        self.checkError(self.getTimerTriggerTicks())
        print("[SYSTEM]: Timer trigger ticks gotten.")
        self.checkError(self.setTimerTriggerPeriod())
        print("[SYSTEM]: Timer trigger period set.")
        self.checkError(self.axisTriggerSource([0, 1, 2, 3]))
        print("[SYSTEM]: Axis trigger source configured.")
        self.checkError(self.masterTriggerSource())
        print("[SYSTEM]: Master trigger source cnfigured.")
        self.checkError(self.selectMode(2))
        print("[SYSTEM]: Streaming mode selected.")
        self.checkError(self.globalTriggerEnable(1, 2048))
        print("[SYSTEM]: Global trigger enabled")
        return 0

    def close(self):
        """Closes the connection to the EIB7 hardware. All former opened child handles (axis, I/O)
        are closed as well. 

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.lib.EIB7Close.argtypes = [ctypes.c_int]
        self.lib.EIB7Close.restype = ctypes.c_uint
        return self.lib.EIB7Close(self.eib)

    def safeExit(self):
        """This function finishes safely the streaming. Disables the global 
        trigger, sets the polling mode (default) and closes all connections. 

        Returns
        -------
        unsigned int
            Error code. If it is successful it would return NO_ERROR = 0.
        """
        self.globalTriggerEnable(0, -1)
        self.selectMode(0)
        self.close()

    def readData(self):
        """Reads the position of every axis and the status word. 

        Returns
        -------
        list: int
            status, posAx1, posAx2, posAx3, posAx4.
        """
        res = self.readFIFOData()
        if res == -1610612717:
            self.clearFIFO()
        res = self.getDataFieldPtr(0, 1)
        trigger = ctypes.cast(
            self.field, ctypes.POINTER(ctypes.c_ushort)).contents
        res = self.getDataFieldPtr(1, 8)
        timestamp = ctypes.cast(
            self.field, ctypes.POINTER(ctypes.c_ulong)).contents
        res = self.getDataFieldPtr(1, 4)
        posx = ctypes.cast(self.field, ctypes.POINTER(
            ctypes.c_longlong)).contents
        res = self.getDataFieldPtr(2, 4)
        posy = ctypes.cast(self.field, ctypes.POINTER(
            ctypes.c_longlong)).contents
        res = self.getDataFieldPtr(3, 4)
        posz = ctypes.cast(self.field, ctypes.POINTER(
            ctypes.c_longlong)).contents
        res = self.getDataFieldPtr(4, 4)
        posw = ctypes.cast(self.field, ctypes.POINTER(
            ctypes.c_longlong)).contents
        res = self.getDataFieldPtr(1, 2)
        status = ctypes.cast(
            self.field, ctypes.POINTER(ctypes.c_ushort)).contents
        return status.value, posx.value, posy.value, posz.value, posw.value



    def checkError(self, err):
        """Checks the error code returned by any function of this class.
        If it is not zero, a message with the error code is printed 
        and the execution finishes. 

        Params
        ------
        err: 
           The error code.
        """
        if err != 0:
            print(f"[ERROR]: The error code is -> {err}")
            self.globalTriggerEnable(0, -1)
            self.selectMode(0)
            self.close()
            exit(1)


    def tare(self):
        """Clears the trigger counter. Hopefuly it would tare the measures
        """
        self.lib.EIB7ResetTriggerCounter.argtypes = [ ctypes.c_int ]
        self.lib.EIB7ResetTriggerCounter.restype = [ ctypes.c_uint ]
        return self.lib.EIB7ResetTriggerCounter(self.eib)


if __name__ == '__main__':
    andromeda = PyEIBWrapper('./eib7_64.dll')
    res = andromeda.openConnectInit([0, 1, 2, 3])
    print("[SYSTEM]: AFTER CONNECTION")
    print(res)
    andromeda.configStreaming()
    count = 0
    while(True):
        status, px, py, pz, pw = andromeda.readData()
        print(f"Status: {status}. posx: {px} posy: {py} posz: {pz} posw: {pw}")
        count += 1
        if count == 100:
            print("[SYSTEM]: Trying to tare ... ")
            time.sleep(0.1)
            res1, res2 = andromeda.tare()
            print(f"[SYSTEM]: Tare result: {res1} {res2}")

        if count == 200: 
            break
    andromeda.safeExit()


"""res = andromeda.getTimestampTicks()
print("[SYSTEM]: GETTING TIMESTAMPS")
print(res)

res = andromeda.setTimestampPeriod()
print("[SYSTEM]: SETTING TIMESTAMP PERIOD")
print(res)

res = andromeda.setTimestamp([0, 1, 2, 3], 1)    
print("[SYSTEM]: SETTING TIMESTAMP")    
print(res)

res = andromeda.addDataPacketSection(0, 1)
print("[SYSTEM]: ADDING DATA TO THE PACKET - GLOBAL") 
print(res)

items = ctypes.c_int(0x0002 | 0x0004 | 0x0008)

for x in range (1, 5):
    res = andromeda.addDataPacketSection(x, items)
    if res != 0:
        print(res)
        andromeda.lib.EIB7Close(andromeda.eib)
        break
    print("[SYSTEM]: ADDING DATA TO THE PACKET - AXIS") 
    print(res)

res = andromeda.configDataPacket()
print("[SYSTEM]: CONFIG DATA PACKET. ")
print(res)

res = andromeda.getTimerTriggerTicks()
print("[SYSTEM]: GETTING TIMER TRIGGERS. ")
print(res)

res = andromeda.setTimerTriggerPeriod()
print("[SYSTEM]: SETTING TIMER TRIGGERS. ")
print(res)

res = andromeda.axisTriggerSource([0, 1, 2, 3])
print("[SYSTEM]: AXIS TRIGGER SOURCE. ")
print(res)

res = andromeda.masterTriggerSource()
print("[SYSTEM]: MASTER TRIGGER SOURCE. ")
print(res)

res = andromeda.selectMode(2)
print("[SYSTEM]: SELECTING STREAMING. ")
print(res)

res = andromeda.globalTriggerEnable(1, 2048)
print("[SYSTEM]: ENABLING GLOBAL TRIGGER")
print(res)



for x in range(10):
    res = andromeda.readFIFOData()
    print("[SYSTEM]: READING FIFO")
    print(res)

    if res == -1610612717:
        andromeda.clearFIFO()

    res = andromeda.getDataFieldPtr(0, 1)
    trigger = ctypes.cast(andromeda.field, ctypes.POINTER(ctypes.c_ushort)).contents

    res = andromeda.getDataFieldPtr(1, 8)
    timestamp = ctypes.cast(andromeda.field, ctypes.POINTER(ctypes.c_ulong)).contents


    res = andromeda.getDataFieldPtr(1, 4)
    posx = ctypes.cast(andromeda.field, ctypes.POINTER(ctypes.c_longlong)).contents
    res = andromeda.getDataFieldPtr(2, 4)
    posy = ctypes.cast(andromeda.field, ctypes.POINTER(ctypes.c_longlong)).contents
    res = andromeda.getDataFieldPtr(3, 4)
    posz = ctypes.cast(andromeda.field, ctypes.POINTER(ctypes.c_longlong)).contents
    res = andromeda.getDataFieldPtr(4, 4)
    posw = ctypes.cast(andromeda.field, ctypes.POINTER(ctypes.c_longlong)).contents


    res = andromeda.getDataFieldPtr(1, 2)
    status = ctypes.cast(andromeda.field, ctypes.POINTER(ctypes.c_ushort)).contents


    print(f"Status: {status}. posx: {posx.value} posy: {posy.value} posz: {posz.value} posw: {posw.value}")
    

    time.sleep(1)



### Esto es temporal
res = andromeda.globalTriggerEnable(0, -1)
print("[SYSTEM]: ENABLING GLOBAL TRIGGER")
print(res)

res = andromeda.selectMode(0)
print("[SYSTEM]: ENABLING GLOBAL TRIGGER")
print(res)

res = andromeda.close()
print("[SYSTEM]: ENABLING GLOBAL TRIGGER")
print(res)"""
