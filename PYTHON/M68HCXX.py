import serial
import time
import serial.tools.list_ports
import sys
import S19 as s19
import binView as bw

import sys
import time


def loadingBar(count,total,size):
    percent = float(count)/float(total)*100
    sys.stdout.write("\r" + str(int(count)).rjust(3,'0')+"/"+str(int(total)).rjust(3,'0') + ' [' + '='*int(percent/10)*size + ' '*(10-int(percent/10))*size + ']')

class TimeOutError(Exception):
    pass
class SerialException(Exception):
    pass
    
class MC68HCXX:
    """
    Base class for 68HC11 Device.
    The base class (MC68HCXX) can read eeprom,eprom and write eeprom only.

    For use this class directly, user must edit the apropriate device address.
        self.epromStart
        self.epromEnd
        self.eepromStart
        self.eepromEnd
    And set self.p_prom to 3 if eprom is present on device.

    Another war is to create a specific device class which inherit from this one.
    See example with M68HC711E9 class defined below.
    If eprom write is needed the method writeEProm() must be overwriten.
    Set self.p_prom to 3 if eprom is present on device.
    """
    def __init__(self,comPort):
        self.binDataFile = 0
        self.serialPort = 0
        self.comPortStr = comPort
        
        #device definition
        self.epromStart = 0  #eprom address start
        self.epromEnd = 0    #eprom address end
        self.eepromStart = 0 #eeprom address start
        self.eepromEnd = 0   #eeprom address end
        self.readEPromBootloader = 'bootLoader\A8NS3P.TSK'  #Bootloader for read eprom
        self.writeEPromBootloader = 'bootLoader\BTROM.S19'  #Bootloader for write eprom when device have "EPROM Programming Utility" preprogrammed by NXP 
        self.readEEPromBootloader = 'bootLoader\A8NS3E.TSK' #Bootloader for read/write eeprom
        self.writeEEPromBootloader = 'bootLoader\A8NS3E.TSK'#Bootloader for read/write eeprom
        self.p_prom = 3
       
    def _serialOpen(self, speed, timeOut = None):
        """
        Open serial port.
        Raise SerialException if an error occur.
        """
        try:
            self.serialPort = serial.Serial(self.comPortStr, speed, timeout=timeOut)
        except:
            self.serialPort = 0
            raise SerialException

    def _serialClose(self):
        """
        Close serial port.
        """
        if self.serialPort != 0:
            self.serialPort.close()
            self.serialPort = 0
        
    def uploadBootloaderFromS19(self, bootLoaderS19):  
        """ Send bootloader to the device with S19 file.
            An hardware device reset must be done before calling this function.
            bootLoaderS19: file path of s19 file.
        """
        lineList = s19.makeLineList(bootLoaderS19)
        binaryDat = s19.makeBinaryList(lineList)
        self.uploadBootloader(binaryDat)
        
    def uploadBootloader(self, binaryData):
        """ Send bootloader to the device with binary data.
            An hardware device reset must be done before calling this function.
            binaryData: 
        """
        binaryData = list(binaryData)
        self._serialClose()
        try:
            self._serialOpen(1200, 10)
        except:
            print('Unable to open {}'.format(self.comPortStr))
            self._serialClose()
     
        else:
            print('Open OK')
            self.serialPort.write(0xFF.to_bytes(1, 'big'))
            #self.serialPort.write(binaryData)
            for data in binaryData:
                self.serialPort.write(data.to_bytes(1, 'big'))
            print('Bootloader send')
            bw.printBinaryData(binaryData)
            echo = list(self.serialPort.read(len(binaryData)))
            print('Bootloader echo')
            bw.printBinaryData(echo)
            
            if echo == binaryData:
                print('Bootloader OK')
            else:
                print('Error bootloader')
                self._serialClose()
        
    def writeEProm(self, data, startAddress, size):
        """
        Abstract method for write eprom.
        An hardware device reset must be done before calling this function.
        data: list of byte to write into the device.
        startAddress: Start adresse where to write data.
        size: size of data.
        """
        print("This device doesn't have an EPROM")
        
    def writeEPromFromS19(self, s19FileName):
        """
        Write eprom from s19 file.
        An hardware device reset must be done before calling this function.
        s19FileName: file path of s19 file.
        """
        lineList = s19.makeLineList(s19FileName)
        self.writeEProm(s19.makeBinaryList(lineList), s19.getStartAdress(lineList), s19.getDataSize(lineList)) 
        
    def writeEEProm(self, data, startAddress, size, configRegister = 0x0F):
        """
        Write eeprom method.
        An hardware device reset must be done before calling this function.
        The eeprom will be completely erased before writing the desired data.
        By default this method will write 0x0F to the device config register, overide this if needed. 
        data: list of byte to write into the device.
        startAddress: Start adresse where to write data.
        size: size of data.
        configRegister: New value of device config register.
        """
        
        #Check if the requested write is in the device adress.
        if (startAddress >= self.eepromStart) and (startAddress <= self.eepromEnd) and (startAddress + (size-1) >= self.eepromStart) and (startAddress + (size-1) <= self.eepromEnd):
            bootloaderData = open(self.writeEEPromBootloader,'rb').read()
        else:
            print('Address {:04X}-{:04X} out of range'.format(startAddress,startAddress + (size-1)))
            return 0
            
        #Inject specific data in the bootloader.
        bootloaderData = list(bootloaderData)
        endAddress = (startAddress + size) -1
        bootloaderData[2] = self.p_prom 
        bootloaderData[3] = configRegister#CONFIG register
        bootloaderData[4] = (startAddress & 0xFF00) >> 8
        bootloaderData[5] =  startAddress & 0x00FF
        bootloaderData[6] = (endAddress & 0xFF00) >> 8
        bootloaderData[7] =  endAddress & 0x00FF
        
        
        #Write bootLoader
        self.uploadBootloader(bootloaderData)
        self._serialClose()
        try:
            self._serialOpen(9600)
        except:
            print('Unable to open {}'.format(self.comPortStr))
            self._serialClose()
            return 0
     
        else:
            print('Open OK')
            
            #Erasing eeprom.
            self.serialPort.write('P'.encode('utf-8'))
            print('EEprom erasing')
            self.serialPort.read(1)
            
            #Read config resigter.
            config = self.serialPort.read(1)[0]
            print('CONFIG = {:02X}'.format(config))
            
            actualAddress = startAddress
            
            #Write data.
            idData = 0
            for intVal in data:
                loadingBar(idData+1, len(data), 5)
                idData +=1
                self.serialPort.write(intVal.to_bytes(1, 'big')) #Write byte
                resp = self.serialPort.read(1)[0] #Read response from device.
                if intVal != resp: #Check validity of byte.
                    print('Error on {:04X}, write {:02X} != read {:02X}'.format(actualAddress ,intVal , resp))
                    self._serialClose()
                    return 0
                actualAddress +=1
            print('')
            print('Write succes :)')
            self._serialClose()
            return 1
            
    def writeEEPromFromS19(self, s19FileName, configRegister = 0x0F):
        """
        Write eeprom method from s19 file.
        An hardware device reset must be done before calling this function.
        The eeprom will be completely erased before writing the desired data.
        By default this method will write 0x0F to the device config register, overide this if needed. 
        s19FileName: file path of s19 file.
        configRegister: New value of device config register.
        """
        lineList = s19.makeLineList(s19FileName)
        writeEEProm(s19.makeBinaryList(lineList), s19.getStartAdress(lineList), s19.getDataSize(lineList))    
        
        
    def writeMemoryFromS19(self, s19FileName, configRegister = 0x0F):
        """
        Write memory method from s19 file.
        Equivalent to writeEEPromFromS19() or writeEPromFromS19().
        This function call the correct method depending of the addess where we write.
        """
        lineList = s19.makeLineList(s19FileName)
        self.writeMemory(s19.makeBinaryList(lineList), s19.getStartAdress(lineList), s19.getDataSize(lineList), configRegister)  
    
    def writeMemory(self, data, startAddress, size, configRegister = 0x0F):
        """
        Write memory method.
        Equivalent to writeEEProm() or writeEProm().
        This function call the correct method depending of the addess where we write.
        """
        if (startAddress >= self.epromStart) and (startAddress <= self.epromEnd) and (startAddress + (size-1) >= self.epromStart) and (startAddress + (size-1) <= self.epromEnd):
            self.writeEProm(data, startAddress, size)
        elif (startAddress >= self.eepromStart) and (startAddress <= self.eepromEnd) and (startAddress + (size-1) >= self.eepromStart) and (startAddress + (size-1) <= self.eepromEnd):
            self.writeEEProm(data, startAddress, size, configRegister)
        else:
            print('Address {:04X}-{:04X} out of range'.format(startAddress,startAddress + (size-1) ))
            return 0
        
    def readMemory(self, startAddress, size, configRegister = 0x0F):
        """
        Read slected memory and return a list of bytes read.
        An hardware device reset must be done before calling this function.
        By default this method will write 0x0F to the device config register, overide this if needed. 
        startAddress: Start adresse where to read data.
        size: size of data.
        configRegister: New value of device config register.
        """
        
        #Check if the requested read is in the device adress and select the correct bootloader(eprom or eeprom).
        if (startAddress >= self.epromStart) and (startAddress <= self.epromEnd) and (startAddress + (size-1) >= self.epromStart) and (startAddress + (size-1) <= self.epromEnd):
            bootloaderData = open(self.readEPromBootloader,'rb').read()
        elif (startAddress >= self.eepromStart) and (startAddress <= self.eepromEnd) and (startAddress + (size-1) >= self.eepromStart) and (startAddress + (size-1) <= self.eepromEnd):
            bootloaderData = open(self.readEEPromBootloader,'rb').read()
        else:
            print('Address {:04X}-{:04X} out of range'.format(startAddress,startAddress + (size-1) ))
            return 0
        
        #Inject specific data in the bootloader.
        bootloaderData = list(bootloaderData)
        endAddress = (startAddress + size) -1
        bootloaderData[2] = self.p_prom 
        bootloaderData[3] = configRegister#CONFIG register
        bootloaderData[4] = (startAddress & 0xFF00) >> 8
        bootloaderData[5] =  startAddress & 0x00FF
        bootloaderData[6] = (endAddress & 0xFF00) >> 8
        bootloaderData[7] =  endAddress & 0x00FF
        
        #Write bootLoader
        self.uploadBootloader(bootloaderData)
        self._serialClose()
        try:
            self._serialOpen(9600,(((endAddress-startAddress)/9600) * 10)+3)
        except:
            print('Unable to open {}'.format(self.comPortStr))
            return 0
     
        else:
            print('Serial port open at 9600 OK')
            self.serialPort.write('L'.encode('utf-8'))
            return self.serialPort.read((endAddress-startAddress) + 2)[1:]
        
       
