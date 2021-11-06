
# JACC

## Introduction

JACC is an open source clocking configurator generator for 7 series fpgas.<br/>

Only "base" features are currently supported, see Xilinx' [MMCME2_BASE](https://www.xilinx.com/support/documentation/sw_manuals/xilinx14_7/7series_hdl.pdf#1225157649) and [PLLE2_BASE](https://www.xilinx.com/support/documentation/sw_manuals/xilinx14_7/7series_hdl.pdf#1225168170) documentation.<br/>

Spartan-7 models are currently not supported.<br/>
All supported FPGA models can be read by calling jacc with the -sm argument.<br/>


## Usage

Call jacc.py and specify arguments for your configuration.<br/>

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

JACC has some extra features that are not known to be supported by Xilinx' Vivado Clocking Wizard.<br/>

### Divider Cascade

7-Series fpga mmcm blocks have an attribute called CLKOUT4_CASCADE.<br/>
This attribute can be used to use the product of the clock dividers 4 and 6 on the clock signal 4.<br/>

#### Example Usage

Consider the following configuration is targeted:<br/>
<br/>
input frequency: 400 MHz<br/>
clock 0 frequency: 750 MHz<br/>
clock 1 frequency: 800 MHz<br/>
clock 2 frequency: 4.69 MHz<br/>
<br/>
Clock 2s frequency is very low compared to clock 0 and 1.<br/>
This will lead to some unrequested deviation on clock 2.<br/>
The Divider Cascade feature can be used in this case in order to reduce the deviation on clock 4.<br/>
To do this the low frequency clock has to be put on clock 4 and the -clk4c argument has to be used.<br/>
Example call:
```
    python jacc.py -fin1 400 -fout0 750 -fout1 800 -fout4 4.69 -clk4c
```

### Max Delta Values

Some clock frequencies may be considered more important than others by the user.<br/>
A user can specify the amount of deviation he allows for a specific requested value.<br/>
This deviation amount is specified as a percentage (in decimal notation).<br/>
The default value is 0.5 (50%) and is used if the user specifies no other value.<br/>
<br/>
#### Example Usage

Consider the following configuration with is targeted:<br/>
<br/>
input frequency: 400 MHz<br/>
clock 0 frequency: 113 MHz  with an allowed deviation of 2%<br/>
clock 1 frequency: 457 MHz  with an allowed deviation of 5%<br/>
clock 2 frequency: 15 MHz  with an allowed deviation of 80%<br/>
<br/>
The following example would lead to a desired configuration:
```
    python jacc.py -fin1 100 -fout0 113 -fout1 457 -fout2 800 -fdelta0 0.02 -fdelta1 0.05 -fdelta2 0.8
```
Not specifying user dependant deltas would lead to a different result with more error on clock 0 and 1.<br/>

###### Note:
JACC will always choose the "best" configuration of a list of considered configuration.<br/>
This means that specifying 100% allowed deviation for all clocks leads in most cases to the same result as specifying 90% allowed deviations for all clocks.<br/>
The fitness of a configuration is chosen according to a scoring system.<br/>
There are two scoring methods based on relative or absolute deviations.<br/>
The absolute error deviations are used by default.<br/>
Use the -re argument to consider relative errors instead of absolute errors:
```
    python jacc.py -fin1 100 -fout0 113 -fout1 457 -re
```
