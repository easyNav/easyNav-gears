import serial

# Serial class
class SerialClass:

    # constr
    def __init__(self, strPort):
        # open serial port
        self.ser = serial.Serial(strPort, 57600)
        self.arr = []
        self.yaw = 0
        self.pitch = 0
        self.roll = 0
        self.mag = 0
        self.gx = 0
        self.gy = 0
        self.gz = 0
        self.ms = 0

    def read(self, bit):
        # read line
        # #YPRMfssT=,-1.24,-2.04,-179.52,1.08,0.04,-0.01,-1.00,10.00,
        bit = bit + "\r"
        self.ser.write(bit.encode())
        line = self.ser.readline()
        print line
        # self.arr = line.split(",")
        # ctrl = self.arr[0]
        # if ctrl != "#YPRMfssT=":
        #     return

        # self.yaw = float(self.arr[1])
        # self.pitch = float(self.arr[2])
        # self.roll = float(self.arr[3])
        # self.mag = float(self.arr[4])
        # self.gx = float(self.arr[5])
        # self.gy = float(self.arr[6])
        # self.gz = float(self.arr[7])
        # self.ms = float(self.arr[8])

    def close(self):
        # close serial
        self.ser.flush()
        self.ser.close()

if __name__ == '__main__':
    serial = SerialClass("/dev/tty.usbserial-A600dRYL")

    # Serial Loop
    while(1):
        serial.read("$")
        #serial.read("#")

    serial.close()








