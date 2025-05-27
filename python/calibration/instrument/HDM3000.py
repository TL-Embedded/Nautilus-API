from . import SCPI

# Not implemented:
#   TEMPerature
#   VOLTage:DC:RATio

class HDM3000():
    def __init__(self, uri: str = "ip://phoenix.local"):
        self.scpi = SCPI.from_uri(uri)
        self._func = None
        self._conf = {}

    def is_present(self, throw_on_error: bool = False) -> bool:
        # Hantek, HDM3055, CN2106030000156, 2.0.0.2
        success = self.scpi.get_idn().startswith("Hantek, HDM30")
        if throw_on_error and not success:
            raise Exception("HDM3000 not found")
        return success

    def close(self):
        self.set_remote(False)
        self.scpi.close()

    def set_remote(self, is_remote: bool):
        mode = "REM" if is_remote else "LOC"
        self.scpi.write(f"SYST:{mode}")

    def get_voltage(self, range_volts: float = 10.0, aperture_plc: float = 1.0) -> float:
        self._set_conf("VOLT:DC:RANGE", range_volts)
        self._set_conf("VOLT:DC:NPLC", aperture_plc)
        self._set_func("VOLT:DC")
        return self._read()

    def get_ac_voltage(self, range_volts: float = 10.0, bandwidth_hz: float = 20.0) -> float:
        self._set_conf("VOLT:AC:RANGE", range_volts)
        self._set_conf("VOLT:AC:BAND", bandwidth_hz)
        self._set_conf("VOLT:AC:TERM", bandwidth_hz)
        self._set_func("VOLT:AC")
        return self._read()

    def get_current(self, range_amps: float = 1.0, aperture_plc: float = 1.0) -> float:
        self._set_curr_range("DC", range_amps)
        self._set_conf("CURR:DC:NPLC", aperture_plc)
        self._set_func("CURR:DC")
        return self._read()

    def get_ac_current(self, range_amps: float = 10.0, bandwidth_hz: float = 20.0) -> float:
        self._set_curr_range("AC", range_amps)
        self._set_conf("CURR:AC:BAND", bandwidth_hz)
        self._set_func("CURR:AC")
        return self._read()

    def get_diode_voltage(self) -> float:
        self._set_func("DIOD")
        return self._read()

    def get_resistance(self, range_ohms: float = 1e6, aperture_plc: float = 1.0, four_wire: bool = False) -> float:
        self._set_conf("RES:RANGE", range_ohms)
        self._set_conf("RES:NPLC", aperture_plc)
        self._set_func("FRES" if four_wire else "RES")
        return self._read()

    def get_capacitance(self, range_farads: float = 1e-6) -> float:
        self._set_conf("CAP:RANGE", range_farads)
        self._set_func("CAP")
        return self._read()

    def get_frequency(self, range_volts: float = 10.0, bandwidth_hz: float = 20.0, gate_seconds: float = 0.1) -> float:
        self._set_freq_period_conf(range_volts, bandwidth_hz, gate_seconds)
        self._set_func("FREQ")
        return self._read()

    def get_period(self, range_volts: float = 10.0, bandwidth_hz: float = 20.0, gate_seconds: float = 0.1) -> float:
        self._set_freq_period_conf(range_volts, bandwidth_hz, gate_seconds)
        self._set_func("PER")
        return self._read()

    def get_continuity(self) -> float:
        self._set_func("CONT")
        return self._read()

    def _set_freq_period_conf(self, range_volts: float, bandwidth_hz: float, gate_seconds: float):
        self._set_conf("FREQ:VOLT:RANGE", range_volts)
        self._set_conf("FREQ:RANGE:LOW", bandwidth_hz)
        self._set_conf("FREQ:APER", gate_seconds)

    def _set_curr_range(self, acdc: str, range_amps: float):
        if range_amps > 3.0:
            self._set_conf(f"CURR:{acdc}:TERM", 10)
        else:
            self._set_conf(f"CURR:{acdc}:TERM", 3)
            self._set_conf(f"CURR:{acdc}:RANGE", range_amps)

    def _set_func(self, func):
        if self._func != func:
            self._func = func
            self.scpi.write(f'FUNC "{func}"')

    def _set_conf(self, key, value):
        value = f"{value:0.1g}"
        if self._conf.get(key, None) != value:
            self._conf[key] = value
            self.scpi.write(f"{key} {value}")

    def _read(self) -> float:
        return float(self.scpi.query("READ?"))
        

