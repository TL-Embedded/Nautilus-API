# Common commands

## Identity

Format:
* `*IDN?`

Returns a standard SCPI identification string: Manufacturer, Device, Serial, Version.

Example:
```
*IDN?
TL Embedded, Nautilus, 001C00484331500120373358, v1.0
```

## Reset

Format
* `*RST`

Issues a reset, resetting all non-volatile parameters. This will reset the state of all IO. It is reccommended to issue a reset when starting communications with a Nautilus in an unknown state.

Example:
```
*RST
```

# Input Channels

## Input Voltage

Format
* `INPut#:VOLTage?`

Measures the voltage at an input.

| Parameter     | Type | Range     | Description |
| ------------- | ---- | --------- | ----------- |
| Channel       | #    | 1 - 12    | Selects the input channel |

Example:
```
INP1:VOLT?
5.023
```

## Input Frequency

Format:
* `INPut:FREQuency <u>Hz`
* `INPut:FREQuency?`

Set the sampling frequency for the input measurement. This affects all input channels.

| Parameter     | Type   | Range     | Description |
| ------------- | ------ | --------- | ----------- |
| Frequency     | u (Hz) | 2.5Hz - 4KHz | The target frequency |

Only the following discrete frequencies are supported:
 * 2.5Hz
 * 5Hz
 * 10Hz
 * 16.666Hz
 * 20Hz
 * 50Hz
 * 60Hz
 * 100Hz
 * 200Hz
 * 400Hz
 * 800Hz
 * 1kHz
 * 2kHz
 * 4kHz

Example:
```
INP:FREQ 100Hz
INP:FREQ?
100.000
```


# Output Channels

## Output Set

Format:
 * `OUTput#:SET <b>, <u>V`

Sets all output parameters of an output channel. This is equivilent to calling the ENAble and VOLTage commands separately.

| Parameter     | Type | Range     | Description |
| ------------- | ---- | --------- | ----------- |
| Channel       | #    | 1 - 12    | Selects the output channel |
| Enable        | b    |           | Enables the channel output |
| Voltage       | u (V)| 0V - 30V  | Target output voltage |

Example
```
OUT1:SET ON, 5.0V
```

## Output Enable


Format:
 * `OUTput#:ENAble <b>`
 * `OUTput#:ENAble?`

Sets or queries the selected chanels output state.

| Parameter     | Type | Range     | Description |
| ------------- | ---- | --------- | ----------- |
| Channel       | #    | 1 - 12    | Selects the output channel |
| Enable        | b    |           | Enables the channel output |

Example:
```
OUT1:ENA ON
OUT1:ENA?
ON
```

## Output Voltage

Format:
 * `OUTput#:VOLTage <u>V`
 * `OUTput#:VOLTage?`

Sets or queries the target output voltage for the specified channel.

| Parameter     | Type      | Range     | Description |
| ------------- | --------- | --------- | ----------- |
| Channel       | #         | 1 - 12    | Selects the output channel |
| Voltage       | u (V)     | 0V - 30V  | Target output voltage |

Example:
```
OUT1:VOLT 5.0V
OUT1:VOLT?
5.000
```

# Power Supplies

## Power Set

Format:
 * `POWer#:SET <b>, <u>V, <u>A`

Sets all output parameters of a power supply. This is equivilent to calling the ENAble, VOLTage, and CURRent commands separately.

| Parameter     | Type | Range     | Description |
| ------------- | ---- | --------- | ----------- |
| Supply        | #    | 1 - 2     | Selects the supply |
| Enable        | b    |           | Enables the supply output |
| Voltage       | u (V)| 0V - 30V  | Target output voltage |
| Current       | u (A)| 0V - 3A   | Target current limit |

Example
```
POW1:SET ON, 5.0V, 3.0A
```

## Power Enable

Format:
 * `POWer#:ENAble <b>`
 * `POWer#:ENAble?`

Enables the selected power supply

| Parameter     | Type      | Range     | Description |
| ------------- | --------- | --------- | ----------- |
| Supply        | #         | 1 - 2     | Selects the output supply |
| Enable        | b         |           | Enables the supply output |

