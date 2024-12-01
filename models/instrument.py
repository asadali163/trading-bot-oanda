import math
class Instrument:

    def __init__(self, name, ins_type, displayName, pipLocation, tradeUnitsPrecision, marginRate, displayPrecision):
        self.name = name
        self.ins_type = ins_type
        self.displayName = displayName
        self.pipLocation = math.pow(10, pipLocation)
        self.tradeUnitsPrecision = tradeUnitsPrecision
        self.marginRate = marginRate
        self.displayPrecision = displayPrecision


    def __str__(self):
        return f"{self.name} - {self.displayName}"
    
    @classmethod
    def FromAPIObject(cls, ob):
        return Instrument(
            ob['name'],
            ob['type'],
            ob['displayName'],
            ob['pipLocation'],
            ob['tradeUnitsPrecision'],
            ob['marginRate'],
            ob['displayPrecision']
        )
