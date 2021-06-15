import ctypes


class DataPacketSection(ctypes.Structure):
    
    _fields_ = [
        ("dataRegion", ctypes.c_int),
        ("items", ctypes.c_ulong)
    ]