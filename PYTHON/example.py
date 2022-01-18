import M68HCXX as hc
import binView as bw
import S19 as s19

#device creation
device = hc.M68HC11E1('COM8')

print('    ********************************************')
print('    *         Modern 68HCXX programmer         *')
print('    *                  V1.0                    *')
print('    *             BY B.S 11/2021               *')
print('    *                 OXILEC                   *')
print('    ********************************************')

print('Enter a command, type help for more information')

while 1:
    command = input(">")

    if command == 'help':
        print('read - read memory (EPROM or EEPROM) from 68HCXX.')
        print('readS19 - Print content of S19 file in terminal.')
        print('write - write memory (EPROM or EEPROM) from 68HCXX.')

    elif command == 'readS19':#Print binary data from s19 file.
        fileName = input("Enter file name:  ")
        bw.printBinaryS19(fileName) #Print binary data on terminal.
        
    elif command == 'read':#Read data from device and print on terminal.
        #Get iformation from user.
        address = int(input("Enter start address in hexadecimal:  "),16)
        size = int(input("Enter lengt of read in decimal:  "))
        config = int(input("New config register in hexadecimal:  "),16)
        input("Make reset and press ENTER")
        
        devData = device.readMemory(address, size, config) #Read data from device.
        bw.printBinaryData(devData, address)#Print binary data on terminal.
        
    elif command == 'write':#Write data into device from S19 file.
        fileName = input("Enter file name:  ")
        config = int(input("New config register in hexadecimal:  "),16)
        if 'S19' in fileName:
            bw.printBinaryS19(fileName)#Print binary data on terminal.
            #Get iformation from S19 file.
            startAddress = s19.getStartAdress(s19.makeLineList(fileName))
            endAdress = s19.getDataSize(s19.makeLineList(fileName)) + startAddress
            print('{:04X}'.format(endAdress))
            if (startAddress >= device.epromStart) and (startAddress <= device.epromEnd) and (endAdress >= device.epromStart) and (endAdress <= device.epromEnd):
               input("Planc VPP(12V) ON and press ENTER") 
            input("Make reset and press ENTER")
            device.writeMemoryFromS19(fileName,config) #Write data into device.