Example:
```
POW1:ENA ON
POW1:ENA?
ON
```

## Power Voltage

Format:
 * `POWer#:VOLTage <u>V`
 * `POWer#:VOLTage?`

Sets or queries the target output voltage for the specified supply.

| Parameter     | Type      | Range     | Description |
| ------------- | --------- | --------- | ----------- |
| Supply        | #         | 1 - 2     | Selects the output supply |
| Voltage       | u (V)     | 0V - 24V  | Target output voltage |

Example:
```
POW1:VOLT 5.0V
POW1:VOLT?
5.000
```

## Power Current

Format:
 * `POWer#:CURRent <u>A`
 * `POWer#:CURRent?`

Sets or queries the target output current for the specified supply.

| Parameter     | Type      | Range     | Description |
| ------------- | --------- | --------- | ----------- |
| Supply        | #         | 1 - 2     | Selects the output supply |
| Current       | u (A)     | 0V - 3A   | Target current limit |

Example:
```
POW1:CURR 1.0A
POW1:CURR?
1.000
```

## Power Measure Voltage

Format:
 * `POWer#:MEASure:VOLTage?`

Measures the output voltage on the specified supply

| Parameter     | Type      | Range     | Description |
| ------------- | --------- | --------- | ----------- |
| Supply        | #         | 1 - 2     | Selects the output supply |

Example:
```
POW1:MEAS:VOLTage?
4.910
```

## Power Measure Current

Format:
 * `POWer#:MEASure:CURRent?`

Measures the output current on the specified supply

| Parameter     | Type      | Range     | Description |
| ------------- | --------- | --------- | ----------- |
| Supply        | #         | 1 - 2     | Selects the output supply |

Example:
```
POW1:MEAS:CURRent?
0.050
```

# System

## Input Voltage

Format:
 * `VINput?`

Queries the system input voltage.

Example:
```
VIN?
11.982V
```

## System Temperature

Format:
 * `SYST:TEMPerature?`

Queries the system temperature

Example:
```
SYST:TEMP?
28
```

## System Reference Voltage

Format:
 * `SYST:VREFerence?`

Queries the system reference voltage

Example:
```
SYST:VREF?
3.001
```

## Network MAC Address

Format:
 * `SYST:NETwork:MAC?`

Queries the MAC address

Example:
```
SYST:NET:MAC?
44:B7:D0:EA:16:10
```

## Network IP Address

Format:
 * `SYST:NETwork:IPADdress?`

Queries the IP address

Example:
```
SYST:NET:IPAD?
192.168.1.123
```

## Network Host Name

Format:
 * `SYST:NETwork:NAME <s>`
 * `SYST:NETwork:NAME?`

Sets or queries the host name used for MDNS.

| Parameter     | Type      | Range     | Description |
| ------------- | --------- | --------- | ----------- |
| Name          | s         |           | Host name for MDSN resolution |

Example:
```
SYST:NET:NAME "nautilus"
SYST:NET:NAME?
nautilus
```

## Network Resolved Host Name

Format:
 * `SYST:NETwork:NAME:RESolved?`

Queries the host name after MDNS resolution.

Example:
```
SYST:NET:NAME:RES?
nautilus-2.local
```

## Beep

Format:
 * `SYST:BEEP <u>Hz, <u>s`

Runs the beeper

| Parameter     | Type      | Range     | Description |
| ------------- | --------- | --------- | ----------- |
| Frequency     | u (Hz)    | 500Hz - 6kHz | Tone of the beeper |
| Duration      | u (s)     | 1ms - 10s  | Duration of the beep |

Example:
```
SYST:BEEP 2kHz, 300ms
```

# Auxillary Serial

## Serial Enable

Format:
 * `AUXillary:SERial:ENAble <b>`
 * `AUXillary:SERial:ENAble?`

Enables or disables the serial port.

| Parameter     | Type | Range | Description            |
| ------------- | ---- | ----- | ---------------------- |
| Enable        | b    |       | Enables serial comms   |

Example:
```
AUX:SER:ENA ON
AUX:SER:ENA?
ON
```

## Serial Baudrate

Format:
 * `AUXillary:SERial:BAUDrate <i>`
 * `AUXillary:SERial:BAUDrate?`

