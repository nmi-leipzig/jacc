`timescale 1ps/1ps

module clk
    (
        output  clkout0,
        output  clkout0b,
        output  clkout1,
        output      clkout1b,
        output      clkout2,
        output      clkout2b,
        output      clkout3,
        output      clkout3b,
        output      clkout4,
        output      clkout5,
        output      clkout6,
        output      clkfbout,
        output      clkboutb,
        output      locked,
        input       clkin1,
        input       pwrdwn,
        input       rst,
        input       clkfbin
    );
    
    //Here could be your code for wires and input buffers

    MMCME2_BASE #(
        .DIVCLK_DIVIDE        (1),
        .CLKFBOUT_MULT_F      (60.000),
        .CLKOUT0_DIVIDE_F     (1.000),
        .CLKOUT1_DIVIDE       (2),
        .CLKOUT1_PHASE        (180.000),
        .CLKOUT1_DUTY_CYCLE   (0.750),
        .CLKIN1_PERIOD        (100.0)
    )
    MMCME2_BASE_inst(
        .CLKOUT0      (clkout0),
        .CLKOUT0B     (clkout0b),
        .CLKOUT1      (clkout1),
        .CLKOUT1B     (clkout1b),
        .CLKOUT2      (clkout2),
        .CLKOUT2B     (clkout2b),
        .CLKOUT3      (clkout3),
        .CLKOUT3B     (clkout3b),
        .CLKOUT4      (clkout4),
        .CLKOUT5      (clkout5),
        .CLKOUT6      (clkout6),
        .CLKFBOUT     (clkfbout),
        .CLKFBOUTB    (clkboutb),
        .LOCKED       (locked),
        .CLKIN1       (clkin1),
        .PWRDWN       (pwrdwn),
        .RST          (rst),
        .CLKFBIN      (clkfbin)
    );
    
    //Here could be your code for wires and output buffers

endmodule
