#include <msp430.h>
#include <string.h>

void output_str(char *output);
char input_str[255] = "";
int return_flag = 0;    //Flag that describes the state of RX => 0 -> Unconfirmed, 1 -> Fail, 2 -> Success, 3 -> Timeout
int count = 5;  //Seconds to wait until retransmission due to unconfirmation

int main(void)
{
  WDTCTL = WDTPW + WDTHOLD;                 // Stop WDT
  if (CALBC1_1MHZ==0xFF)		    // If calibration constant erased
  {											
    while(1);                               // do not load, trap CPU!!	
  }
  DCOCTL = 0;                               // Select lowest DCOx and MODx settings
  BCSCTL1 = CALBC1_1MHZ;                    // Set DCO
  DCOCTL = CALDCO_1MHZ;
  P1SEL = BIT1 + BIT2 ;                     // P1.1 = RXD, P1.2=TXD
  P1SEL2 = BIT1 + BIT2 ;                    // P1.1 = RXD, P1.2=TXD
  UCA0CTL1 |= UCSSEL_2;                     // SMCLK
  UCA0BR0 = 104;                            // 1MHz 9600
  UCA0BR1 = 0;                              // 1MHz 9600
  UCA0MCTL = UCBRS0;                        // Modulation UCBRSx = 1
  UCA0CTL1 &= ~UCSWRST;                     // **Initialize USCI state machine**
  IE2 |= UCA0RXIE;                          // Enable USCI_A0 RX interrupt
  
  TA0CTL = TASSEL_1 + MC_0;                 //ACLK, off-mode
  TA0CCTL0 = CCIE;                          //Enable capture compare interrupt
  TA0CCR0 = 32768;                          //Set CCR0 to 1 of crystal clock count so 1s/1 = 1s
  
  output_str("AT+WIFICONN=ssid,pwd\r\n");   //Send => Connect to WiFi - insert own ID + pwd
  TA0CTL &= ~MC_0;                          
  TA0CTL |= MC_1;                           //Switch on Timeout timer
  __enable_interrupt();
  
  while(!(return_flag ==  2)){              //Wait if no success yet
    if(return_flag == 3 || return_flag == 1){   //If failed, retry
      output_str("AT+WIFICONN=ssid,pwd\r\n");
      TA0CTL &= ~MC_0;
      TA0CTL |= MC_1;
    }
    __bis_SR_register(LPM0_bits + GIE);       // Enter LPM0, interrupts enabled
  }
  return_flag = 0;                         //Reset flag
  
  output_str("AT+MQTTUSERCFG=0,1,'client_id','usr','pwd'\r\n");
  while(!(return_flag ==  2)){
    if(return_flag == 3 || return_flag == 1){
      output_str("AT+MQTTUSERCFG=0,'client_id','usr','pwd'\r\n");
      TA0CTL &= ~MC_0;
      TA0CTL |= MC_1;
    }
    __bis_SR_register(LPM0_bits + GIE);       // Enter LPM0, interrupts enabled
  }
  return_flag = 0;
  
  output_str("AT+MQTTCONNCFG=0,1,0,CON,CON_DISCONNECT,1\r\n");   //Send => Try and connect to broker - insert parameters
  while(!(return_flag ==  2)){
    if(return_flag == 3 || return_flag == 1){
      output_str("AT+MQTTCONNCFG=0,1,0,CON,CON_DISCONNECT...,1,0\r\n");
      TA0CTL &= ~MC_0;
      TA0CTL |= MC_1;
    }
    __bis_SR_register(LPM0_bits + GIE);       // Enter LPM0, interrupts enabled
  }
  return_flag = 0;
  
 output_str("AT+MQTTCONN=0,'host','port',1\r\n");  
  while(!(return_flag ==  2)){
    if(return_flag == 3 || return_flag == 1){
      output_str("AT+MQTTCONN=0,'host','port',1\r\n");
      TA0CTL &= ~MC_0;
      TA0CTL |= MC_1;
    }
    __bis_SR_register(LPM0_bits + GIE);       // Enter LPM0, interrupts enabled
  }
  return_flag = 0;
  
  output_str("AT+MQTTSUB=0,CON/...,0\r\n"); 
  
  __bis_SR_register(LPM0_bits + GIE);       // Enter LPM0, interrupts enabled
}

//  Map input to an output string and send that
#pragma vector=USCIAB0RX_VECTOR
__interrupt void USCI0RX_ISR(void)
{
  size_t len = strlen(input_str);
  if(UCA0RXBUF != '\r'){                        //While enter hasn't been pressed
    input_str[len] = UCA0RXBUF;                 //Add to the input string
  }
  else{
    input_str[len] = '\0';                      //Add termination
    if (!(strcmp(input_str,"FAIL"))){
      return_flag = 1;
      __bic_SR_register_on_exit(LPM0_bits);
    }
    else if (!(strcmp(input_str,"OK"))){
      return_flag = 2;
      __bic_SR_register_on_exit(LPM0_bits);
    }
    else if (!strcmp(input_str,"MQTTSUBRECV:0,CON/...,12,CON_REQ_CMDS\r\n"))){
      output_str("AT+MQTTPUB=0,CON,CON_CMDS...,0,0\r\n"); 
    }
    /*
    Other if statements for commands received  
    */

    memset(input_str,0,strlen(input_str));      //Clear input on enter press
  }

  IFG2 &= ~UCA0RXIFG;                           //Clear Rx flag
}

//Timeout interrupt. Set a flag when it happens
#pragma vector = TIMER0_A0_VECTOR
__interrupt void TIMER_A0(void){
  if(count == 0){                               //if 5 seconds have passed
    return_flag = 3;                            //Timeout
    TA0CTL &= ~MC_1;
    TA0CTL |= MC_0;                             //Stop timer
    count = 5;                                  //Reset count
    __bic_SR_register_on_exit(LPM0_bits);
  }
  else{
    count--;
  }
}

//Sends output string by sending each individual character that composes it, confirm TX buffer is ready first
void output_str(char *output){
  for(int i=0; output[i] != '\0'; i++){
    while (!(IFG2&UCA0TXIFG));                  // USCI_A0 TX buffer ready?
    UCA0TXBUF = output[i];                      //TX -> output character
  }
}
