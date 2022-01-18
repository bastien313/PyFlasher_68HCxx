
        *****************************************
        * BootLoader 68HCxxx   pour EPROM       *
        * A8NS3P.ASM                            *
        * Rev A : E.J. 11/2001                  *
        *****************************************

        * 1.0 : Declarations
        * ==================
        * 1.1 : Declaration des registres
        * -------------------------------

REGIST  EQU     $1000;             Adresse registres de base
PORTB   EQU     $1004;             Port B
SCDR    EQU     $102F;             Registre donn‚e SCI
CONFIG  EQU     $103F;             Registre configuration

XPORTB  EQU     $04;               Port B
XSPCR   EQU     $28;               Registre controle SPI
XBAUD   EQU     $2B;               Registre BAUD SCI
XSCSR   EQU     $2E;               Registre status SCI
XPPROG  EQU     $3B;               Registre programmation EPROM

        * 1.2 : Constantes divers
        * -----------------------

DEBUT   EQU     $0008;             Adresse debut programme RAM
FIN     EQU     $00EC;             Adresse fin programme RAM
STACK   EQU     $00FF;             Adresse haute de la pile
CR      EQU     $0D;               Caractere retour chariot
TIMPRO  EQU     600;               Valeur pour 3 ms prog. EPROM (Clk = 2 Mhz)

        * 1.3 : Declaration des variables
        * -------------------------------

* -------------------------------------------------------------------------
* Organisation de la RAM
* -------------------------------------------------------------------------
* Adresse  $0002           :  (0) -> Pas EPROM / (2) -> EPROM presente
* Adresse  $0003           :  Registre configuration 68HCxxx
* Adresses $0004 et $0005  :  Adresse debut EPROM
* Adresses $0006 et $0007  :  Adresse fin   EPROM
* Adresses $0008 …  $00EC  :  Programme A8NS3E
* Adresse  $00ED           :  STATUS Status operation
* Adresses $00EE et $00EF  :  CHKSUM Checksum calcule
* Adresses $00F0 et $00F1  :  ADRFIN Adresse de fin
* Adresses $00F2 …  $00FF  :  Pile
* -------------------------------------------------------------------------

        * 2.0 : Programme principal
        * =========================

        ORG     $0000;             Origine RAM

START0: BRA     START1;            Branchement debut de programme

        ORG     DEBUT;             Origine debut de programme

START1: LDAA    #'<';              Caractere '<' (Pas de programmation)
        STAA    STATUS;            Rangement dans STATUS
        LDX     #REGIST;           X : Pointeur registres
        BCLR    XSPCR,X,$20;       Port D en drain ouvert
        BCLR    XBAUD,X,$03;       BAUD = 9600
        BSET    XPORTB,X,$01;      Allumage LED
STABCL: BSR     RECCAR;            Attente reception serie
        CMPA    #'P';              Programmation ?
        BNE     START2;            Non : Continuer @
        BSR     PROEEP;            Oui : Traiter la programmation
START2: CMPA    #'L';              Lecture ?
        BNE     START3;            Non : Continuer @
        BSR     LECEEP;            Oui : Traiter la lecture
START3: CMPA    #'S';              Demande Checksum programme EPROM ?
        BNE     START4;            Non : Continuer @
        LDD     $0006;             Oui : Derniere adresse
        STD     ADRFIN;            Rangement
        LDX     $0004;             Premiere adresse
        BRA     START5;            Continuer @
START4: CMPA    #'R';              Demande Checksum BootLoader ?
        BNE     START6;            Non : Continuer @
        LDD     #FIN;              Oui : Adresse dernier octet programme
        STD     ADRFIN;            Rangement
        LDX     #DEBUT;            Adresse 1er octet programme
START5: BSR     CALCHK;            Calcul Checksum
        BSR     TRSCAR;            Envoi partie haute
        TBA;                       Transfert de B dans A
        BSR     TRSCAR;            Envoi partie basse
START6: LDAA    STATUS;            Status
        BSR     TRSCA2;            Envoi du STATUS
        BRA     STABCL;            Boucler @
***************************************************************************
* Reception caractere serie sur la SCI                                    *
* Sortie : Valeur re‡ue dans A                                            *
***************************************************************************
RECCAR: PSHX;                       Sauvegarde de X
        LDX     #REGIST;            Pointer les registres
RECCA1: BRCLR   XSCSR,X,$20,RECCA1; Attente reception serie
        LDAA    SCDR;               Lire la donnee et la placer dans A
        PULX;                       Restitution adresse registres
        RTS;                        Retour
***************************************************************************
* Calcul cheksum sur portion de memoire                                   *
* Entree : X --> Adresse debut de memoire                                 *
* Entree : ADRFIN --> Adresse fin de memoire                              *
* Valeur checksum sur 16 bits dans CHKSUM                                 *
***************************************************************************
CALCHK: CLRA;
        CLRB;                      D = 0
        STD     CHKSUM;            Init Checksum
        DEX;                       Pointeur - 1
