`timescale 1ps/1ps
module clk
	(
		input	clkin1,
		input	pwrdwn,
		input	rst,
		input	clkfbin,
		output	clkout0,
		output	clkout1,
		output	clkout2,
		output	clkout3,
		output	clkout4,
		output	clkout5,
		output	clkfbout,
		output	locked
	);

	//Here could be your code for wires and input buffers

	PLLE2_BASE #(
		.CLKFBOUT_MULT(63),
		.CLKIN1_PERIOD(52.631),
		.DIVCLK_DIVIDE(1),
		.CLKOUT0_DIVIDE(2),
		.CLKOUT1_DIVIDE(4)
	)
	PLLE2_BASE_inst(
		.CLKOUT0	(clkout0),
		.CLKOUT1	(clkout1),
		.CLKOUT2	(clkout2),
		.CLKOUT3	(clkout3),
		.CLKOUT4	(clkout4),
		.CLKOUT5	(clkout5),
		.CLKFBOUT	(clkfbout),
		.LOCKED	(locked),
		.CLKIN1	(clkin1),
		.PWRDWN	(pwrdwn),
		.RST	(rst),
		.CLKFBIN	(clkfbin)
	);

	//Here could be your code for wires and output buffers

endmodule