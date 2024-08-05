import minimalmodbus
from time import sleep
# IMPORTANTE: windows: CH340 so funciona versao 3.3.2011.11 de 04/11/2011. 
class ModBus():
    '''Fornece comunicação MODBUS pela USB para leitura e acionamentos'''
    def __init__(self, usb_port, total_portas: int) -> bool:
        self.usb_port = usb_port    # porta iniciada nesta instancia
        self.init = None            # status da inicializacao
        self.error = ''             # texto erro             
        try:
            print(f'[MODBUS] INIT: porta: {self.usb_port}, baud: 9600, portas: {total_portas}')          
            # inicia em "RTU mode" o ModBus
            #baud: 9600, Data bits: 8, Parity: None, Stop Bit: 1
            self.modbus1 = minimalmodbus.Instrument(self.usb_port, 1) # port name, slave address 1 (em decimal 1 ate 247)
            self.modbus1.serial.baudrate = 9600                         # Corrige o Baud rate (padrao da biblioteca é 19200)
            self.modbus1.serial.timeout  = 0.5                          # seconds comunicação lenta. dá mais tempo...)(padrao de 0.05s)            
            
            #precisa de segundo modulo de 16 (portas 17 a 32)?
            if total_portas > 16: 
                self.modbus2 = minimalmodbus.Instrument(self.usb_port, slaveaddress=2)    # port name, slave address 2
            #precisa de terceiro modulo de 16 (portas 33 a 48)?
            if total_portas > 32: 
                self.modbus3 = minimalmodbus.Instrument(self.usb_port, slaveaddress=3)    # port name, slave address 3
            self.init = 1
            print(f'[MODBUS] {self.usb_port} Iniciada...')
            # testar comunicacao lendo status da porta 1
            result = self.port_status(num_porta=1)
            if result == -1:
                self.init = 0
            else:
                self.init = 1
        except Exception as ex:
            self.error = f'[MODBUS] INIT ERROR: {ex}'
            self.init = 0 
            print(self.error)
            
    
    def port_open(self, num_porta: int) -> int:
        # tentar enviar comnando de abrir
        try:
            if num_porta < 1 or num_porta > 48:
                self.error = f'[MODBUS] Port {num_porta} Open: Error! Porta deve ser entre 1 e 48!'
                print(self.error)                
                return -1   #error
            #preciso converter numero de porta(1 a 16) em binario de 16 bits (32.768)           
            if num_porta <= 16:
                decimal = 2**(num_porta - 1)  #2 elevado a i entao porta 3 vai ser 2^2 = 4 decimal(0x8 ou 0100)
                self.modbus1.write_register(functioncode=6, registeraddress=112, value = decimal)
                self.modbus1.write_register(functioncode=6, registeraddress=112, value = 0)         #desliga todas as bobinas
            elif num_porta <= 32:
                decimal = 2**(num_porta - 17)  #2 elevado a i entao porta 3 vai ser 2^2 = 4 decimal(0x8 ou 0100)
                self.modbus2.write_register(functioncode=6, registeraddress=112, value = decimal)
                self.modbus2.write_register(functioncode=6, registeraddress=112, value = 0)
            elif num_porta <= 48:
                decimal = 2**(num_porta - 33)  #2 elevado a i entao porta 3 vai ser 2^2 = 4 decimal(0x8 ou 0100)
                self.modbus3.write_register(functioncode=6, registeraddress=112, value = decimal)
                self.modbus3.write_register(functioncode=6, registeraddress=112, value = 0)
            # comando enviado...
            print(f'[MODBUS] Port {num_porta} Open: executed')
        except Exception as ex:
            print(f'[MODBUS] Erro de acionamento porta {num_porta}. {ex}')
            return -1
        
        # checar sensor da porta e enviar resultado
        sleep(1)    # aguarda 1 segundo para depois ler sensor da porta
        sensor_porta = self.port_status(num_porta)
        if sensor_porta == -1:
            return -1
        # retorna leitura do sensor da porta
        self.error = ''            
        return sensor_porta     # retorna sensor da porta!
    
    def port_status(self, num_porta: int):
        #ler entradas individuais address: 129(0x81) ate 144(0x90) (16 entradas)
        #ler as 16 entradas de uma vez address: 192(0xC0) le todas de uma vez em binario
        #rs485: 1, function: 3, length 2bytes 
        try:
            if num_porta < 1 or num_porta > 48:
                self.error = f'[MODBUS] Port {num_porta} Status: Error! Porta deve ser entre 1 e 48!'
                print(self.error)                
                return -1   #error
            if num_porta <= 16 :            
                address = 129 + (num_porta - 1) # varia de porta 1 (address 129) a 16(address 144) 
                status_porta = self.modbus1.read_register(registeraddress=address, functioncode=3) # endereço e numero de decimais retornados
            elif num_porta <= 32:
                address = 129 + (num_porta - 17) # varia de porta 17 (address 129) a 32(address 144) 
                status_porta = self.modbus2.read_register(registeraddress=address, functioncode=3) # endereço e numero de decimais retornados
            elif num_porta <= 48:
                address = 129 + (num_porta - 33) # varia de porta 33 (address 129) a 48(address 144) 
                status_porta = self.modbus3.read_register(registeraddress=address, functioncode=3) # endereço e numero de decimais retornados
           
            # tudo ok...
            self.error = ''
            print(f'[MODBUS] Port {num_porta} Status: {status_porta}')           
            return status_porta 
        except:
            self.error = f'[MODBUS] Port {num_porta} Status: nao responde!'
            self.init = 0
            print(self.error)
            return -1       #error
            