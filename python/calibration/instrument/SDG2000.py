from . import SCPI
from collections import OrderedDict
import math
import time


class SDG2000Wave():
    def __init__(self, host: 'SDG2000'):
        self._host = host
        self._bswv: dict[str,str] = OrderedDict()
        self._commands: dict[str, str] = OrderedDict()

    def amplitude(self, amplitude_volts: float, offset_volts: float = 0.0) -> 'SDG2000Wave':
        return self._set_basic_params({
            "AMP": f"{amplitude_volts:0.3f}V",
            "OFST": f"{offset_volts:0.3f}V",
        })

    def span(self, min_volts: float, max_volts: float)  -> 'SDG2000Wave':
        return self.amplitude(
            max_volts - min_volts,
            (max_volts + min_volts) / 2.0
            )

    def frequency(self, frequency_hz: float, phase_deg: float = 0.0) -> 'SDG2000Wave':
        return self._set_basic_params({
            "FRQ": f"{frequency_hz}HZ",
            "PHSE": f"{phase_deg:0.1f}",
        })
    
    def period(self, period_s: float, delay_s: float = 0.0) -> 'SDG2000Wave':
        return self.frequency(
            1.0 / period_s,
            360 * delay_s / period_s
        )
    
    def wave_sine(self) -> 'SDG2000Wave':
        return self._set_basic_params({
            "WVTP": "SINE",
        })
    
    def wave_square(self, duty_percent: float = 50.0) -> 'SDG2000Wave':
        return self._set_basic_params({
            "WVTP": "SQUARE",
            "DUTY": f"{duty_percent:0.1f}",
        })
    
    def wave_dc(self) -> 'SDG2000Wave':
        self._set_basic_params({
            "WVTP": "DC",
        })

    def wave_ramp(self, symmetry_percent: float = 50.0) -> 'SDG2000Wave':
        return self._set_basic_params({
            "WVTP": "RAMP",
            "SYM": f"{symmetry_percent:0.1f}",
        })
    
    def wave_noise(self, stddev_volts: float, bandwidth_hz: float|None = None)  -> 'SDG2000Wave':
        params = {
            "WVTP": "NOISE",
            "STDEV": f"{stddev_volts:0.3f}V",
            "BANDSTATE": "ON" if bandwidth_hz else "OFF"
        }
        if bandwidth_hz:
            params["BANDWIDTH"] = f"{bandwidth_hz:f}"
        return self._set_basic_params(params)
    
    def wave_pulse(self, width_seconds: float = 1e-3, rise_seconds: float = 0.0)  -> 'SDG2000Wave':
        return self._set_basic_params({
            "WVTP": "PULSE",
            "WIDTH": f"{width_seconds:f}S",
            "RISE": f"{rise_seconds:f}S",
        })
    
    def wave_builtin(self, name: str) -> 'SDG2000Wave':
        index = self._host._get_builtin_waves()[name]
        self._commands["ARWV"] = f"INDEX,{index}"
        self._commands["SRATE"] = f"MODE,DDS"
        return self
    
    def wave_user(self, name: str) -> 'SDG2000Wave':
        self._commands["ARWV"] = f"NAME,{name}"
        self._commands["SRATE"] = f"MODE,DDS"
        return self
    
    def sample_rate(self, sample_rate_hz: int, interpolate: bool = True):
        self._commands["SRATE"] = f"MODE,TARB,VALUE,{sample_rate_hz},INTER,{'LINE' if interpolate else 'HOLD'}"
        return self

    def submit(self):
        if len(self._bswv):
            # Because _arbwave is ordered, this command is executed last
            self._commands["BSWV"] = ",".join( f"{k},{v}" for k,v in self._bswv.items())

        for key, params in self._commands.items():
            self._host._channel_command(f"{key} {params}")

    def _set_basic_params(self, params: dict[str,str]) -> 'SDG2000Wave':
        self._bswv.update(params)
        return self


