from pint import UnitRegistry
from collections import OrderedDict
import re
ureg = UnitRegistry()

__name__ = "pint_worker"

units=OrderedDict([("ampere","ampere"), ("watt","watt"), ("ohm","ohm"), ("meter","meter"), ("sekunden","seconds"), ("sekunde","second"), ("pro","per"), ("centimeter","centimeter")]) 
#unsere self.units als resultat von translate_namedvalues() => orderedDict
#da wir keine generate_plural_de (wie auch in anderen Sprachen) in LF haben müssen wir die mehrzahl mit in self.units packen
#string="wie lang ist der zurückgelegte Weg nach 50 millisekunden bei 12 meter pro sekunde" #darauf achten, das der string nur kleinbuchstaben hat (string.lower())
pint_abrevations={"meter per second": "mps"}   

def translate_unit(unitname, translation, string, splitted=""):
    

    r = re.compile(".*"+unitname)
    checkpos=splitted.index(list(filter(r.match, splitted))[0]) #der list(...) ausdruck ist nur relevant wenn wir milli,... aus self.units herauslassen
    prefix=splitted[checkpos].split(unitname)[0]
    #checkt das wort vor unit ob es eine weitere unit ist (inkl. "per") 
    if splitted[checkpos-1] not in units.keys() and splitted[checkpos-1] not in units.values():#items
        rx_pattern = "{"+prefix+translation.lower()+"}.*"+prefix+translation.lower()
    else:
        rx_pattern = prefix+translation.lower()
    #ersetzt das wort mit dem englischen
    string=string.replace(unitname, translation)
    splitted=string.split(" ")
    
    return rx_pattern

def worker(string): 

    splitted=string.lower().split(" ")
    #ruft translate_unit() auf wenn er eine übersetzbare Einheit findet
    patternlist=[]
    for word in splitted:
        for unit, trans in units.items():
            if re.match(r".*"+unit,word):
                rx=translate_unit(unit, trans, string, splitted)
                if re.match(r"^{.*}",rx): 
                    patternlist.append(rx)
                else:
                    patternlist[-1]+=".*"+rx
                break
    print(str(patternlist))
    pattern = make_pattern(patternlist)
    pintObj=ureg.parse_pattern(string, pattern, many=True)
    print(pintObj)
    #pattern mit abkürzung ersetzen falls nötig

def make_pattern(patternlist):
    for i, pattern in enumerate(patternlist): 
        for unit, abr in pint_abrevations.items():
            if unit in pattern.replace(".*"," "):
                patternlist[i]=re.sub(r"({)(.*)(})", r"\1"+abr+r"\3", pattern) 
    #regex pattern falls es mehrere einheitenpaare gibt
    pattern = r".*".join(patternlist)
 
    #print(pattern)
    return pattern