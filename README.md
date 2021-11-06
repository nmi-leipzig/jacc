
# JACC

## Introduction

JACC is an open source clocking configurator generator for 7 series fpgas.

Only "base" features are currently supported, see Xilinx' [MMCME2_BASE](https://www.xilinx.com/support/documentation/sw_manuals/xilinx14_7/7series_hdl.pdf#1225157649) and [PLLE2_BASE](https://www.xilinx.com/support/documentation/sw_manuals/xilinx14_7/7series_hdl.pdf#1225168170) documentation

Spartan-7 models are currently not supported.
All supported FPGA models can be read by calling jacc with the -sm argument.


## Usage

Call jacc.py and specify arguments for your configuration.

### Examples

Getting a list of all existing arguments:
```
    python jacc.py -h
```  

Getting a list of all supported FPGA models:
```
    python jacc.py -sm
```  

Generate a configuration with input frequency 400 MHz and output frequencies of 600 MHz and 200 MHz by using the pll block:
```
    python jacc.py -cmtb -pll -fin1 400 -fout0 600 -fout1 200
```  

Generate a configuration for a specific fpga model. The block chosen here is the MMCM (which is the default):
```
    python jacc.py -model "kintex-7" "3" "1.0V" -fin1 100 -fout0 700
```  

## Extra Features

JACC has some extra features that are not known to be supported by Xilinx' Vivado Clocking Wizard.

### Divider Cascade

7-Series fpga mmcm blocks have an attribute called CLKOUT4_CASCADE.
This attribute can be used to use the product of the clock dividers 4 and 6 on the clock signal 4.

#### Example Usage

Consider the following configuration is targeted:

input frequency: 400 MHz
clock 0 frequency: 750 MHz
clock 1 frequency: 800 MHz
clock 2 frequency: 4.69 MHz

Clock 2s frequency is very low compared to clock 0 and 1.
This will lead to some unrequested deviation on clock 2.
The Divider Cascade feature can be used in this case in order to reduce the deviation on clock 4.
To do this the low frequency clock has to be put on clock 4 and the -clk4c argument has to be used.
Example call:
```
    python jacc.py -fin1 400 -fout0 750 -fout1 800 -fout4 4.69 -clk4c
```

### Max Delta Values

Some clock frequencies may be considered more important than others by the user.
A user can specify the amount of deviation he allows for a specific requested value.
This deviation amount is specified as a percentage (in decimal notation).
The default value is 0.5 (50%) and is used if the user specifies no other value.

#### Example Usage

Consider the following configuration with is targeted:

input frequency: 400 MHz
clock 0 frequency: 113 MHz  with an allowed deviation of 2%
clock 1 frequency: 457 MHz  with an allowed deviation of 5%
clock 2 frequency: 15 MHz  with an allowed deviation of 80%

The following example would lead to a desired configuration:
```
    python jacc.py -fin1 100 -fout0 113 -fout1 457 -fout2 800 -fdelta0 0.02 -fdelta1 0.05 -fdelta2 0.8
```
Not specifying user dependant deltas would lead to a different result with more error on clock 0 and 1.

###### Note:
JACC will always choose the "best" configuration of a list of considered configuration.
This means that specifying 100% allowed deviation for all clocks leads in most cases to the same result as specifying 90% allowed deviations for all clocks.
The fitness of a configuration is chosen according to a scoring system.
There are two scoring methods based on relative or absolute deviations.
The absolute error deviations are used by default.
Use the -re argument to consider relative errors instead of absolute errors:
```
    python jacc.py -fin1 100 -fout0 113 -fout1 457 -re
```
