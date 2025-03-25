import nautilus


if __name__ == "__main__":
    with nautilus.Nautilus() as jig:
        print(jig.get_mac())
