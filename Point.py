
from decimal import Decimal

import math


class Point:
    def __init__(self, x=0.0, y=0.0):
        self.x = x
        self.y = y

    @classmethod
    def from_point(cls, p):
        return cls(p.x, p.y)

    def __repr__(self):
        return f"({Decimal(self.x):.3f},{Decimal(self.y):.3f})"


