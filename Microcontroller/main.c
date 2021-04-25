#include <msp430.h>
#include <string.h>

void output_str(char *output);
char input_str[100] = "";

int main(void)
{
  WDTCTL = WDTPW + WDTHOLD;                 // Stop WDT
  if (CALBC1_1MHZ==0xFF)		    // If calibration constant erased
  {											
    while(1);                               // do not load, trap CPU!!	
  }
  P1DIR |= BIT0;
  P1OUT &= ~BIT0;
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

  __bis_SR_register(LPM0_bits + GIE);       // Enter LPM0, interrupts enabled
}

//  Map input to an output string and send that
#pragma vector=USCIAB0RX_VECTOR
__interrupt void USCI0RX_ISR(void)
{
  P1OUT ^= BIT0;
  size_t len = strlen(input_str);
  if(UCA0RXBUF != '\r'){                        //While enter hasn't been pressed
    input_str[len] = UCA0RXBUF;                 //Add to the input string
  }
  else{
    input_str[len] = '\0';
    /*switch(input_str){                          //I guess some sort of switch/
        case some_input:                          //Mapping would determine what
          some_output_method()                    //output command to execute
        break;
        ...
      }
      */

    output_str(input_str);                      //In this case the input is fed-back to the output
    memset(input_str,0,strlen(input_str));      //Clear input on enter press
  }

  IFG2 &= ~UCA0RXIFG;                           //Clear Rx flag
}

//Sends output string by sending each individual character that composes it, confirm TX buffer is ready first
void output_str(char *output){
  for(int i=0; output[i] != '\0'; i++){
    while (!(IFG2&UCA0TXIFG));                  // USCI_A0 TX buffer ready?
    UCA0TXBUF = output[i];                      //TX -> output character
  }
}