class M68HC711E9(MC68HCXX):
    """
    Specific device class inherited from MC68HCXX(base class).
    A specific device class can be created for each device.
    Device address must be redefined.
        self.epromStart
        self.epromEnd
        self.eepromStart
        self.eepromEnd
    And set self.p_prom to 3 if eprom is present on device.
    Specific bootloader can be redefined if needed

    This device include eprom and "EPROM Programming Utility" preprogrammed by NXP.
    The method for write eprom is overwriten for use NXP routine.

    """
    def __init__(self,comPort):
        MC68HCXX.__init__(self, comPort)
        #device definition
        self.epromStart = 0xD000
        self.epromEnd = 0xFFFF
        self.eepromStart = 0xB600
        self.eepromEnd = 0xB7FF
        self.p_prom = 3
        self.readEPromBootloader = 'bootLoader\A8NS3P.TSK'  #Bootloader for read eprom
        self.writeEPromBootloader = 'bootLoader\BTROM.S19'  #Bootloader for write eprom when device have "EPROM Programming Utility" preprogrammed by NXP 
        self.readEEPromBootloader = 'bootLoader\A8NS3E.TSK' #Bootloader for read/write eeprom
        self.writeEEPromBootloader = 'bootLoader\A8NS3E.TSK'#Bootloader for read/write eeprom
    
    def writeEProm(self, data, startAddress, size):
        """
        Method for write eprom.
        An hardware device reset must be done before calling this function.
        data: list of byte to write into the device.
        startAddress: Start adresse where to write data.
        size: size of data.
        """
        lineList = s19.makeLineList(self.writeEPromBootloader)
        bootloaderData = s19.makeBinaryList(lineList)
        
        #Inject specific data in the bootloader.
        bootloaderData[2] = (startAddress & 0xFF00) >> 8 
        bootloaderData[3] = startAddress & 0x00FF
        
        #Write bootLoader
        self.uploadBootloader(bootloaderData)
        
        rdyFlag = self.serialPort.read(1)
        if rdyFlag[0] == 0xFF:
            idData = 0
            print('Device ready')
            
            while idData < size:
                #Write and verify twice data
                loadingBar(idData+1, size, 5)
                nbDataToSend = 2 if ((size - idData) != 1) else 1
                dataVerify = []
                for nb in range(0,nbDataToSend):
                    dataVerify.append(data[idData])
                    self.serialPort.write(data[idData].to_bytes(1, 'big')) #Write data.
                    idData +=1
                
                echo = list(self.serialPort.read(nbDataToSend))
                if echo != dataVerify:
                    for nb in range(0,nbDataToSend):
                        print('Error on {:04X}, write {:02X} != read {:02X}'.format(startAddress + (idData - ( 1-nb)) - 1 ,dataVerify[1-nb] , echo[1-nb]))
                    self._serialClose()
                    print('Write abort')
                    return 0
        else:
            self._serialClose()
            print('Device busy?')
            return 0
        self._serialClose()
        print('')
        print('Write succes :)')
                
                
                
