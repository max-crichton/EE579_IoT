

class Groups:
    def __init__(self, name, devices=[]):
        self.name = name
        self.devices = devices

    def add(self, device):
        self.devices.append(device)
