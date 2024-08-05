from flask import Flask
from modbus import ModBus
import os

app = Flask(__name__)
port_name='/dev/ttyUSB0'
TOTAL_PORTAS = 16
modbus = ModBus(usb_port=port_name,total_portas=TOTAL_PORTAS)

def modbus_init():
    global modbus
    # ja inicializado?
    if modbus.init == 1:        
        modbus.port_status(1) # tenta ler um status...        
   
    # linux... 
    if modbus.init == 0:               
        try:
            port_number = 0
            while port_number < 5 and modbus.init == 0:
                usb_port_name=f'/dev/ttyUSB{port_number}'
                modbus = ModBus(usb_port=usb_port_name,total_portas=TOTAL_PORTAS)
                port_number += 1
        except:
            ...
    # windows...
    if modbus.init == 0:        
        try:
            port_number = 0
            while port_number < 10 and modbus.init == 0:
                usb_port_name=f'COM{port_number}'
                modbus = ModBus(usb_port=usb_port_name,total_portas=TOTAL_PORTAS)
                port_number += 1
        except:
            ...
  
    
@app.route("/")
def init():
    modbus_init()
    return {
        "init": modbus.init,
        "usbport":modbus.usb_port,
        "error":modbus.error,
        "status":modbus.init,
    }  
    

@app.route("/modbus/status")
def modbus_status():
    '''Retorna json com status'''
    modbus_init()
    return {
        "init": modbus.init,
        "usbport":modbus.usb_port,
        "error":modbus.error,
        "status":modbus.init,
    }  

@app.route("/port/<int:port_id>/status")
def port_status(port_id):
    if modbus.init == 0:
        modbus_init()   
    port_status = modbus.port_status(port_id)
    return {
        "init": modbus.init,
        "usbport":modbus.usb_port,
        "error":modbus.error,
        "status":port_status,
    }

@app.route("/port/<int:port_id>/open")
def port_open(port_id):
    if modbus.init == 0:
        modbus_init()   
    port_status = modbus.port_open(port_id)
    return {
        "init": modbus.init,
        "usbport":modbus.usb_port,
        "error":modbus.error,
        "status":port_status,
    }
    
# rodar sem precisar usar "flask run" no terminal
if __name__ == '__main__':
    app.run(debug=True)