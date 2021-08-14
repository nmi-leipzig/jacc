`timescale 1ps/1ps

module clk_synth_test

 (// Clock in ports
  input         clk_in1,
  // Clock out ports
  output        clk_out0,
  output        clk_out1,
  // Status and control signals
  input         reset,
  output        locked

 );

  wire        clk_out0_pll;
  wire        clk_out1_pll;
  wire        clk_out2_pll;
  wire        clk_out3_pll;
  wire        clk_out4_pll;
  wire        clk_out5_pll;
  wire        clk_out6_pll;
  wire        clk_out7_pll;

  wire        locked_int;
  wire        clkfbout_pll;


  wire        reset_high;


  
  PLLE2_BASE#(.BANDWIDTH("OPTIMIZED"),//OPTIMIZED,HIGH,LOW
  .CLKFBOUT_MULT        (64),//MultiplyvalueforallCLKOUT,(2-64)
  .CLKFBOUT_PHASE       (0.0),//Phase offset in degrees of CLKFB, (-360.000-360.000).
  .CLKIN1_PERIOD        (52.6), //Input clock period in ns tops resolution (i.e.33.333is30MHz).
  
  //CLKOUT0_DIVIDE-CLKOUT5_DIVIDE:DivideamountforeachCLKOUT(1-128)
  .CLKOUT0_DIVIDE       (1),
  .CLKOUT1_DIVIDE       (128),
  //.CLKOUT2_DIVIDE(1),
  //.CLKOUT3_DIVIDE(1),
  //.CLKOUT4_DIVIDE(1),
  //.CLKOUT5_DIVIDE(1),
  
  //CLKOUT0_DUTY_CYCLE-CLKOUT5_DUTY_CYCLE:DutycycleforeachCLKOUT(0.001-0.999).
  .CLKOUT0_DUTY_CYCLE(0.25),
  //.CLKOUT1_DUTY_CYCLE(0.5),
  //.CLKOUT2_DUTY_CYCLE(0.5),
  //.CLKOUT3_DUTY_CYCLE(0.5),
  //.CLKOUT4_DUTY_CYCLE(0.5),
  //.CLKOUT5_DUTY_CYCLE(0.5),
  
  //CLKOUT0_PHASE-CLKOUT5_PHASE:PhaseoffsetforeachCLKOUT(-360.000-360.000).
  .CLKOUT0_PHASE(180.0),
  //.CLKOUT1_PHASE(0.0),
  //.CLKOUT2_PHASE(0.0),
  //.CLKOUT3_PHASE(0.0),
  //.CLKOUT4_PHASE(0.0),
  //.CLKOUT5_PHASE(0.0),
  .DIVCLK_DIVIDE        (1),//Masterdivisionvalue,(1-56)
  //.REF_JITTER1(0.0),//ReferenceinputjitterinUI,(0.000-0.999).
  .STARTUP_WAIT         ("FALSE")//DelayDONEuntilPLLLocks,("TRUE"/"FALSE")
  )
  PLLE2_BASE_inst(//ClockOutputs:1-bit(each)output:Userconfigurableclockoutputs
  .CLKOUT0              (clk_out0_pll),
  .CLKOUT1              (clk_out1_pll),
  .CLKOUT2              (clk_out2_pll),
  .CLKOUT3              (clk_out3_pll),
  .CLKOUT4              (clk_out4_pll),
  .CLKOUT5              (clk_out5_pll),
  
  //FeedbackClocks:1-bit(each)output:Clockfeedbackports
  .CLKFBOUT             (clkfbout_pll),//1-bitoutput:Feedbackclock//StatusPort:1-bit(each)output:
  .LOCKED               (locked_int),//1-bitoutput:LOCK//ClockInput:1-bit(each)input:Clockinput
  .CLKIN1               (clk_in1),//1-bitinput:Inputclock//ControlPorts:1-bit(each)input:PLLcontrolports
  .PWRDWN               (1'b0),//1-bitinput:Power-down
  .RST                  (reset_high),//1-bitinput:Reset//FeedbackClocks:1-bit(each)input:Clockfeedbackports
  .CLKFBIN              (clkfbout_pll)//1-bitinput:Feedbackclock
  );
  
  assign reset_high = reset;
  assign locked = locked_int;
  
  BUFG clkout0_buf
   (.O   (clk_out0),
    .I   (clk_out0_pll));

  BUFG clkout1_buf
   (.O   (clk_out1),
    .I   (clk_out1_pll));




endmodule
