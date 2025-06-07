# Nautilus-API
This is the API for the TL Embedded Nautilus test fixture. This includes bindings for NodeJS and Python3.

# Python

Currently not deployed as a package. Just copy the `/python/nautilus` into your project and import it as a package.
If using the nautilus over serial, you will need to install `pyserial`.

# Node

Available as a node module:
`npm install @tl-embedded/nautilus`


# Pinout

The pinout of the 50 pin IDC connector is below:

| Signal      | Pin | Pin | Signal      |
| ----------- | --- | --- | ----------- |
| VIN         | 1   | 2   | GND         |
| VIN         | 3   | 4   | GND         |
| VIN         | 5   | 6   | GND         |
| PSU1        | 7   | 8   | GND         |
| PSU1        | 9   | 10  | GND         |
| PSU2        | 11  | 12  | GND         |
| PSU2        | 13  | 14  | GND         |
| OUT1        | 15  | 16  | IN1         |
| OUT2        | 17  | 18  | IN2         |
| OUT3        | 19  | 20  | IN3         |
| OUT4        | 21  | 22  | IN4         |
| OUT5        | 23  | 24  | IN5         |
| OUT6        | 25  | 26  | IN6         |
| OUT7        | 27  | 28  | IN7         |
| OUT8        | 29  | 30  | IN8         |
| OUT9        | 31  | 32  | IN9         |
| OUT10       | 33  | 34  | IN10        |
| OUT11       | 35  | 36  | IN11        |
| OUT12       | 37  | 38  | IN12        |
| 5V          | 39  | 40  | GND         |
| VDDIO       | 41  | 42  | GND         |
| SHIFT.CLK   | 43  | 44  | SHIFT.DAT   |
| SHIFT.LATCH | 45  | 46  | SER.DIR     |
| SER.TX      | 48  | 48  | SER.RX      |
| I2C.SCL     | 49  | 50  | I2C.SDA     |


A functional description of each signal is below:

| Signal      | Direction | Max voltage | Max current | Description |
| ----------- | --------- | ----------- | ----------- | ----------- |
| VIN         | IO        | 30V         | 9A          | May be used either a power input, or unprotected power output. It is internally connected to the power connector `J1` |
| PSU[1..2]   | O         | VSYS        | 3A          | 0.8V-24V, 0-3A, programmable power supply. Voltage and current are monitored. |
| OUT[1..12]  | O         | VSYS        | 20mA        | 0-30V 12bit DAC output. Output voltage may degrade when current exceeds 10mA. |
| IN[1..12]   | I         | 32V         | 250uA       | 0-30V 24bit ADC input. 130k input impedance. |
| 5V          | O         | 5.5V        | 2A          | 5V output to power downstream devices. |
| VDDIO       | I         | 5.5V        | 20mA        | Reference voltage for the auxilary IO. May be connected to 5V output. |
| SHIFT.CLK   | IO        | VDDIO       | 5mA         | Aux GPIO. May operate as shift register clock, or SPI clock. |
| SHIFT.DAT   | IO        | VDDIO       | 5mA         | Aux GPIO. May operate as shift register data, or SPI MOSI. |
| SHIFT.LATCH | IO        | VDDIO       | 5mA         | Aux GPIO. May operate as shift register latch, or SPI MISO. |
| SER.DIR     | IO        | VDDIO       | 5mA         | Aux GPIO. May operate as serial direction output (active high or low). |
| SER.TX      | IO        | VDDIO       | 5mA         | Aux GPIO. May operate as serial TX or CAN TX. |
| SER.RX      | IO        | VDDIO       | 5mA         | Aux GPIO. May operate as serial RX or CAN RX. |
| I2C.SCL     | IO        | VDDIO       | 5mA         | Aux GPIO. May operate as I2C SCL. |
| I2C.SDA     | IO        | VDDIO       | 5mA         | Aux GPIO. May operate as I2C SDA. |

## VSYS

VSYS is the internal system voltage. This can be sourced from any of the following:
 * VIN (either from J1 or IDC)
 * Ethernet POE
 * USB

This defines the maximum voltage available from the power supplies and DACS. It must be capable of providing enough power to run all outputs, plus 2W of for the rest of the Nautilus.

Performance of the DACs and ADCs may be degraded if VSYS falls below 5.5V.

## Notes on AUX GPIO
All auxillary GPIO may act as a digital input or output. They may also operate as a standard servo PWM output.

Pullup or pulldown resistors are not reccommended, as these intefere with the logic translators direction detection. The I2C will operate with no external pullups.