Sets or queries the serial baudrate.

| Parameter | Type | Range | Description     |
| --------- | ---- | ----- | --------------- |
| Baudrate  | i    | 1200 - 1000000 | Baudrate in bps |

Example:
```
AUX:SER:BAUD 115200
AUX:SER:BAUD?
115200
```

## Serial Direction Pin

Format:
 * `AUXillary:SERial:DIR <s>`
 * `AUXillary:SERial:DIR?`

Sets or queries the serial direction.

| Parameter | Type | Range | Description         |
| --------- | ---- | ----- | ------------------- |
| Mode      | s    |       | Mode of direction pin |

The following modes are supported:
 * `TX`: DIR pin output high while transmitting
 * `NTX`: DIR pin output low while transmitting
 * `OFF`: DIR pin inactive

Example:
```
AUX:SER:DIR "NTX"
AUX:SER:DIR?
NTX
```

## Serial Read

Format:
 * `AUXillary:SERial:READ <i>`

Reads a number of bytes from the serial port buffer.

| Parameter | Type | Range | Description              |
| --------- | ---- | ----- | ------------------------ |
| Length    | i    | 0-256 | Number of bytes to read  |

Example:
```
AUX:SER:READ 4
48656C6C6F20776F726C643F0A0D
```

## Serial Write

Format:
 * `AUXillary:SERial:WRITE <x>`

Writes bytes to the serial port

| Parameter | Type | Range | Description      |
| --------- | ---- | ----- | ---------------- |
| Data      | x    |       | Bytes to write to the port |

Example:
```
AUX:SER:WRITE 48656C6C6F20776F726C64410A0D
```

## I2C Enable

Format:
 * `AUXillary:IIC:ENAble <b>`
 * `AUXillary:IIC:ENAble?`

Enables or disables I2C.

Example:
```
AUX:IIC:ENA ON
AUX:IIC:ENA?
ON
```

## I2C Speed

Format:
 * `AUXillary:IIC:SPEED <i>`
 * `AUXillary:IIC:SPEED?`

Sets or queries the I2C bus speed.

Example:
```
AUX:IIC:SPEED 400000
AUX:IIC:SPEED?
400000
```

## I2C Read

Format:
 * `AUXillary:IIC:READ <i>, <i>`

Reads bytes from an I2C device.

| Parameter | Type | Range   | Description         |
| --------- | ---- | ------- | ------------------- |
| Address   | i    | 0 - 127 | Device address      |
| Length    | i    | 0 - 256 | Number of bytes     |

Example:
```
AUX:IIC:READ 80, 4
01020304
```

## I2C Write

Format:
 * `AUXillary:IIC:WRITE <i>, <x>`

Writes bytes to an I2C device. Replies with a boolean to indicate ACK status.

| Parameter | Type | Range   | Description            |
| --------- | ---- | ------- | ---------------------- |
| Address   | i    | 0 - 127 | Device address         |
| Data      | x    |         | Bytes to write         |

Example:
```
AUX:IIC:WRITE 80, 01020304
ON
```


## I2C Transfer

Format:
 * `AUXillary:IIC:TRANsfer <i>, <x>, <i>`

Performs a write followed by a read on an I2C device.

| Parameter | Type | Range   | Description                 |
| --------- | ---- | ------- | --------------------------- |
| Address   | i    | 0 - 127 | Device address              |
| TX Data   | x    |         | Written bytes               |
| RX Length | i    | 0 - 256 | Number of bytes to read     |

Example:
```
AUX:IIC:TRAN 80, A0, 2
0102
```

## I2C Scan

Format:
 * `AUXillary:IIC:SCAN <i>`

Checks for the existing of a device

| Parameter | Type | Range   | Description       |
| --------- | ---- | ------- | ----------------- |
| Address   | i    | 0 - 127 | Device address    |

Example:
```
AUX:IIC:SCAN 80
ON
```

## SPI Enable

Format:
 * `AUXillary:SPI:ENAble <b>`
 * `AUXillary:SPI:ENAble?`

Enables or disables SPI.

Example:
```
AUX:SPI:ENA ON
AUX:SPI:ENA?
ON
```

