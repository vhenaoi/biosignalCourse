import serial

def puertos_seriales():
    ports = ['COM%s' % (i + 1) for i in range(256)]
    encontrados = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            encontrados.append(port)
        except (OSError, serial.SerialException):
            pass
    return encontrados

if __name__ == '__main__':
    print(puertos_seriales())