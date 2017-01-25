//expEYES-17  Firmware
//Author  : Jithin B.P, jithinbp@gmail.com
//License : GNU GPL version 3
//Date : Dec-2016

#pragma config ICS = NONE               // ICD Communication Channel Select bits (Reserved, do not use)
#pragma config JTAGEN = OFF             // JTAG Enable bit (JTAG is disabled)
#include"commands.h"
#include<xc.h>
#include <p24EP256GP204.h>
#include <stdlib.h>
#include<libpic30.h>
#include"functions.h"


const BYTE version[] = "SJ-2.0"; //Python communication library will check first two letters to determine device type

/* PLL using external oscillator. */
_FOSCSEL(FNOSC_FRC & IESO_OFF); //Start up using internal oscillator
_FOSC(FCKSM_CSECMD & OSCIOFNC_OFF & POSCMD_XT ); // enable failsafe osc, use external crystal

#pragma config WDTPOST = PS512          // Watchdog Timer Postscaler bits (1:512)
#pragma config WDTPRE = PR128           // Watchdog Timer Prescaler bit (1:128)
#pragma config WINDIS = OFF             // Watchdog Timer Window Enable bit (Watchdog Timer in Non-Window mode)
#pragma config FWDTEN = OFF              // Watchdog Timer Enable bit (Watchdog timer always enabled)

#pragma config ALTI2C2 = OFF            // Alternate I2C2 pins (I2C2 mapped to SDA2/SCL2 pins)

