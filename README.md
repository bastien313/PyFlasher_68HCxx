![Banner](view.png)
# What is PyFlasher_68HCxx?
PyFlasher_68HCxx is a python library to read and write eeprom of 68HCxx device.
The device must run in bootstrap mode.
This library does not deal with the hardware aspect necessary for programming.

## Features
- Upload bootloader on device.
- Read/write  eeprom.
- Read/write eprom (only for supporting device which include "EPROM Programming Utility").

## Dependency
- [pyserial] 
 ``pip install pyserial``

## How to use it?
```python
import M68HCXX as hc
import binView as bw

#At this point the device must be powered and connected to the serial port.

#Call class constructor of appropriate device and assign the good serial port.
device = hc.M68HC11E1('COM1')

#Read data from the device, do a hardware reset (put in bootstrap mode) before this opération.
#Read from 0xB600 to 0xB700 and put 0x0F on config register.
devData = device.readMemory(0xB600, 0x100, 0x0F)
#Print binary data on the terminal.
bw.printBinaryData(devData, 0xB600)

#Write data into the device, do a hardware reset (put in bootstrap mode) before this opération.
#Write data represented byfilepath.s19 file into the device and put 0x0F on config register.
#For eprom write a 12V must be present on correct pin(see device datasheet).
device.writeMemoryFromS19('filepath.s19',0x0F)


binData = [0xAB,0xFF,0x10,0x25]
#Write data into the device, do a hardware reset (put in bootstrap mode) before this opération.
#Write data [0xAB,0xFF,0x10,0x25] at 0xB600 and put 0x0F on config register.
device.writeMemory(binData, 0xB600, len(binData), 0x0F):
```

## How it works?
The device must be in bootstrap mode before each request.
When writeMemory() or readMemory() are called the library load the correct bootloader into the device with uploadBootloader().
When the device executes the selected bootloader the library talk to the bootloader for performs an operation.

## Bootloader.
The M68HC11 Family of MCUs (microcontroller units) has a bootstrap mode that allows a user-defined
program to be loaded into the internal random-access memory (RAM) by way of the serial
communications interface (SCI); the M68HCXX then executes this loaded program.

Three bootloader is available:
- A8NS3E.TSK for read/write eeprom.
- A8NS3P.TSK for reading eprom when the device has some eprom (write seem to not work).
- BTROM.S19 for writing eprom when the device has some eprom and "EPROM Programming Utility".

BTROM.S19 simply jump to "EPROM Programming Utility"
A8NS3E.TSK / A8NS3P.TSK are more complicated the assembly file and help can be found on \RESSOURCES.

## Utility
- binView.py Provide some function to display binary data on the terminal.
- S19.py Provide some function to process S19 file, thanks to [marwinq/S19]
- DOS_UTILITY\LINK11.EXE Is a linker for 68hc11, work only on DOS (DOSBOX can be used)
- DOS_UTILITY\X68C11.EXE Is an assembler for 68hc11, work only on DOS (DOSBOX can be used)


[pyserial]: <pyserial>
[marwinq/S19]: <https://github.com/marwinq/S19>