## SPI Speed

Format:
 * `AUXillary:SPI:SPEED <i>`
 * `AUXillary:SPI:SPEED?`

Sets or queries the SPI bus speed.
The speed may be truncated to a valid SPI bus speed when the SPI is enabled.

Example:
```
AUX:IIC:SPEED 8000000
AUX:IIC:SPEED?
8000000
```

## SPI Mode

Format:
 * `AUXillary:SPI:MODE <i>`
 * `AUXillary:SPI:MODE?`

Sets or queries the SPI bus mode.

Example:
```
AUX:IIC:MODE 0
AUX:IIC:MODE?
0
```

## SPI Read

Format:
 * `AUXillary:SPI:READ <i>`

Reads bytes from the SPI bus.

| Parameter | Type | Range   | Description         |
| --------- | ---- | ------- | ------------------- |
| Length    | i    | 0 - 256 | Number of bytes     |

Example:
```
AUX:SPI:READ 4
01020304
```

## SPI Write

Format:
 * `AUXillary:SPI:WRITE <x>`

Writes bytes to the SPI bus

| Parameter | Type | Range   | Description            |
| --------- | ---- | ------- | ---------------------- |
| Data      | x    |         | Bytes to write         |

Example:
```
AUX:SPI:WRITE 01020304
```


## SPI Transfer

Format:
 * `AUXillary:SPI:TRANsfer <x>`

Performs a read/write on the SPI bus

| Parameter | Type | Range   | Description                 |
| --------- | ---- | ------- | --------------------------- |
| TX Data   | x    |         | Written bytes               |

Example:
```
AUX:SPI:TRAN 0102
0304
```

## GPIO Set

Format:
 * `AUXillary:GPIO#:SET <b>`
 * `AUXillary:GPIO#:SET?`

Sets the output state of a GPIO pin.

| Parameter | Type | Range | Description             |
| --------- | ---- | ----- | ----------------------- |
| Pin       | #    | 1 - 8 | Pin number              |
| State     | b    |       | Output state            |

Example:
```
AUX:GPIO1:SET ON
AUX:GPIO1:SET?
ON
```

## GPIO Read

Format:
 * `AUXillary:GPIO#:READ?`

Reads the input state of a GPIO pin.

| Parameter | Type | Range | Description             |
| --------- | ---- | ----- | ----------------------- |
| Pin       | #    | 1 - 8 | Pin number              |

Example:
```
AUX:GPIO1:READ?
```

## Servo Set

Format:
 * `AUXillary:GPIO#:SERVo:SET <b>, <u>s`

Sets a GPIO as a servo output. This is equivalent to calling ENAble and PULSe separately.

| Parameter | Type | Range | Description             |
| --------- | ---- | ----- | ----------------------- |
| Pin       | #    | 1 - 8 | Pin number              |
| Enable    | b    |       | Enables the servo output |
| Pulse     | u (s)| 500us - 2500us | Pulse width    |

Example:
```
AUX:GPIO1:SERV:SET ON, 1500us
```

## Servo Enable

Format:
 * `AUXillary:GPIO#:SERVo:ENAble <b>`
 * `AUXillary:GPIO#:SERVo:ENAble?`

Enables or disables the servo output.

| Parameter | Type | Range | Description             |
| --------- | ---- | ----- | ----------------------- |
| Pin       | #    | 1 - 8 | Pin number              |
| Enable    | b    |       | Enables the servo output |

Example:
```
AUX:GPIO1:SERV:ENA ON
AUX:GPIO1:SERV:ENA?
ON
```

## Servo Pulse

Format:
 * `AUXillary:GPIO#:SERVo:PULSe <u>s`
 * `AUXillary:GPIO#:SERVo:PULSe?`

Sets or queries the pulse width of the servo output.

| Parameter | Type | Range | Description             |
| --------- | ---- | ----- | ----------------------- |
| Pin       | #    | 1 - 8 | Pin number              |
| Pulse     | u (s)| 500us - 2500us | Pulse width    |

Example:
```
AUX:GPIO1:SERV:PULS 1500us
AUX:GPIO1:SERV:PULS?
0.001500
```




