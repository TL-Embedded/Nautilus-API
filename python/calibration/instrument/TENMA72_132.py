from . import SCPI

class TENMA72_132():
    def __init__(self, uri: str = None):
        if uri == None:
            uri = TENMA72_132.find_devices()[0]
        self.scpi = SCPI.from_uri(uri, is_tcp=False)

    def is_present(self, throw_on_error: bool = False) -> bool:
        # TENMA 72-13210 V2.50 SN:00011654
        success = self.scpi.get_idn().startswith("TENMA 72-132")
        if throw_on_error and not success:
            raise Exception("TENMA 72-132x0 not found")
        return success

    def close(self):
        self.scpi.close()

    def get_voltage(self) -> float:
        return self._get_number(":MEAS:VOLT?")

    def get_current(self) -> float:
        return self._get_number(":MEAS:CURR?")

    def get_power(self) -> float:
        return self._get_number(":MEAS:POW?")

    def set_input(self, is_on: bool):
        self.scpi.write(f":INP {'ON' if is_on else 'OFF'}")

    def set_voltage(self, volts: float):
        self.scpi.write(f":VOLT {volts:.3f}V")

    def set_current(self, amps: float):
        self.scpi.write(f":CURR {amps:.3f}A")

    def set_power(self, watts: float):
        self.scpi.write(f":POW {watts:.3f}W")

    def set_resistance(self, ohms: float):
        self.scpi.write(f":RES {ohms:.3f}OHM")

    def config_network(self, ip: str | None = None, subnet: str = "255.255.255.0", port: int = 5025, dhcp: bool = True):
        if ip != None:
            self.scpi.write(f":SYST:IPAD {ip}")
        self.scpi.write(f":SYST:SMASK {subnet}")
        self.scpi.write(f":SYST:DHCP {1 if dhcp else 0}")
        self.scpi.write(f":SYST:PORT {port}")

    def _get_number(self, command: str) -> float:
        result = self.scpi.query(command)
        return float(result.strip()[:-1])

    @staticmethod
    def find_devices(max_devices: int = 1) -> list[str]:
        results = []
        for data, _ in SCPI.broadcast_search(b"find_ka000", 18191):
            try:
                text = data.decode().splitlines()
                ip = text[0]
                port = text[2]
                results.append(f"udp://{ip}:{port}")
                if len(results) >= max_devices:
                    break
            except:
                pass
        return results
