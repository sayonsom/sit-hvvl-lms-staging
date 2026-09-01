**Introduction** 

High Voltage DC is used in several applications in industries, equipment, and research. HV DC is also employed to transmit bulk power. That apart, HVDC is used in the testing of High Voltage Cables and as a source for charging the Impulse Voltage and Current Generator. 

The most common way of generating High Voltage DC is through rectification using a) Half wave b) Full wave c) Multiplier Circuits. In all these cases, the AC input is taken from a High Voltage transformer. 

**Theory**

The Cockcroft-Walton Voltage Multiplier is a voltage multiplier circuit that was developed in 1934 by John Douglas Cockcroft and Ernest Thomas Sinton Walton. It was used in the Cockcroft-Walton accelerator, which was the first particle accelerator that was able to impart energies in the MeV range to particles. The circuit consists of a voltage multiplier ladder network of capacitors and diodes to generate high voltages. The circuit is also known by other names such as the multiplier ladder, voltage ladder, or ladder network.

The circuit is based on a charge pump circuit derived from a half-wave rectifier circuit. The half-wave rectifier circuit is made up of a capacitor, diode, and a resistor. The capacitor is charged during the positive half cycle of the input AC voltage and discharged through the resistor during the negative half cycle. The voltage across the capacitor is the peak voltage of the input AC voltage. The voltage multiplier circuit is made up of a series of half-wave rectifier circuits connected in series. The output voltage of each stage is the peak voltage of the input AC voltage. The total output voltage of the circuit is the sum of the output voltages of each stage.

An important aspect to consider in the Cockcroft-Walton Voltage Multiplier is the ripple in the output voltage, which is affected by various parameters such as load current, frequency, and capacitance. The ripple voltage ($ V_{ripple} $) for an ($ n $)-stage Cockcroft-Walton circuit can be calculated using the following formula:

$$
V_{ripple} = \frac{I \cdot n \cdot (n + 1)}{2 f C}
$$

Where:
- ($ I $) is the load current,
- ($ n $) is the number of stages,
- ($ f $) is the frequency of the input AC,
- ($ C $) is the capacitance.


This formula shows that the ripple voltage is directly proportional to the load current and the number of stages, and inversely proportional to the product of the frequency and capacitance. Understanding and controlling this ripple is crucial in high-voltage DC applications.

**Objective** 

- Understand the functioning of High Voltage DC Multiplier.
- Study the variation of ripple by varying each of the following parameters:
  1. Load Current,
  2. Frequency, and
  3. Capacitance.

**Procedure** 

1. The input parameters are Current (in µA), Frequency (in Hz), and Capacitance (in µF), and these are associated with corresponding text boxes that are displayed.
2. The input values of each of these variables to be entered should be within the range specified.
3. Upon entering the values of all the variables, click on the "Start Experiment" button to display the computed ripple values via a graph. This calculation of ripple is for a set of values of Current (in µA), Frequency (in Hz), and Capacitance (in µF). In addition, the variation of one of the above parameters on the ripple voltage can also be studied.
4. The graph will show two ripple plots (except for the first time you run the experiment). One for the present set of parameters, and a second for the previous set of parameters. The user can compare the two plots to understand the effect of varying the parameters.
5. The parameters that must be varied are shown to the user on the right pane. The user must choose only one of the parameters to vary at a time while keeping others constant.
6. These steps can be repeated for other parameters.

**References** 

- High Voltage Engineering by M.S. Naidu, V. Kamaraju, McGraw-Hill Professional Publishing, 2001. 
- High Voltage Engineering by C.L. Wadhwa 
- High Voltage Engineering (Third Edition), New Age International Publishers, 2010.








