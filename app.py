import csv, pathlib, os, datetime, time
from flask import Flask, jsonify, Response, request, session, render_template
from flask_cors import CORS, cross_origin
from netBoxConnection import create_udp_socket, send_request, read_data
from fakeheiden import FakeHeinden
from pyeibwrapper import PyEIBWrapper
from pyhbcwrapper import PyHBCWraperr



app = Flask(__name__, static_url_path='/static')
cors = CORS(app)
app.config['CORS_HEADERS'] = 'Content-Type'
app.secret_key = "kofoajgraijf#&%kdfj3321*"
#Init global objects
heiden = None
hbc = None
heidenCon = True


@app.route('/', methods=['GET'])
def root():
    session["tarex"] = 0
    session["tarey"] = 0
    session["tarez"] = 0

    return render_template('index.html')


@app.route('/api/tareloadcell', methods=['GET'])
def tareLoadCell():
    print("[SYSTEM]: REQUEST RECEIVED")
    global hbc
    result = hbc.sdoWrite(0x4410, 4, "")
    print(f"[SYSTEM]: results {result}")
    if result == -1:
        return jsonify({"message": "clipX tare unsuccessful"}), 200
    return jsonify({"message": "clipX tare successful"}), 200


@app.route('/api/tareheiden', methods=['GET'])
def tareHeiden():
    print("[SYSTEM]: REQUEST RECEIVED")
    global heiden
    status, ax, ay, az, aw = heiden.readData()
    session["tarex"] = ax/2000000
    session["tarey"] = ay/2000000
    session["tarez"] = az/2000000
    return jsonify({"message": "heidenhain tare successful"}), 200
    """res = heiden.tare()
    print(f"[SYSTEM]: results {res}")
    if res == 0:
        return jsonify({"message": "heidenhain tare successful"}), 200
    return jsonify({"message": "heidenhain tare unsuccessful"}), 200"""




@app.route('/api/test', methods=['GET'])
def test():
    if 'filename' in session: 
        print("I am in")
        print(session.get('filename'))
    print(session['filename'])
    return jsonify({"message": "Test sucessful"}), 200



#   Function: connect
#   Route: GET /api/connect/
#   Description: Closes all open conncections (NetBox and eib741)
@app.route('/api/connect', methods=['GET'])
def connect():
    try:
        """sk = create_udp_socket()
        send_request(('127.0.0.1', 49152), 0x0002, 1, sk)
        fx, fy, fz, tx, ty, tz = read_data(sk)
        sk.close()"""

        if heidenCon:
            global heiden
            heiden = PyEIBWrapper('./eib7_64.dll')
            heiden.openConnectInit([0, 1, 2 , 3])
            heiden.configStreaming()


        global hbc
        hbc = PyHBCWraperr()
        hbc.connect()
        hbc.sdoWrite(0x4428, 8, '10')
        hbc.startMeasurement()
        
        

        #   Use only when HeidenHain eib741 is connected
        

        fields = ["Date", "Heidenhain Ax", "Heidenhain Ay", "Heidenhain Az", "Load Cell Fx", "Load Cell Fy", "Load Cell Fz", "Load Cell Tx", "Load Cell Ty", "Load Cell Tz"]
        filename = "netbox-data-" + datetime.datetime.now().strftime("%d-%m-%Y-%H-%M") + ".csv"
        session['filename'] = filename
        if not os.path.exists(pathlib.Path().absolute().joinpath('data').joinpath(filename)):
            with open(f'./data/{filename}', 'w', newline='') as csv_file:
                csv_writer = csv.DictWriter(csv_file, fieldnames=fields)
                csv_writer.writeheader()
                csv_file.close()
        return jsonify({"message": "Connection sucessful", "filename": filename}), 200
    except Exception as e:
        print("[ SERVER ]: Error ocurred in route: '/api/connect'. Error message: ")
        print(e)
        return jsonify({"message": "Failed to connect"}), 500



#   Function: readSamples
#   Route: GET /api/readsamples/
#   Description: Reads Samples from both sensors and sends 
#   them to the client. It als writes samples if it is requested. 
@app.route('/api/readsamples', methods=['GET'])
def readSamples():
    try:
        
        """sk = create_udp_socket()
        send_request(('127.0.0.1', 49152), 0x0002, 1, sk)
        fx, fy, fz, tx, ty, tz = read_data(sk)
        sk.close()"""

        global hbc
        fx = 0
        fy = 0
        fz = 0
        tx = 0
        ty = 0
        tz = 0
        ax = 0
        ay = 0
        az = 0
        aw = 0
        while hbc.availableLines() > 0:
                fx, fy, fz, tx, ty, tz = hbc.readNextBlock()


        #   Use only when HeidenHain eib741 is connected
        if heidenCon:
            global heiden
            status, ax, ay, az, aw = heiden.readData()
            if request.args.get('write') == "true":
                filename = session['filename']
                fields =  ["Date", "Heidenhain Ax", "Heidenhain Ay", "Heidenhain Az", "Load Cell Fx", "Load Cell Fy", "Load Cell Fz", "Load Cell Tx", "Load Cell Ty", "Load Cell Tz"]
                with open(f'./data/{filename}', 'a', newline='') as csv_file:
                    dialect = csv.excel
                    dialect.delimiter = ";"
                    csv_writer = csv.DictWriter(csv_file, fieldnames=fields, dialect=dialect)
                    info = {
                        'Date': datetime.datetime.now().strftime("%d-%m-%Y-%H:%M:%S"),
                        'Heidenhain Ax': ax/2000000 - session["tarex"],
                        'Heidenhain Ay': ay/2000000 - session["tarey"],
                        'Heidenhain Az': az/2000000 - session["tarez"],
                        'Load Cell Fx': fz/1000,
                        'Load Cell Fy': fy/1000,
                        'Load Cell Fz': fz/1000,
                        'Load Cell Tx': tx/1000,
                        'Load Cell Ty': ty/1000,
                        'Load Cell Tz': tz/1000,
                    }
                    csv_writer.writerow(info)
                    csv_file.close()
        return jsonify({
            "fz": fy/1000, 
            "ax": ax/2000000 - session["tarex"],
            "ay": ay/2000000 - session["tarey"],
            "az": az/2000000 - session["tarez"]}), 200
    except Exception as e:
        print("[ SERVER ]: Error ocurred in route: /api/readSamples. Error message: ")
        print(e)
        return jsonify({"message": "Internal Server Error"}), 500

#   Function: disconnect
#   Route: GET /api/disconnect/
#   Description: Closes all open conncections (NetBox and eib741)
@app.route('/api/disconnect', methods=['GET'])
def disconnect():
    try:
        #   Use only when HeidenHain eib741 is connected
        global hbc
        hbc.stopMeasurements()
        global heiden
        heiden.safeExit()
        #fakeHeiden = FakeHeinden('path/to/dll')
        """sk = create_udp_socket()
        send_request(('127.0.0.1', 49152), 0x0000, 0, sk)
        sk.close()"""
        #fakeHeiden.fakeExit()
        return jsonify({"message": "Disconnected"}), 200
    except Exception as e:
        print("[ SERVER ]: Error ocurred in route: /api/disconnect. Error message: ")
        print(e)
        return jsonify({"message": "Internal server Error"}), 500



if __name__ == '__main__':
    app.run(debug=True, port=4000)
