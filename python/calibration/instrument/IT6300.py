from . import SCPI
from typing import Callable
import time

class IT6300CH():
    def __init__(self, host: 'IT6300', index: int):
        self.host = host
        self.channel = index

    def get_voltage(self) -> float:
        self.host.select_channel(self.channel)
        return self.host.get_voltage()
    
    def get_current(self) -> float:
        self.host.select_channel(self.channel)
        return self.host.get_current()

    def set_voltage(self, volts: float):
        self.host.select_channel(self.channel)
        self.host.set_voltage(volts)

    def set_current(self, amps: float):
        self.host.select_channel(self.channel)
        self.host.set_current(amps)

    def set_output(self, is_on: bool):
        self.host.select_channel(self.channel)
        self.host.set_output(is_on)


class IT6300():
    def __init__(self, uri: str = None):
        if uri == None:
            uri = IT6300.find_devices()[0]
        self.scpi = SCPI.from_uri(uri)
        self.channels = [
            IT6300CH(self, i+1) for i in range(3)
        ]
        self.selected_channel = -1
    
    def is_present(self, throw_on_error: bool = False) -> bool:
        # ITECH Ltd., IT6302, 800071020767110110, 1.05-1.04
        success = self.scpi.get_idn().startswith("ITECH Ltd., IT63")
        if throw_on_error and not success:
            raise Exception("IT6302 not found")
        return success

    def close(self):
        self.set_remote(False)
        self.scpi.close()

    def set_remote(self, is_remote: bool):
        mode = "REM" if is_remote else "LOC"
        self.scpi.write(f"SYST:{mode}")

    def get_channel(self, ch: int) -> IT6300CH:
        return self.channels[ch-1]

    def select_channel(self, ch: int):
        if self.selected_channel != ch:
            self.scpi.write(f"INST:NSEL {ch}")
            if int(self.scpi.query("INST:NSEL?")) != ch:
                raise Exception("Channel change failed")
            self.selected_channel = ch

    def get_voltage(self) -> float:
        return float(self.scpi.query("MEAS:VOLT?"))

    def get_current(self) -> float:
        return float(self.scpi.query("MEAS:CURR?"))
    
    def set_voltage(self, volts) -> float:
        self.scpi.write(f"VOLT {volts:.3f}V")
    
    def set_current(self, amps: float):
        self.scpi.write(f"CURR {amps:.3f}A")

    def set_output(self, is_on: bool):
        self.scpi.write(f"CHAN:OUTP {1 if is_on else 0}")
    
    @staticmethod
    def find_devices(max_devices: int = 1) -> list[str]:
        results = []
        for data, _ in SCPI.broadcast_search(b"find_it6300", 18191):
            try:
                text = data.decode().splitlines()
                ip = text[0]
                port = text[2]
                results.append(f"tcp://{ip}:{port}")
                if len(results) >= max_devices:
                    break
            except:
                pass
        return results
    
    def calibrate_current(self, get_current: Callable[[],float]):
        # The output should pass through a DMM that can measure the test current

        self.scpi.write(f"CAL:SEC 0, '6302'")
        if int(self.scpi.query("CAL:SEC?")) != 0:
            raise Exception("Security change failed")

        for i in range(2):
            self.scpi.write(f"CAL:CURR:LEV P{i+1}")
            time.sleep(1.0)
            current = get_current()
            self.scpi.write(f"CAL:CURR {current:.3f}A")
            time.sleep(0.1)

        self.scpi.write("CAL:SAV")
        self.scpi.write(f"CAL:SEC 1")

    def calibrate_voltage(self, get_voltage: Callable[[],float]):
        # The output should be metered by a DMM that can measure the test voltage

        self.scpi.write(f"CAL:SEC 0, '6302'")
        if int(self.scpi.query("CAL:SEC?")) != 0:
            raise Exception("Security change failed")

        for i in range(4):
            self.scpi.write(f"CAL:VOLT:LEV P{i+1}")
            time.sleep(1.0)
            voltage = get_voltage()
            self.scpi.write(f"CAL:VOLT {voltage:.3f}V")
            time.sleep(0.1)

        self.scpi.write("CAL:SAV")
        self.scpi.write(f"CAL:SEC 1")


