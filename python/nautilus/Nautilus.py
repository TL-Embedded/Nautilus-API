from . import SCPI
import time


class Nautilus():
    def __init__(self, uri: str = "tcp://nautilus.local"):
        self.scpi = SCPI.from_uri(uri)
        self.version = 0.0
        self.input_freq: float|None = None

    def __enter__(self):
        self.open()
        return self
    
    def __exit__(self, *args):
        self.close()

    def get_version(self) -> str:
        idn = self.scpi.get_idn()
        # TL Embedded, Nautilus, 001C00484331500120373358, v0.1
        if idn.startswith("TL Embedded, Nautilus,"):
            return float(idn.split(", ")[-1][1:])
        raise Exception("Nautilus not found")

    def open(self):
        self.version = self.get_version()

    def close(self, reset: bool = True):
        if reset:
            self.reset()
        self.scpi.close()

    def reset(self):
        self.scpi.write("*RST")

    # ADC input commands

    def set_input_frequency(self, frequency: float):
        if self.version >= 1.0:
            self.scpi.write(f"INP:FREQ {frequency:.3f}Hz")
        self.input_freq = frequency

    def get_input_voltage(self, channel: int, frequency: float|None = None) -> float:
        if frequency is not None and self.input_freq != frequency:
            self.set_input_frequency(frequency)
        return float(self.scpi.query(f"INP{channel}:VOLT?"))
    
    # DAC output commands

    def set_output_voltage(self, channel: int, volts: float ):
        self.scpi.write( f"OUT{channel}:VOLT {volts:.3f}V" )

    def set_output_enable(self, channel: int, enable: bool):
        self.scpi.write( f"OUT{channel}:ENA {'ON' if enable else 'OFF'}" )

    def set_output(self, channel: int, enable: bool, volts: float = 0.0):
        self.scpi.write( f"OUT{channel}:SET {'ON' if enable else 'OFF'}, {volts:.3f}V" )

    # PSU output commands

    def set_psu_voltage(self, channel: int, volts: float):
        self.scpi.write(f"POW{channel}:VOLT {volts:.3f}V")
        
    def set_psu_current(self, channel: int, amps: float):
        self.scpi.write(f"POW{channel}:CURR {amps:.3f}A")
    
    def set_psu_enable(self, channel: int, enable: bool):
        self.scpi.write(f"POW{channel}:ENA {'ON' if enable else 'OFF'}")
    
    def set_psu(self, channel: int, enable: bool, volts: float, amps: float):
        if self.version >= 1.0:
            self.scpi.write(f"POW{channel}:SET {'ON' if enable else 'OFF'}, {volts:.3f}V, {amps:.3f}A")
        else:
            self.set_psu_voltage(channel, volts)
            self.set_psu_current(channel, amps)
            self.set_psu_enable(channel, enable)
        

    def get_psu_voltage(self, channel: int) -> float:
        return float(self.scpi.query(f"POW{channel}:MEAS:VOLT?"))
    
    def get_psu_current(self, channel: int) -> float:
        return float(self.scpi.query(f"POW{channel}:MEAS:CURR?"))

    # System commands

    def get_vin(self) -> float:
        return float(self.scpi.query("VIN?"))
    
    def get_temperature(self) -> float:
        return float(self.scpi.query("SYST:TEMP?"))
    
    def get_reference_voltage(self) -> float:
        return float(self.scpi.query("SYST:VREF?"))
    
    def beep(self, freq_hz: int = 2000, duration_s: float = 0.1):
        self.scpi.write(f"SYST:BEEP {freq_hz}Hz, {duration_s}s")
    
    # Networking commands
    
    def get_ip(self) -> str:
        return self.scpi.query("SYST:NET:IPAD?")
    
    def get_mac(self) -> str:
        return self.scpi.query("SYST:NET:MAC?")
    
    def get_hostname(self) -> str:
        return self.scpi.query("SYST:NET:NAME?")
    
    def set_hostname(self, name: str):
        self.scpi.write(f"SYST:NET:NAME \"{name}\"")

    def get_address(self) -> str | None:
        address = self.scpi.query("SYST:NET:NAME:RES?")
        return address if address else None

    # Aux serial commands

    def open_serial(self, baud: int = 9600):
        self.scpi.write(f"AUX:SER:BAUD {int(baud)}")
        self.scpi.write("AUX:SER:ENA ON")
        self._serial_buffer = bytearray()

    def close_serial(self):
        self.scpi.write("AUX:SER:ENA OFF")

    def _read_serial(self, count: int = 256) -> bytes:
        result = self.scpi.query(f"AUX:SER:READ {count}")
        return bytes.fromhex(result)
    
    def get_serial_remaining(self) -> int:
        return int(self.scpi.query(f"AUX:SER:READ?"))

    def write_serial(self, payload: bytes):
        self.scpi.write(f"AUX:SER:WRITE {payload.hex()}")

    def set_dir_pin(self, enable: bool, active_high: bool = False):
        if not enable:
            mode = "OFF"
        else:
            mode = "TX" if active_high else "NTX"
        self.scpi.write(f"AUX:SER:DIR {mode}")

    def read_serial_line(self, delimiter: bytes = b"\n", timeout: float = 0.0) -> None | bytes:
        start = time.time()
        while True:
            self._serial_buffer.extend(self._read_serial())
            index = self._serial_buffer.find(delimiter)
            if index >= 0:
                line = bytes(self._serial_buffer[:index])
                self._serial_buffer = self._serial_buffer[index + len(delimiter):]
                return line
            if time.time() - start > timeout:
                return None
            time.sleep(0.05)

    def read_serial_bytes(self, count: int, timeout: float = 0.0) -> bytes:
        start = time.time()
        while True:
            self._serial_buffer.extend(self._read_serial())
            if len(self._serial_buffer) >= count:
                line = bytes(self._serial_buffer[:count])
                self._serial_buffer = self._serial_buffer[count:]
                return line
            if time.time() - start > timeout:
                line = bytes(self._serial_buffer)
                self._serial_buffer = bytearray()
                return line
            time.sleep(0.05)

    # Aux I2C commands

    def open_i2c(self, speed: int = 100000):
        self.scpi.write(f"AUX:IIC:SPEED {int(speed)}")
        self.scpi.write(f"AUX:IIC:ENA ON")

    def close_i2C(self):
        self.scpi.write("AUX:IIC:ENA OFF")

    def read_i2c(self, address: int, to_read: int) -> bytes:
        result = self.scpi.query(f"AUX:IIC:READ {address}, {to_read}")
        return bytes.fromhex(result)
    
    def write_i2c(self, address: int, payload: bytes) -> bool:
        result = self.scpi.query(f"AUX:IIC:WRITE {address}, {payload.hex()}")
        return result == "ON"
    
    def transfer_i2c(self, address: int, payload: bytes, to_read: int) -> bytes:
        result = self.scpi.query(f"AUX:IIC:TRAN {address}, {payload.hex()}, {to_read}")
        return bytes.fromhex(result)
    
    def scan_i2c(self, address: int) -> bool:
        result = self.scpi.query(f"AUX:IIC:SCAN {address}")
        return result == "ON"

    def scan_all_i2c(self) -> list[int]:
        return [ addr for addr in range(0x80) if self.scan_i2c(addr)]
    
    def read_eeprom(self, count: int = 16, address: int = 0x50, offset: int = 0) -> bytes:
        return self.transfer_i2c(address, bytes([offset]), count )
    
    # Default settings support the 24AA01 EEPROMs
    def write_eeprom(self, payload: bytes, address: int = 0x50, offset: int = 0, pagesize: int = 8) -> bool:
        index = 0
        end = offset + len(payload)
        while offset < end:

            page_end = (offset & ~(pagesize-1)) + pagesize
            chunk = min( page_end, end ) - offset

            # Write chunk
            if not self.write_i2c(address, bytes([offset]) + payload[index:index+chunk] ):
                return False
            
            offset += chunk
            index += chunk
            
            # Device acks once page write is complete.
            for _ in range(10):
                if self.scan_i2c(address):
                    break
                time.sleep(0.05)
            
        return True
    
    # Aux GPIO commands

    def set_gpio(self, pin: int, state: bool):
        self.scpi.write(f"AUX:GPIO{pin}:SET {'ON' if state else 'OFF'}")

    def read_gpio(self, pin: int):
        return self.scpi.query(f"AUX:GPIO{pin}:READ?") == 'ON'

    # Aux Servo commands

    def set_servo(self, pin: int, period_us: int = 1500):
        self.scpi.write(f"AUX:GPIO{pin}:SERV:SET ON, {period_us}us")

    def set_servo_enable(self, pin: int, enable: bool):
        self.scpi.write(f"AUX:GPIO{pin}:SERV:ENA {'ON' if enable else 'OFF'}")

    def set_servo_pulse(self, pin: int, period_us: int):
        self.scpi.write(f"AUX:GPIO{pin}:SERV:PULS {period_us}us")

    def set_servo_angle(self, pin: int, angle_deg: float):
        period_us = ((angle_deg / 180.0) * 1000) + 1000
        self.set_servo_pulse(pin, period_us)

    # Calibration commands
    # These should only be used with the appropriate jig...
    
    def calibrate_output(self, channel: int, setpoint_a: float = 1.0, setpoint_b: float = 11.0):
        self.set_output_enable(channel, True)
        self.scpi.write( f"OUT{channel}:VOLT:UNCAL {setpoint_a:.3f}V" )
        time.sleep(0.5)
        result_a = self.get_input_voltage(channel)
        self.scpi.write( f"OUT{channel}:VOLT:UNCAL {setpoint_b:.3f}V" )
        time.sleep(0.5)
        result_b = self.get_input_voltage(channel)
        self.set_output_enable(channel, False)
        self.scpi.write( f"OUT{channel}:VOLT:CAL {setpoint_a:.3f}V, {result_a:.3f}V, {setpoint_b:.3f}V, {result_b:.3f}V" )

    @staticmethod
    def find_usb_devices() -> list[str]:
        results = []
        from serial.tools.list_ports import comports
        for port in comports():
            if port.vid == 0x16D0 and port.pid == 0x13FD:
                results.append(f"tty://{port.device}")
        return results
