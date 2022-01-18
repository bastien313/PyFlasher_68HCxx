import S19 as s19

# Small module for visualise binary data formated for an human.

def printBinaryS19(s19File):
    """
    Print binary data on terminal from S19 file.
    Print 16 value by line + the start adresss.
    s19File: s19 file path
    """
    lineList = s19.makeLineList(s19File)
    binList = s19.makeBinaryList(lineList)
    startAdr = s19.getStartAdress(lineList)
    printBinaryData(binList, startAdr)

def printBinaryData(binaryData, startAdrress = 0):
    """
    Print binary data on terminal from list.
    Print 16 value by line + the start adresss.
    binaryData: data to be printed.
    startAdrress: first address of data.
    """
    print(binaryFormatText(binaryData, startAdrress))

def binaryFormatText(binaryData, startAdrress = 0):
    """
    Return a string for visualise binary data.
    Return 16 value by line + the start adresss.
    binaryData: data to be printed.
    startAdrress: first address of data.
    """
    binaryID = 0
    adress = startAdrress
    textOut = ''
    sizeData = len(binaryData)
    
    
    #Print top information
    textOut = '     ' 
    for lowerAdress in range(0,16):
        textOut += '{:02X} '.format(lowerAdress)
    textOut += '\n'
        
    while binaryID < sizeData:
        textOut += '{:04X} '.format(adress)
        for lowerAdress in range(0,16):
            if binaryID < sizeData:
                textOut += '{:02X} '.format(binaryData[binaryID])
            binaryID += 1
        textOut += '\n'
        adress += 16
    return textOut