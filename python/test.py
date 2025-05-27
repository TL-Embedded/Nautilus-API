import nautilus


if __name__ == "__main__":
    with nautilus.Nautilus() as jig:
        jig.reset()
        print( f"version: {jig.get_version()}" )
        print( f"mac: {jig.get_mac()}" )
        print( f"vin: {jig.get_vin()} V" )
        print( f"temp: {jig.get_temperature()} C" )
