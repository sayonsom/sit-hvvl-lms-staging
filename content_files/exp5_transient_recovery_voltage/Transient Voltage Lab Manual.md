# Introduction

The voltage that appears across the terminals of the high voltage circuit breaker is known as the transient recovery voltage (TRV). The TRV is dependent on the characteristics of the system connected on both terminals of the circuit breaker, and on the type of fault that this circuit breaker must interrupt (single, double, or three-phase faults, grounded or ungrounded fault). It is important to analyse the TRV of a system to properly size the ratings of the circuit breaker to cater for the expected TRV during a fault.

# Theory

IEEE C37.011 defines Transient Recovery Voltage (TRV) as the voltage that appears across the terminals of a circuit breaker after a current interruption. It is a result of the voltage difference response of the circuits on the source side and load side of the circuit breaker. This difference creates the TRV across the breaker terminals.

![Transient Recovery Voltage](https://res.cloudinary.com/dti7egpsg/image/upload/v1709037312/SIT%20Align/SIT/HVL/Exp5_TransientVoltage/Screenshot_2024-02-27_at_5.32.10_AM_opeye1.png)

This voltage across the breaker terminals upon current interruption may be considered in two successive stages. The transient recovery voltage stage where high frequency oscillations are observed, followed by the recovery voltage stage where power frequency oscillations are observed (transient has decayed).

![Recovery Voltage Stages](https://res.cloudinary.com/dti7egpsg/image/upload/v1709037312/SIT%20Align/SIT/HVL/Exp5_TransientVoltage/Screenshot_2024-02-27_at_5.32.10_AM_opeye1.png)

## Factors affecting TRV

Transient recovery voltage is affected by various parameters of the system. Some widely and popularly known parameters are:
- the system’s inductance and capacitance.
- the fault current level of the system at the point of the study of TRV.
- The voltage transformers, the bushing capacitance of circuit breakers etc.
- A number of transmission lines terminating at a bus and their characteristics impedance. 
- The internal factors of the circuit breaker (example: first pole to clear a fault etc.)
- The grounding for the system.

## Importance of TRV analysis

The objective of a TRV study is to verify that the TRV experienced by the breaker during current interruption is within the capability of the breaker, under credible scenarios. The longitudinal voltage withstand of the gap between the poles of the circuit breaker are challenged where TRV appears across the circuit breaker while it is opening. A longitudinal breakdown will occur if the system TRV reaches the gap withstand voltage. This is known as a re-ignition if the breakdown occurs before a quarter cycle following the current interruption, and a restrike if it occurs after.
Restrikes can be avoided by design and re-ignition can be minimized. Restrikes and re-ignition can create hot-spots in the circuit breaker and high-frequency transients in the circuit. The

worst cases would be the circuit breaker is not able to interrupt the current, or if the successive breakdowns create a voltage escalation.
The following can be done for an TRV analysis:
1.	System modelling: Frequencies ranging from the fundamental to few kilohertz of the system must be modelled. Frequency-dependent modelling is required for most of the part, especially for conductors.
2.	Simulation of worst-case scenarios: depending on the system, some clearing scenarios will be more challenging for the circuit breaker. For example, 3-phase ungrounded faults are very often the most challenging events to clear, especially if they occur at the secondary of a series- reactor or a transformer. For lines, short-line-faults (single-phase to ground) and 3-phase terminal faults are the worst cases. The outcomes of the worst-case scenario simulations are the prospective TRVs.
3.	Comparison of the prospective TRVs (by simulation) with the breaker inherent TRV (by standardized lab tests): the prospective TRV is superimposed with the breaker inherent TRV envelop which is built with 2 or 4 parameters and depends on the:
- breaker class
- rated voltage
- short-circuit current
- type of fault cleared during the studied event
- short-circuit current cleared during the studied event

![TRV waveshapes](https://res.cloudinary.com/dti7egpsg/image/upload/v1709037312/SIT%20Align/SIT/HVL/Exp5_TransientVoltage/Screenshot_2024-02-27_at_5.32.40_AM_wgp1ga.png)

Both the TRV magnitude and its initial slope (known as the Rate of Rise of Recovery Voltage or RRRV) must be inside the inherent TRV envelop, considering a safety margin.
TRV studies are typically performed for the following cases:

1. Breakers disconnecting transmission lines: In this case, two cases are simulated:
    - A short-line single-phase-to-ground fault, which produces the more severe RRRV
    - A terminal 3-phase ungrounded fault, which produces the highest TRV
2. Breakers disconnecting reactors:
    - Transformer limited faults
    - Induction motor tripping during start-up
    - Synchronous generator tripping
    - Capacitor bank de-energization


## IEC and IEE standards 
International industries requirement on TRV are:
- IEEE C37.011-2011: IEEE Guide for the Application of Transient Recovery Voltage for AC High-Voltage Circuit Breaker
- IEEE C37.06-2009: IEEE Standard for AC High-Voltage Circuit Breakers Rated on a Symmetrical Current Basis - Preferred Ratings and Related Required Capabilities for Voltages Above 1000
- IEC 62271-100: High-Voltage switchgear and control gear – Part 100: Alternating-current circuit-breaker. Edition 2.0, 2008-04


## Selection of circuit breaker for TRV
The TRV ratings define a withstand boundary. A circuit TRV that exceeds this boundary is more than the circuit breaker’s rated or related capability.
When the withstand boundary is exceeded:
- either a different circuit breaker should be used,
- or the system should be modified in such a manner as to change its TRV characteristics.
