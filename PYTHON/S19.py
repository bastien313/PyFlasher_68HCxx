#S19 File Analysis
#anovus
#This is a small module which can be used to analyze the structure of
#an S19 file for personal study and reference.

###############
#	Functions
###############

#Returns a count for records of the S[N] type, where N is any number from 0 through 9.

def s_count(record_list, N):
    c=0				#count var initalized at 0
    r=record_list 	#local var for the list of records
    l=len(r) 		#length of the record list (the S19 file)
    s= "S"+str(N)		#Depending on value of N, a string equal to S0, S1, .., S8, or S9
    for i in range(0, l):	#iterates for each member of the list
        t= s in r[i]		#Is S[N] found in the current row? True if yes, False if no.
        if t==True:			
            c+=1 			#increment by 1 for each record of S[N] found
    return c

#Returns a list of 10 elements, where the first element is equal to the number of S0
#records in the S19 file, the 2nd element equal to the number of S1 records, and so on
#until S9.

def s_totals(record_list):
    r=record_list	#local var for the list of records
    S=zerolist(10)	#initialize empty list.
    for i in range(0,10):
        S[i]=s_count(r,i)		#count how many of S[N] type records in the S19 file.
    return S

#A printed breakdown of the type of S records found in the S19 file. Omits S type records
#that are not found in the file.

def print_totals(S):
    for i in range(0,10):
        if S[i]!=0:
            print(str(S[i])+'\tS'+str(i)+' records.')
    return

#Initialize a list of zeroes of length N.

def zerolist(N):
    l=[0]*N
    return l

#Extracts the bytecount byte from the selected record R. See S19_Chart for illustration of
#different byte fields for each record.

def bytecount_byte(R):
    r=R[2:4]
    return r

#Converts the bytecount byte from hex to decimal value.

def bytecount(s):
    b=bytecount_byte(s)
    r=int(b,16)
    return r

#Extracts the checksum byte from the selected record R.

def checksum(R):
    r=R[-2:]
    return r

#Extracts the data fields from the selected record R

def data_extract(R):
    adc=R[4:] 			#address, data, checksum
    s = 0
    if 'S0' in R or 'S1' in R:
        s=R[8:-2]
    if 'S2' in R:
        s=R[10:-2]
    if 'S3' in R or 'S7' in R:
        s=R[12:-2]
    return s

#Extracts the address fields from the selecter record R.

def addr_extract(R):
    adc=R[4:] #address, data, checksum
    s = 0
    if 'S0' in R or 'S1' in R:
        s=R[4:8]
    if 'S2' in R:
        s=R[4:10]
    if 'S3' in R or 'S7' in R:
        s=R[4:12]
    return s

#Extracts the address fields for all records in the records list.
#Returns a list of the address fields.

def addr_extract_whole(record_list):
    r=record_list
    l=len(record_list)
    S=zerolist(l)
    for i in range(0,l-1):
        S[i]=addr_extract(r[i])
    return S

#Extracts the data fields for all records in the records list.
#Returns a list of the data fields.

def data_extract_whole(record_list):
    r=record_list
    l=len(record_list)
    S=zerolist(l)
    for i in range(0,l-1):
        S[i]=data_extract(r[i])
    return S

#Saves the extracted data fields list to file.

def dump_data(g):
    q=data_extract_whole(g)
    data=open('_data.txt','w')
    for x in q:
        data.write("%s\n" % x)
    return

#Saves the extracted address fields list to file.

def dump_addresses(g):
    q=addr_extract_whole(g)
    data=open(file_name+'_addresses.txt','w')
    for x in q:
        data.write("%s\n" % x)
    return
    
    

def getAdressList(lineFile):
    """Return list of addres in array of int.
    """
    adress = addr_extract_whole(lineFile)
    adressOut = []
    for line in adress:
        if line != 0:
            adressOut.append(int(line,16))
    return adressOut
    
def getDataList(lineFile):
    """Return data in array, [[data line 1], [data line 2]...... [data line x]]
    """
    data = data_extract_whole(lineFile)
    dataOut = []
    for line in data:
        if line != 0:
            dataLine = []
            for pos in range(0,len(line),2):
                strHex = line[pos] + line[pos+1]
                dataLine.append(int(strHex,16))
            dataOut.append(dataLine)
    return dataOut
    
def getDataSize(lineFile):
    adressList = getAdressList(lineFile)
    data = getDataList(lineFile)
   
    maxAdress = 0
    idMax = 0
    for idLine in range(0,len(adressList)):
        if adressList[idLine] > maxAdress:
            maxAdress = adressList[idLine]
            idMax = idLine
        
    return maxAdress + len(data[idMax]) - getStartAdress(lineFile)
    
def getStartAdress(lineFile):
    adress = getAdressList(lineFile)
    return min(adress)


def makeBinaryList(lineFile):
    s9_number = s_count(lineFile,9)
    minAdress = getStartAdress(lineFile)
    maxAdress = getDataSize(lineFile) + minAdress
    
    adress = getAdressList(lineFile)
    data = getDataList(lineFile)
    
    dataOut = []
    
    for num in range(0,maxAdress - minAdress):
        dataOut.append(0xFF)
    
    for idLine in range(len(data)):
        idByte = 0
        for byte in data[idLine]:
            dataOut[(adress[idLine] + idByte) - minAdress] = byte
            idByte +=1
    
    return dataOut
        
    

def makeLineList(fileName):
    f=open(fileName,'r')
    f_data=f.read()
    g='\r\n'
    if g in f_data:
        return f_data.split(g)
    else:
        return f_data.split('\n')
    f.close
    
    