CALCH1: INX;                       Pointeur + 1
        LDAB    0,X;               Lecture donnee
        CLRA;                      A = 0
        ADDD    CHKSUM;            Additionner
        STD     CHKSUM;            Rangement
        CPX     ADRFIN;            Derniere adresse ?
        BLO     CALCH1;            Non : Boucler @
        RTS;                       Retour
***************************************************************************
* Emission serie sur la SCI                                               *
* Entree : TRSCA2 --> Envoi valeur  + CR sur la SCI                       *
* Entree : TRSCAR  --> Envoi valeur sur la SCI                            *
* La valeur a envoyer se trouve dans A                                    *
***************************************************************************
TRSCA2: BSR     TRSCAR;             Envoi donnee
        LDAA    #CR;                Separateur (Retour chariot)
TRSCAR: PSHX;                       Sauvegarde de X
        LDX     #REGIST;            Pointer les registres
TRSCA1: BRCLR   XSCSR,X,$80,TRSCA1; Attente emission libre
        STAA    SCDR;               Envoi donnee
        PULX;                       Restitution de X
        RTS;                        Retour
***************************************************************************
* Lecture et envoi contenu EPROM                                          *
* Entree : $0004 --> Adresse debut EPROM                                  *
* Entree : $0006 --> Adresse fin EPROM                                    *
* Valeur checksum sur 16 bits dans CHKSUM                                 *
***************************************************************************
LECEEP: LDAA    CONFIG;            Registre configuration 68HCxxx
        BSR     TRSCAR;            Envoi
        BRCLR   $02,$01,LECEE1;    EPROM presente ? Non : Sortir
        LDY     $0004;             1ere adresse EPROM
        DEY;                       Pointeur - 1
LECEE2: INY;                       Pointeur + 1
        LDAA    0,Y;               Lecture donnee
        BSR     TRSCAR;            Envoi
        CPY     $0006;             Derniere adresse + 1 ?
        BLO     LECEE2;            Non : Boucler @
LECEE1: CLRA;                      A = 0
        RTS;                       Retour
***************************************************************************
* Programmation EPROM                                                     *
* Entree : $0004 --> Adresse debut EPROM                                  *
* Entree : $0006 --> Adresse fin EPROM                                    *
* Valeur checksum sur 16 bits dans CHKSUM                                 *
***************************************************************************
PROEEP: LDAA    CONFIG;            Valeur registre configuration
        BSR     TRSCAR;            Transmission
        BRCLR   $02,$02,LECEE1;    Continuer @ si la EPROM est absente
        LDX     #$0000;            Init compteur octets
        LDY     $0004;             Adresse 1er emplacement EPROM
        DEY;                       Pointeur - 1
PROEE4: INY;                       Pointeur + 1
        BSR     RECCAR;            Attente reception caractere
        PSHX;                      Sauvegarde de X
        LDX     #REGIST;           Pointer les registres
        BSR     PROEE1;            Ecriture EPROM
        BEQ     PROEE2;            Si pas de defaut continuer @
        LDAA    #'F';              Sinon : Caractere 'F' (Fail)
        PULX;                      Restitution de X
        BRA     PROEE3;            Sortir
PROEE2: BSR     TRSCAR;            Fin de programmation (AR)
        PULX;                      Restitution de X
        INX;                       X + 1
        CPY     $0006;             Derniere adresse + 1 ?
        BLO     PROEE4;            Non : Boucler @
        LDAA    #'>';              Oui : Caractere '>' (Programmation OK)
PROEE3: STAA    STATUS;            Rangement STATUS
        CLR     PORTB;             Extinction LED
        RTS;                       Retour
PROEE1: BSET    XPPROG,X,$20;      EPROM en ecriture (ELAT = 1)
PROEE5: STAA    0,Y;               Ecriture donnee
        BSET    XPPROG,X,$01;      Tension de programmation EPROM
        LDX     #TIMPRO;           Temporisation programmation EPROM
PROEE6: DEX;                       X = X - 1
        NOP;                       Delai
        NOP;                       Delai
        BNE     PROEE6;            Boucler @ si non nul
        LDX     #REGIST;           Pointer les registres
        CLR     XPPROG,X;          Arret programmation (EPROM en lecture)
        CMPA    0,Y;               Comparaison
        RTS;                       Retour
* -------------------------------------------------------------------------
* Variables programme
* -------------------------------------------------------------------------
STATUS  DS      1;                 Status op‚ration
CHKSUM  DS      2;                 Checksum calcul‚
ADRFIN  DS      2;                 Adresse de fin

END.
* -------------------------------------------------------------------------
