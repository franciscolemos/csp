import unittest
import main


class ARP(unittest.TestCase):
    def __init__(self, *args, **kwargs):
        super(ARP, self).__init__()
        self.m = main.ARP()
        self.m.initialize()

    def fs(self):
        s0 = len(main.fs)
        s1 = len(self.m.fixedFlights) #sizeFixedFlights
        s2 = len(self.m.movingFlights) #sizeMovingFlights
        self.assertEqual(s0, s1 + s2)

ARP().fs()