int main() {
    LED_OUT=0;
    RCONbits.SWDTEN=1;
    unsigned char main_command,sub_command,RESPONSE;
    unsigned int i = 0, n = 0;
    unsigned int ADLOC;
    pProg=0x0;
    unsigned int *pData;
    init();
    initUART(BRGVAL500000);

    LED_OUT=1;
    /*
     State machine starts here
     -Wait for data
     -First byte received defines a broad category such as 'ADC' or 'TIMING MEASUREMENTS'
     -Second byte received(sub command) determines the specific function to execute within the chosen category
     -  All byte values and their meanings are defined in commands.h
     Once the function call is chosen, the device will read further bytes(arguments) relevant to the chosen function.*/
    while (1) {
        while (!hasChar()){asm("CLRWDT");}  // A watchdog timer prevents the device from freezing up in case the master disconnects midway
        main_command = getChar();
        sub_command = getChar();
        RESPONSE = SUCCESS; //Assume success. This value is modified later on if necessary
        switch (main_command) {
            case FLASH:     // category pertaining to flash memory read and write
                switch(sub_command){
                    case WRITE_FLASH:  // The PIC stores flash data in blocks/pages 1024 words long. this call writes 16 characters into some section of some page.
                        value = getChar(); //fetch the page[0-19]
                        location = getChar(); //fetch the address(0-31)
                        /*-----------fetch 16 characters----------*/
                        for (i = 0; i < 8; i++) {    blk[i] = getInt();       } //two per loop
                        setFlashPointer(value);
                        load_to_flash(p, location, &blk[0]);
                        break;

                    case READ_FLASH: //read relevant section from chosen page
                        value = getChar(); //fetch the page[0-19]
                        location = getChar();
                        setFlashPointer(value);
                        read_flash(p, location);
                        for (i = 0; i < 8; i++) {
                            sendInt(blk[i]);
                            }
                        break;
                    
                    case READ_BULK_FLASH: //read an entire page
                        lsb = getInt();
                        location = getChar();
                        setFlashPointer(location);
                        read_all_from_flash(p);
                        for (i = 0; i < lsb/2; i++) {
                            sendInt(dest[i]);
                        }
                        break;

                    case WRITE_BULK_FLASH: //write an entire page
                        lsb = getInt();
                        location = getChar();
                        for (i = 0; i < lsb/2; i += 1)  {
                            dest[i]=getInt();
                        }
                        setFlashPointer(location);
                        _erase_flash(p); /* erase a page */
                        for (i = 0; i < _FLASH_ROW * 4; i += 1) /*combine two ints each for each word32 write*/ {
                            tmp_int1 = dest[2 * i];
                            tmp_int2 = dest[2 * i + 1];
                            pProg = p + (4 * i);
                            _write_flash_word32(pProg, tmp_int1, tmp_int2); Nop(); Nop();
                        }
                        
                        break;
                }
                break;

            case ADC:
                switch(sub_command){
                    case CAPTURE_12BIT: //12-bit oscilloscope. Single channel
                        value = getChar();  //channel number
                        samples_to_fetch = getInt();
                        ADC_DELAY = getInt();
                        ADC_CHANNELS = 0; //capture one channel
                        disableADCDMA();
                        setADCMode(ADC_12BIT_SCOPE,value&0x7F,0);

                        if(value&0x80)PrepareTrigger(); //bit 6 of value.
                        else TRIGGERED=true;
                        conversion_done = 0;samples=0;
                        buff0 = &ADCbuffer[0];
                        endbuff = &ADCbuffer[samples_to_fetch];
                        setupADC10();
                        _AD1IF = 0;   _AD1IE = 1;
                        LED_OUT=0;//set_RGB(0x060606);
                        break;

                    case CAPTURE_12BIT_SCAN:  //12-bit oscilloscope. Multi channel . Scans through inputs. Python library compensates time difference.
                        ADC_CHANNELS = getChar(); //total channels
                        lsb = getInt();
                        samples_to_fetch = getInt();
                        ADC_DELAY = getInt();
                        setADCMode(ADC_12BIT_SCOPE,0,0);
                        TRIGGERED=true;
                        conversion_done = 0;samples=0;

                        buff0 = &ADCbuffer[0];buff1 = &ADCbuffer[samples_to_fetch];buff2 = &ADCbuffer[2*samples_to_fetch];buff3 = &ADCbuffer[3*samples_to_fetch];  //assume 4 channels. 
                        endbuff = &ADCbuffer[samples_to_fetch];
                        AD1CON1bits.ADON = 0;
                        AD1CON2bits.CSCNA = 1;  //Enable Scanning
                        AD1CON2bits.SMPI = (lsb>>12)&0xF;
                        AD1CSSL=lsb&0xFFF; //scan certain channels
                        AD1CON1bits.ADON = 1;Delay_us(20);

                        setupADC10();
                        _AD1IF = 0;   _AD1IE = 1;
                        LED_OUT=0;//set_RGB(0x060606);
                        break;
                        
                        
                    case CAPTURE_ONE:  //Capture 10 bit ADC readings from 1 channel
                        //disable_input_capture();
                        value = getChar();  //channel number
                        samples_to_fetch = getInt();
                        ADC_DELAY = getInt();

                        ADC_CHANNELS = 0; //capture one channel
                        AD1CON2bits.CHPS = 0;
                        setADCMode(ADC_10BIT_SIMULTANEOUS,value&0x7F,0);
                        AD1CON2bits.CHPS = 0;

                        if(value&0x80)PrepareTrigger(); //bit 6 of value.
                        else TRIGGERED=true;
                        conversion_done = 0;samples=0;
                        buff0 = &ADCbuffer[0];
                        endbuff = &ADCbuffer[samples_to_fetch];
                        setupADC10();
                        _AD1IF = 0;   _AD1IE = 1;
                        LED_OUT=0;//set_RGB_now(0x000A06);
                        break;

                    case CAPTURE_TWO:  //Capture 10 bit ADC readings from 2 channels (Simultaneous)
                        value = getChar();  //channel number
                        samples_to_fetch = getInt();
                        ADC_DELAY = getInt();
                        ADC_CHANNELS = 1; //capture two channels
                        AD1CON2bits.CHPS = 1;
                        setADCMode(ADC_10BIT_SIMULTANEOUS,value&0x7F,0);
                        AD1CON2bits.CHPS = 1;
                        buff0 = &ADCbuffer[0];buff1 = &ADCbuffer[samples_to_fetch];
                        endbuff = &ADCbuffer[samples_to_fetch];
                        if(value&0x80)PrepareTrigger(); //bit 6 of value.
                        else TRIGGERED=true;
                        conversion_done = 0;samples=0;
                        setupADC10();
                        _AD1IF = 0;   _AD1IE = 1;
                        LED_OUT=0;//set_RGB_now(0x0A0000);
                        break;

                    case CAPTURE_FOUR:  //Capture 10 bit ADC readings from 4 channels (Simultaneous)
                        value = getChar();  //channel number for SH0
                        samples_to_fetch = getInt();
                        ADC_DELAY = getInt();
                        ADC_CHANNELS = 3;   //capture all four channels
                        AD1CON2bits.CHPS = ADC_CHANNELS;
                        setADCMode(ADC_10BIT_SIMULTANEOUS,(value&0xF),(value>>4)&0x1);
                        buff0 = &ADCbuffer[0];buff1 = &ADCbuffer[samples_to_fetch];
                        buff2 = &ADCbuffer[2*samples_to_fetch];buff3 = &ADCbuffer[3*samples_to_fetch];
                        endbuff = &ADCbuffer[samples_to_fetch];
                        if(value&0x80)PrepareTrigger(); //bit 8 of value.
                        else TRIGGERED=true;
                        conversion_done = 0;samples=0;
                        setupADC10();
                        _AD1IF = 0;   _AD1IE = 1;
                        LED_OUT=0;
                        break;
                        
                    //The following calls perform some action before immediately starting the oscilloscope

                    case SET_HI_CAPTURE:   //OD1 is set to 5V . Used for transient response measurements etc
                    case SET_LO_CAPTURE:    //OD1 is set to 0V
                    case PULSE_CAPTURE:    // A fixed width pulse on OD1 is output. Echo measurements
                        OD1_PPS = 0; //OD1 mappings disabled
                        //fall through
                    case MULTIPOINT_CAPACITANCE:  // Capacitance measurement using RC discharge
                    case CAPTURE_DMASPEED:
                        value = getChar();  //channel number
                        samples_to_fetch = getInt();
                        ADC_DELAY = getInt();

                        if(sub_command==PULSE_CAPTURE){lsb=getInt();}

                        if(ADC_DELAY<4)ADC_DELAY = 4;                           //maximum capacity is 2msps
                        ADC_CHANNELS = 0;                                       //capture one channel
                        AD1CON2bits.CHPS = 0;
                        _AD1IF = 0;   _AD1IE = 0;                               // Do not enable ADC interrupt. We're using DMA.
                        conversion_done = 1;samples=samples_to_fetch;           //assume it's all over already
                        if(value&0x80){setADCMode(ADC_12BIT_DMA,value&0x7F,0); } 
                        else {setADCMode(ADC_10BIT_DMA,value&0x7F,0); }

                        DMA0STAH = __builtin_dmapage (&ADCbuffer[0]);
                        DMA0STAL = __builtin_dmaoffset (&ADCbuffer[0]);
                        DMA0PAD = (int)&ADC1BUF0;                               // Address of the capture buffer register
                        DMA0CNT = samples_to_fetch-1;                           // Number of words to buffer


                        DMA0CONbits.CHEN = 1;
                        _DMA0IF = 0; _DMA0IE = 1; // Enable DMA interrupt enable bit
                        if(sub_command==SET_LO_CAPTURE)OD1_OUT=0; 
                        else if(sub_command==SET_HI_CAPTURE)OD1_OUT=1; 
                        else if(sub_command==PULSE_CAPTURE){
                            if(lsb&0x8000){OD1_OUT=1;Delay_us(lsb&0x7FFF);OD1_OUT=0;}
                            else{OD1_OUT=0;Delay_us(lsb&0x7FFF);OD1_OUT=1;}
                        }
                        else if(sub_command==MULTIPOINT_CAPACITANCE){ CAP_CHARGE_TRIS=0; CAP_CHARGE_OUT=0;}    //Prepare 20K impedance voltage source, and connect it to 0V.

                        setupADC10();
                        LED_OUT=0;
                        break;

                        
                    case SET_CAP:
                        value = getChar();
                        lsb = getInt();         //Delay uS
                        set_cap_voltage(value,lsb);
                        break;

                    case CONFIGURE_TRIGGER:
                        value = getChar();
                        TRIGGER_CHANNEL=value&0x0F;
                        TRIGGER_LEVEL=getInt();
                        TRIGGER_TIMEOUT=50000;
                        TRIGGER_PRESCALER = (value>>4)&0xF;
                        break;

                    case GET_CAPTURE_STATUS:
                        sendChar(conversion_done|(TRIGGERED<<1));
                        sendInt(samples);
                        break;

                    case SET_PGA_GAIN:
                        location = getChar();
                        value = getChar();
                        setPGA(location, value);
                        break;

                    case SELECT_PGA_CHANNEL:
                        location = getChar();
                        setSensorChannel(location);
                        break;

                    case GET_VOLTAGE:
                        location = getChar();
                        setADCMode(ADC_12BIT,3,0);
                        i=get_voltage(location);
                        sendInt(i);
                        break;

                    case GET_VOLTAGE_SUMMED:
                        location = getChar();
                        i=get_voltage_summed(location);
                        sendInt(i);
                        //sendInt(ADC1BUF0);sendInt(ADC1BUF1);sendInt(ADC1BUF2);sendInt(ADC1BUF3);sendInt(ADC1BUF4);sendInt(ADC1BUF5);sendInt(ADC1BUF6);sendInt(ADC1BUF7);
                        //sendInt(ADC1BUF8);sendInt(ADC1BUF9);sendInt(ADC1BUFA);sendInt(ADC1BUFB);sendInt(ADC1BUFC);sendInt(ADC1BUFD);sendInt(ADC1BUFE);sendInt(ADC1BUFF);
                        break;


                    case GET_CAPTURE_CHANNEL:
                        //disable_input_capture();
                        CAP_CHARGE_OUT=0;CAP_CHARGE_TRIS=1; //set 20K CAP voltage source to high impedance mode.

                        value = getChar();      //channel number
                        lsb = getInt();   //number of bytes
                        msb = getInt();           //offset / starting position
                        for (i = msb; i < msb+lsb; i++) sendInt(ADCbuffer[i+samples_to_fetch*value]);
                        break;


                }
                break;
            case I2C:
                switch(sub_command){
                    case I2C_START:             //Initialize I2C and select device address
                        I2CStart();
                        location = getChar(); //=address<<1 | R/W   [r=1,w=0]
                        I2CSend(location);
                        RESPONSE|=(I2C2STATbits.ACKSTAT<<4)|(I2C2STATbits.BCL<<5);
                        break;

                    case I2C_STOP:
                        I2CStop();              // send stop condition as transfer finishes
                        break;

                    case I2C_WAIT:
                        I2CWait();              // send stop condition as transfer finishes
                        break;

                    case I2C_SEND:
                        value = getChar();
                        I2CSend(value);
                        RESPONSE|=(I2C2STATbits.ACKSTAT<<4)|(I2C2STATbits.BCL<<5);
                        break;

                    case I2C_SEND_BURST:
                        value = getChar();
                        I2CSend(value);
                        RESPONSE=DO_NOT_BOTHER;
                        break;

                    case I2C_RESTART:
                        I2CRestart();
                        location = getChar(); //=address<<1 | R/W   [r=1,w=0]
                        I2CSend(location);
                        RESPONSE|=(I2C2STATbits.ACKSTAT<<4)|(I2C2STATbits.BCL<<5);
                        break;

                    case I2C_READ_MORE:
                        location = I2CRead(1);
                        sendChar(location);
                        break;
                    case I2C_READ_END:
                        location = I2CRead(0);
                        sendChar(location);
                        break;

                    case I2C_CONFIG:
                        I2C_BRGVAL = getInt();
                        initI2C();
                        break;
                        
                    case I2C_STATUS:
                        sendInt(I2C2STAT);
                        break;

                    case I2C_READ_BULK:
                        location=getChar();
                        ca=getChar();
                        value=getChar();
                        I2CStart();
                        I2CSend(location<<1); //Address of I2C slave. write.
                        I2CSend(ca); //I2C slave Memory Address to read from
                        I2CRestart();
                        I2CSend((location<<1)|1); //Address , read
                        for(i=0;i<value-1;i++)sendChar(I2CRead(1));
                        sendChar(I2CRead(0));
                        I2CStop();
                        break;

                    case I2C_WRITE_BULK:
                        location=getChar();
                        value=getChar();
                        I2CStart();
                        I2CSend(location<<1);
                        for(i=0;i<value;i++)I2CSend(getChar());
                        I2CStop();
                        break;

                    case I2C_ENABLE_SMBUS:
                        I2C2STAT = 0x0000;
                        I2C2CONbits.SMEN=1;
                        I2C2CONbits.I2CEN = 1;
                        break;

                    case I2C_DISABLE_SMBUS:
                        I2C2STAT = 0x0000;
                        I2C2CONbits.SMEN=0;
                        I2C2CONbits.I2CEN = 1;
                        break;

                    case I2C_INIT:
                        initI2C();
                        break;

                    case PULLDOWN_SCL:
                        lsb=getInt();
                        _TRISB4 = 0;
                        _LATB4=0;
                        Delay_us(lsb);
                        _LATB4=1;
                        _TRISB4 = 1;
                        break;


                    case I2C_START_SCOPE:
                        I2C_SCOPE_ADDRESS=getChar();
                        I2C_SCOPE_LOCATION=getChar();
                        I2C_SCOPE_BYTES=getChar();
                        I2CTotalSamples=getInt();
                        I2CSamples=0; I2CConvDone=0;
                        bytebuff1 = &ADCbuffer[0];
                        _T2IF = 0;
                        _T2IE = 0;
                        T2CONbits.TON = 0;T2CONbits.T32 = 0;
                        T2CONbits.TSIDL = 1;
                        T2CONbits.TCKPS = 2;
                        PR2 = getInt();
                        TMR2 = 0x0000;
                        LED_OUT=0;//set_RGB_now(0x0A0A00);
                        T2CONbits.TON = 1;
                        _T2IF = 0;
                        _T2IE = 1;

                        break;


                }
                break;
            case DAC:
                switch(sub_command){

                case SET_DAC:
                    lsb = getInt();
                    if(lsb&0x8000)OC3R = lsb&0xFFF;
                    else OC4R = lsb&0xFFF;
                    break;
                }
                break;
            case WAVEGEN:
                switch(sub_command){
                    case SET_SINE1:
                        value = getChar();
                        lsb = getInt();
                        sineWave1(lsb,value);
                        break;

                        
                    case LOAD_WAVEFORM1:
                        for(lsb=0;lsb<WAVE_TABLE_FULL_LENGTH;lsb++)sineTable1[lsb]=getInt();
                        for(lsb=0;lsb<WAVE_TABLE_SHORT_LENGTH;lsb++)sineTable1_short[lsb]=getChar();                            
                        break;

                    case SET_SQR1:  //on OD1
                        lsb = getInt(); //wavelength
                        msb = getInt(); //high time
                        value = getChar(); //prescaler

                        if(value&0x8){sqrs(lsb,msb,value&0x3);}
                        else if(value&0x4){sqr2(lsb,msb,value&0x3);}
                        else{sqr1(lsb,msb,value&0x3);}
                        break;

                    case SET_SQR_LONG:  //on OD1
                        lsb = getInt(); //W1
                        msb = getInt(); //W2
                        tmp_int1 = getInt(); //H1
                        tmp_int2 = getInt(); //H2
                        sqr1_cascade(lsb,msb,tmp_int1,tmp_int2);
                        break;

                    case SET_SINE_AMP:
                        value = getChar();
                        SINE_AMP = value;
                        setOC2Mode(SINE_AMP);
                        break;

                    
                }
                break;
            case DOUT:
                switch(sub_command){
                    case SET_STATE:
                        value = getChar();
                        if(value&0x10){     OD1_PPS = 0;  OD1_OUT  = value&0x1;       } //OD1
                        if(value&0x20){     CCS_TRIS = (value>>1)&0x1;   }                // current source
                        if(value&0x40){     T1CON=0;OC1CON1=0; SQR1_PPS = 0 ;   SQR1_OUT = (value>>2)&0x1; }
                        if(value&0x80){     SQR2_PPS = 0 ;   SQR2_OUT = (value>>3)&0x1;        }
                        break;                        
                        
                }
                break;
            case DIN:
                switch(sub_command){
                    case GET_STATE:
                        //['ID1','SQR1_READ','OD1_READ','SEN','SQR1','OD1','SQ2','SQ3']
                        EnableComparator();
                        sendChar(ID1_READ|(SQR1_READ<<1)|(OD1_READ<<2)|(COMP4_READ<<3)|(SQR1_IN<<4)|(OD1_IN<<5)|(CCS_IN<<6)|(SQR2_IN<<7));
                        RESPONSE = DO_NOT_BOTHER;
                        break;
                }
                break;
            case TIMING:
                switch(sub_command){
                    case GET_TIMING:        //Using input capture
                        _IC1IF=0;
                        lsb = getInt(); //timeout. [t(s)*64e6>>16]
                        value = getChar();
                        location = getChar();
                        SinglePinInterval_IC12(location&0xF,(value>>2)&0x7,value&0x3,true);
                        IC1CON2bits.TRIGSTAT = 1;    IC2CON2bits.TRIGSTAT = 1;

                        while((!_IC1IF) && (IC2TMR<lsb))asm("CLRWDT"); _IC1IF=0;
                        sendInt(IC2TMR);
                        for(n=0;n<(value&0x3);n++){
                        sendInt(IC1BUF);sendInt(IC2BUF); //read from FIFO
                        }
                        disable_input_capture();
                    break;


                    case TIMING_MEASUREMENTS:        //Using two input captures
                        lsb = getInt(); //timeout. [t(s)*64e6>>16]
                        location = getChar();
                        value = getChar();
                        cb = getChar();
                        TimingMeasurements(location&0xF,(location>>4)&0xF,value&0x7,(value>>3)&0x7,cb&0xF,(cb>>4)&0xF);
                        if((value>>6)&1){RPOR5bits.RP54R = 0;_LATC6=(value>>7)&1;}
                        while((!_IC1IF || !_IC3IF) && (IC2TMR<lsb)){asm("CLRWDT");}
                        for(n=0;n<((cb)&0xF);n++){sendInt(IC1BUF);sendInt(IC2BUF);}   //send data from PIN 1
                        for(n=0;n<((cb>>4)&0xF);n++){sendInt(IC3BUF);sendInt(IC4BUF);}//send data from PIN 2
                        _IC3IF=0;_IC1IF=0;
                        sendInt(IC2TMR);
                        disable_input_capture();
                        T2CONbits.TON = 0;
                    break;

                    //not being used.
                    case INTERVAL_MEASUREMENTS:        //Using two input captures
                        lsb = getInt(); //timeout. [t(s)*64e6>>16]
                        location = getChar();
                        value = getChar();
                        Interval(location&0xF,(location>>4)&0xF,value&0x7,(value>>3)&0x7);
                        while((!_IC1IF) && (IC2TMR<lsb)){asm("CLRWDT");}
                        sendInt(IC1BUF);sendInt(IC2BUF);
                        while((!_IC3IF) && (IC2TMR<lsb)){asm("CLRWDT");}
                        sendInt(IC3BUF);sendInt(IC4BUF);
                        sendInt(IC2TMR);
                        disable_input_capture();
                    break;


                    case SINGLE_PIN_EDGES:
                        disable_input_capture();
                        lsb = getInt(); //timeout. [t(s)*64e6>>16]
                        location = getChar(); //pin
                        value = getChar();    //edge
                        cb = getChar();       //interrupts
                        cc = getChar();       //set_state
                        SinglePinInterval_IC12(location,value&0xF,cb,true);
                        if(cc){
                            if(cc&0x10){     OD1_PPS = 0;  OD1_OUT  = cc&0x1;       } //OD1
                            if(cc&0x20){     _TRISB14=(cc>>1)&0x1;   }                // current source
                            if(cc&0x40){    SQR1_PPS = 0 ;   SQR1_OUT = (cc>>2)&0x1;   }  //square 1
                            if(cc&0x80){    SQR2_PPS = 0 ;   SQR2_OUT = (cc>>3)&0x1;   }   //square 2
                        }
                        IC1CON2bits.TRIGSTAT = 1;    IC2CON2bits.TRIGSTAT = 1;

                        while((!_IC1IF) && (IC2TMR<lsb) ){asm("CLRWDT"); }
                        for(n=0;n<((cb)&0xF);n++){sendInt(IC1BUF);sendInt(IC2BUF);}   //send data from PIN 1
                        _IC1IF=0;
                        sendInt(IC2TMR);
                        disable_input_capture();
                    break;
                    
                    case DOUBLE_PIN_EDGES:
                        disable_input_capture();
                        lsb = getInt(); //timeout. [t(s)*64e6>>16]
                        location = getChar();
                        value = getChar();
                        cb = getChar();   
                        SinglePinInterval_IC12(location&0xF,value&0xF,cb&0x7,false);
                        if((cb&0x80)){SinglePinInterval_IC34((location>>4)&0xF,(value>>4)&0xF,(cb>>4)&0x7,16,false );}  //Auto trigger using IC1
                        else{SinglePinInterval_IC34((location>>4)&0xF,(value>>4)&0xF,(cb>>4)&0x7,0,false);}  //No auto trigger . SYNCSEL =0 
                        ActivateDoubleEdges(value&0xF,(value>>4)&0xF);
                        //IC1CON2bits.TRIGSTAT = 1;IC2CON2bits.TRIGSTAT = 1;
                        if((cb&0x80)==0){IC3CON2bits.TRIGSTAT = 1;IC4CON2bits.TRIGSTAT = 1;} //trigger if auto trigger is not defined
                        
                        while((!_IC1IF) && (IC2TMR<lsb) ){asm("CLRWDT"); }
                        for(n=0;n<((cb)&0x7);n++){sendInt(IC1BUF);sendInt(IC2BUF);}   //send data from PIN 1
                        while((!_IC3IF) && (IC2TMR<lsb) ){asm("CLRWDT"); }
                        for(n=0;n<((cb>>4)&0x7);n++){sendInt(IC3BUF);sendInt(IC4BUF);}   //send data from PIN 2

                        _IC2IF=0;_IC3IF=0;
                        sendInt(IC2TMR);
                        disable_input_capture();
                    break;
                    
 

                }
                break;
            case COMMON:
                switch(sub_command){
                    case GET_CTMU_VOLTAGE:
                        value=getChar();                                        //bits<0-4> = channel,bits <5-6> current range
                        msb = get_ctmu_voltage(value&0x1F,(value>>5)&0x3,(value>>7)&0x1);
                        //sendInt(ADC1BUF0);sendInt(ADC1BUF1);sendInt(ADC1BUF2);sendInt(ADC1BUF3);sendInt(ADC1BUF4);sendInt(ADC1BUF5);sendInt(ADC1BUF6);sendInt(ADC1BUF7);
                        //sendInt(ADC1BUF8);sendInt(ADC1BUF9);sendInt(ADC1BUFA);sendInt(ADC1BUFB);sendInt(ADC1BUFC);sendInt(ADC1BUFD);sendInt(ADC1BUFE);sendInt(ADC1BUFF);
                        sendInt(msb);
                    break;

                    case GET_CAP_RANGE:
                        msb=getInt();               //Charge time.  microseconds
                        sendInt(get_cap_range(msb));
                    break;

                    case START_CTMU:
                        value=getChar();    //bits<0-6> =  current range, bit 7=TGEN
                        location=getChar();    // current trim
                        CTMUCON1bits.CTMUEN = 0;
                        CTMUCON1bits.TGEN = (value>>7)&0x1;                     //(channel==5)?1:0;
                        CTMUICONbits.ITRIM = location;
                        CTMUICONbits.IRNG = (value)&0x7F;                       // 01->Base Range .53uA, 10->base*10, 11->base*100, 00->base*1000
                        CTMUCON1bits.CTTRIG = 0; //do not trigger the ADC
                        CTMUCON1bits.CTMUEN = 1;Delay_us(1000);
                        CTMUCON2bits.EDG1STAT = 1;  // Start current source
                        break;

                    case STOP_CTMU:
                        disableCTMUSource();
                        break;
                    
                    
                    case GET_CAPACITANCE:
                        value=getChar();            //current range for CTMU
                        location=getChar();         //current trimming bits
                        msb=getInt();               //Charge time.  microseconds
                        LED_OUT=0;
                        sendInt(get_cc_capacitance(value,location,msb));
                        LED_OUT=1;
                    break;


                    case GET_HIGH_FREQUENCY:        //This one shares TIMER5 with the ADC! and uses TMR2,3 in cascaded mode
                        LED_OUT=0;
                        value=getChar();
                        get_high_frequency(value&0xF);
                        while(!_T5IF);_T5IF=0;
                        freq_lsb=TMR2;
                        freq_msb=TMR3HLD;
                        sendLong(freq_lsb,freq_msb);
                        LED_OUT=1;
                        break;

                    case GET_ALTERNATE_HIGH_FREQUENCY:   //Discontinued.
                        LED_OUT=0;
                        value=getChar();
                        sendLong(0,0);
                        LED_OUT=1;
                        break;

                    case GET_FREQUENCY:        //Using input capture
                        _IC1IF=0;
                        lsb = getInt(); //timeout. [t(s)*64e6>>16]
                        value = getChar();
                        SinglePinInterval_IC12(value,EVERY_FOURTH_RISING_EDGE,2,true);
                        IC1CON2bits.TRIGSTAT = 1;  IC2CON2bits.TRIGSTAT = 1;

                        while((IC2TMR<lsb) && (!_IC1IF))asm("CLRWDT");  _IC1IF=0; RPINR7bits.IC1R =0; //disconnect
                        if((IC2TMR>=lsb) || (IC2CON1bits.ICOV))sendChar(1);             //in case of buffer overflow/timeout
                        else sendChar(0);
                        sendInt(IC1BUF);sendInt(IC2BUF);
                        sendInt(IC1BUF);sendInt(IC2BUF);
                        disable_input_capture();
                        break;

                    case GET_VERSION:
                        for (i = 0; i < sizeof(version)-1; i++) sendChar(version[i]);
                        value = 0;
                        #ifdef NRF_ENABLED
                        value|=1;
                        #endif

                        #ifdef OLED_ENABLED
                        value|=2;
                        #endif

                        #ifdef HX711_ENABLED
                        value|=4;
                        #endif

                        #ifdef HCSR04_ENABLED
                        value|=8;
                        #endif
                                
                        sendChar(value);
                        sendChar('\n');
                        RESPONSE = DO_NOT_BOTHER;
                        break;

                    case RETRIEVE_BUFFER:
                        lsb = getInt();   //starting point
                        msb = getInt();   //number of bytes
                        for (i = lsb; i < msb+lsb; i++) sendInt(ADCbuffer[i]);
                        LED_OUT=1;
                        break;
                    case CLEAR_BUFFER:
                        lsb = getInt();   //starting point
                        msb = getInt();   //number of bytes
                        for (i = lsb; i < msb+lsb; i++) ADCbuffer[i]=0;
                        break;

                    case FILL_BUFFER:
                        lsb = getInt();   //starting point
                        msb = getInt();   //number of bytes
                        for (i = lsb; i < msb+lsb; i++) ADCbuffer[i]=getInt();
                        break;




                    case READ_PROGRAM_ADDRESS:
                        pProg=0x0;
                        l1=getInt()&0xFFFF;
                        l2=getInt()&0xFFFF;
                        _memcpy_p2d16(&ADLOC, pProg+(l1|(l2<<16)),sizeof(unsigned int));
                        sendInt(ADLOC);
                        break;


                    case WRITE_PROGRAM_ADDRESS:
                        pProg=0x0;
                        l1=getInt()&0xFFFF;
                        l2=getInt()&0xFFFF;
                        ADLOC=getInt();
                        //__builtin_tbladdress(p,(l1|(l2<<16)) );  //initialize flash pointer
                        //load_to_flash(p, location, &blk[0]);
                        //_memcpy_p2d16(p,ADLOC ,sizeof(unsigned int));
                        break;

                    case READ_DATA_ADDRESS:
                        lsb=getInt()&0xFFFF;
                        pData=lsb;
                        sendInt(*pData);
                        break;

                    case WRITE_DATA_ADDRESS:
                        msb=getInt();
                        lsb=getInt();
                        pData=msb;
                        *pData=lsb;
                        break;

                    case READ_LOG:
                        while(error_readpos!=error_writepos){
                            sendChar(*error_readpos++);
                            if(error_readpos==&errors[ERROR_BUFFLEN])error_readpos=&errors[0];
                        }
                        sendChar('\n');
                        break;


                    case HCSR04:            //distance sensor
                        SQR2_PPS = 0;
                        lsb = getInt(); //timeout. [t(s)*64e6>>16]
                        SQR2_OUT = 1;  //SQR1  high
                        SinglePinInterval_IC12(0,EVERY_RISING_EDGE,1,false);
                        SinglePinInterval_IC34(0,EVERY_FALLING_EDGE,1,16,false);
                        ActivateDoubleEdges(EVERY_RISING_EDGE,EVERY_FALLING_EDGE);
                        //IC1CON2bits.TRIGSTAT = 1;  IC2CON2bits.TRIGSTAT = 1;
                        Delay_us(10);
                        SQR2_OUT =0;   //SQR1 low
                        while((IC2TMR<lsb) && (!_IC3IF))asm("CLRWDT");  _IC1IF=0; RPINR7bits.IC1R =0; //disconnect
                        if((IC2TMR>=lsb) || (IC2CON1bits.ICOV))sendChar(1);             //in case of buffer overflow/timeout
                        else sendChar(0);

                        sendInt(IC3BUF);sendInt(IC4BUF);

                        disable_input_capture();
                        break;


                    #ifdef HX711_ENABLED
                    case HX711:
                        value = getChar();  //25:chan A 128x , 26: chan B 32x, 27: chan A 64x, 0: turn off, 1: turn on

                        OD1_PPS = 0;   //CLOCK
                        if(value==0)OD1_OUT = 1;
                        else if(value==1)OD1_OUT=0;
                        else{
                            lsb=0;msb=0;
                            if(ID1_READ==1){  //data not ready
                                lsb=0x100;
                            }else{
                                for(i=0;i<16;i++){
                                    OD1_OUT=1; Delay_us(1);
                                    msb<<=1;msb|=ID1_READ;
                                    OD1_OUT=0; Delay_us(1);
                                    }
                                for(i=0;i<8;i++){
                                    OD1_OUT=1; Delay_us(1);
                                    lsb<<=1;lsb|=ID1_READ;
                                    OD1_OUT=0; Delay_us(1);
                                    }
                                for(i=0;i<value-24;i++){
                                    OD1_OUT=1; Delay_us(1);
                                    OD1_OUT=0; 
                                    }
                            }
                        sendInt(msb);
                        sendInt(lsb);

                        }
                        break;
                    #endif  

                }
                break;

                

            case SETBAUD:
                    initUART(sub_command);
                    break;

         }
        if(RESPONSE)ack(RESPONSE);


    }


    return (EXIT_SUCCESS);
}

