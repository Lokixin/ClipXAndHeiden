import socket
import struct
import os
import pathlib


#   The address should be a tuple ('IP', PORT)

ADDRESS = ('localhost', 8080)
# RECV_ADDRESS = ('192.168.1.1', 49152) Net F/T address, used for production, not tests.
RECV_ADDRESS = ('localhost', 49152)
cmd = 0x0002
numOfSamples = 10


def create_udp_socket():
    udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #print("[PROGRAM]: CLIENT SOCKET CREATED")
    return udp_socket


def send_request(RECV_ADDRESS, cmd, numOfSamples, sender_socket):
    encoded_message = struct.pack("!HHI", 0x1234, cmd, numOfSamples)
    numOfBytes = sender_socket.sendto(encoded_message, RECV_ADDRESS)
    #print(f"[PROGRAM]: REQUEST SEND WITH {numOfBytes}")


def read_data(socket):
    #print("[PROGRAM]: WAITING FOR DATA")
    data, address = socket.recvfrom(1024)
    data = struct.unpack('!3I6i', data)
    ip, port = address
    rdt_seq, ft_seq, status, fx, fy, fz, tx, ty, tz = data
    #print(f"[CLIENTE]: Datos redibidos desde: {ip}:{port}\nFt_seq: {ft_seq}\nrdt_seq: {rdt_seq}. The status code is: {status}")
    #print(f"Valores recibidos:\nFx: {fx}\nFy: {fy}\nFz: {fz}")
    return fx, fy, fz, tx, ty, tz