class M68HC11A1(MC68HCXX):
    def __init__(self,comPort):
        MC68HCXX.__init__(self, comPort)
        self.eepromStart = 0xB600
        self.eepromEnd = 0xB7FF
        
class M68HC11E1(MC68HCXX):
    def __init__(self,comPort):
        MC68HCXX.__init__(self, comPort)
        self.eepromStart = 0xB600
        self.eepromEnd = 0xB7FF
        
class M68HC11F1(MC68HCXX):
    def __init__(self,comPort):
        MC68HCXX.__init__(self, comPort)
        self.eepromStart = 0xFE00
        self.eepromEnd = 0xFFFF
        
class M68HC811E2(MC68HCXX):
    def __init__(self,comPort):
        MC68HCXX.__init__(self, comPort)
        self.eepromStart = 0xF800
        self.eepromEnd = 0xFFFF
        
    def uploadBootloader(self, binaryData):
        """ Send bootloader to the device with binary data.
            An hardware device reset must be done before calling this function.
            binaryData: 
        """
        binaryData = list(binaryData)
        while(len(binaryData) < 256):
        # Fill bootloader data with 0xFF to reach a bootloader size of 256.
        # Fix for microcontroller have 256 byte in ram, they wait exactly 256 byte for bootlader.
            binaryData.append(0xFF) 
        self._serialClose()
        try:
            self._serialOpen(1200, 10)
        except:
            print('Unable to open {}'.format(self.comPortStr))
            self._serialClose()
     
        else:
            print('Open OK')
            self.serialPort.write(0xFF.to_bytes(1, 'big'))
            #self.serialPort.write(binaryData)
            for data in binaryData:
                self.serialPort.write(data.to_bytes(1, 'big'))
            print('Bootloader send')
            bw.printBinaryData(binaryData)
            echo = list(self.serialPort.read(len(binaryData)-1))
            print('Bootloader echo')
            bw.printBinaryData(echo)
            
            if echo == binaryData[:-1] :
                print('Bootloader OK')
            else:
                print('Error bootloader')
                self._serialClose()
       
class M68HC711L6(MC68HCXX):
    def __init__(self,comPort):
        MC68HCXX.__init__(self, comPort)
        self.eepromStart = 0xB600
        self.eepromEnd = 0xB7FF
        
class M68HC11A1(MC68HCXX):
    def __init__(self,comPort):
        MC68HCXX.__init__(self, comPort)
        self.eepromStart = 0xB600
        self.eepromEnd = 0xB7FF