class SDG2000():
    def __init__(self, uri: str):
        self.scpi = SCPI.from_uri(uri)
        self.selected_channel = 1
        self._ch = "C1"
        self._builtin_waves = None

    def is_present(self, throw_on_error: bool = False) -> bool:
        # Siglent Technologies,SDG2082X,SDG2XCAD5R3269,2.01.01.35R3B2
        success = self.scpi.get_idn().startswith("Siglent Technologies,SDG20")
        if throw_on_error and not success:
            raise Exception("HDM3055 not found")
        return success

    def close(self):
        self.scpi.close()

    def select_channel(self, ch: int):
        self.selected_channel = ch
        self._ch = f"C{ch}"

    def set_wave(self) -> SDG2000Wave:
        '''
        Returns a SDG2000Wave object. Wave parameters are set via chained calls to this object.
        The parameters are submitted to the instrument simultaniously via the `submit` function.
        `sdg.set_wave().amplitude(1.0).frequency(2000).submit()`
        '''
        return SDG2000Wave(self)

    def set_output(self, is_on: bool, load_ohms: float|None = None):
        '''
        Warning: Changing the load impedance after setting the amplitude results in a changed amplitude (doubled or halved)
        '''
        load = f"{load_ohms:.0f}" if type(load_ohms) is float else "HZ"
        self._channel_command(f"OUTP {'ON' if is_on else 'OFF'},LOAD,{load}")

    def set_burst_cycles(self, period_seconds: float, cycles: int = 1):
        self._channel_command(f"BTWV STATE,ON,PRD,{period_seconds},GATE_NCYC,NCYC,TIME,{cycles}")

    def disable_burst(self):
        self._channel_command("BTWV STATE,OFF")

    def list_builtin_waves(self) -> list[str]:
        return [name for name in self._get_builtin_waves()]
    
    def list_user_waves(self) -> list[str]:
        reply = self.scpi.query("STL? USER")
        # STL WVNM,wave,wave1
        # Discard 'WVNM'
        return reply[4:].split(',')[1:]

    def upload_user_wave(self, name: str, points: list[float]):
        '''
        Uploads a user waveform. The waveform should be a list of sample points from -1.0 to 1.0
        The frequency and ampliude should be selected when the wave is loaded.
        '''
        payload = bytearray()
        for p in points:
            n = math.floor(p * 0x7FFF)
            n = self._sanitize_point(n) # required for early firmware.
            payload.append(n & 0xFF)
            payload.append((n >> 8) & 0xFF)
        command = f"C1:WVDT WVNM,{name},WAVEDATA,".encode()
        self.scpi.write_bytes(command + payload + bytes([0x0A]))

        # Big yikes.
        time.sleep(0.5)
        self._sync()
        
    def _sync(self):
        # For some reason consecutive commands seem to cause issues.
        # Waiting for the status byte straightens this all out.
        stb = int(self.scpi.query("*STB?"))

    def _channel_command(self, command: str):
        self.scpi.write(f"{self._ch}:{command}")
        self._sync()

    def _sanitize_point(self, n: int) -> int:
        # Literally the dumbest garbage
        # Having an 0x0A ('\n') within a datapoint causes the command to be truncated.
        if (n & 0xFF00) == 0x0A00:
            if n > 0x0A7F:
                return 0x0B00
            else:
                return 0x09FF
        if (n & 0x00FF) == 0x000A:
            return n + 1
        return n

    def _get_builtin_waves(self) -> dict[str, int]:
        if self._builtin_waves == None:
            reply = self.scpi.query("STL? BUILDIN")
            #STL M10, ExpFal, M100, ECG14...
            waves = {}
            parts = reply[4:].split(', ')
            for i in range(0, len(parts), 2):
                index = int(parts[i][1:])
                name = parts[i+1]
                waves[name] = index
            self._builtin_waves = waves
        return self._builtin_waves
    



