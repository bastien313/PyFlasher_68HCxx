
        *****************************************************
        * BootLoader To jump in BF00 Progrmer utility       *
        *                                                   *
        * Rev A : B.S. 11/2021                              *
        *****************************************************
		
PROGRAM		EQU		$BF00	EPROM prog utility in boot ROM		
DEBUT   	EQU     $0006;             Adresse debut programme RAM

* -------------------------------------------------------------------------
* Organisation de la RAM
* -------------------------------------------------------------------------
* Adresses $0002 et $0003  :  Adresse debut EPROM
* Adresses $0006 …    	   :  Programme 

* -------------------------------------------------------------------------

			ORG     $0000;             Origine RAM
			BRA     BLPROG;            Branchement debut de programme
			ORG     DEBUT;             Origine debut de programme

BLPROG		LDAA	#$04	Pattern for DWOM off, no SPI
			STAA	$1028	Turns off DWOM in target MCU
			LDY		$0002
			JMP		PROGRAM	Jumps to EPROM prog routine
ENDBPR		EQU		*


END.
* -------------------------------------------------------------------------
