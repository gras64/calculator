from pint import UnitRegistry
from os.path import abspath, dirname, join
from collections import OrderedDict
import re
pint_formul = join(
            abspath(dirname(__file__)), "default_en.txt"
            )
ureg = UnitRegistry(pint_formul,fmt_locale='de_DE')
#Q =ureg.Qualtity

__author__ = 'gras64', 'sgee_'
__name__ = "pint_worker"

units=OrderedDict([("ampere","ampere"),("volt", "volt"), ("watt","watt"), ("ohm","ohm"), ("meter","meter"), ("sekunden","seconds"), ("sekunde","second"), ("pro","per")]) 
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
        rx_pattern = "{"+prefix+translation.lower()+"}\D*"+prefix+translation.lower()
    else:
        rx_pattern = prefix+translation.lower()
    #ersetzt das wort mit dem englischen
    #print("translation "+translation+ " unit "+unitname+ " string "+ string)
    string=string.replace(unitname, translation)
    splitted=string.split(" ")
    
    return rx_pattern, string

def worker(string): 

    splitted=string.lower().split(" ")
    #ruft translate_unit() auf wenn er eine übersetzbare Einheit findet
    patternlist=[]
    for word in splitted:
        #if not word in ureg:
        for unit, trans in units.items():
            if re.match(r"\D*"+unit,word):
                #print("unit "+ unit+ " "+ trans)
                #rx =ureg.parse_unit_nameparse_units(string)
                #print("rx"+str(rx))
                #rx = str(rx)
                rx, string=translate_unit(unit, trans, string, splitted)
                if re.match(r"^{\D*}",rx):
                    if not rx in patternlist: 
                        patternlist.append(rx)
                else:
                    patternlist[-1]+="\D*"+rx
                break
    
    print("patternlist "+str(patternlist))
    pattern = make_pattern(patternlist)
    #pattern = '{ampere}\D*ampere\D*{ohm}\D*ohm'
    #pattern = "{seconds}.*seconds.*{meter}.*meter.*per.*{millisecond}.*millisecond.*{ampere}.*ampere"
    print("pattern "+pattern)
    print("string: "+string)
    pintObj=ureg.parse_pattern(string, pattern, many=True)
    #pintObj=ureg.parse_units(string, as_delta=None)
    #pintObj=ureg.parse_expression(pintObj, many=True)
    print("output: "+str(pintObj))
    #pattern mit abkürzung ersetzen falls nötig
    return pintObj, string

def task_worker(task):
    for unit, trans in units.items():
        if re.match(r"\D*"+unit,task):
            #print("unit "+ unit+ " "+ trans)
            rx, task =translate_unit(unit, trans, task)
            if re.match(r"^{\D*}",rx):
                if not rx in patternlist: 
                    patternlist.append(rx)
            else:
                patternlist[-1]+="\D*"+rx
            break
    return pattern


def make_pattern(patternlist):
    for i, pattern in enumerate(patternlist): 
        for unit, abr in pint_abrevations.items():
            if unit in pattern.replace(".*"," "):
                patternlist[i]=re.sub(r"({)(.*)(})", r"\1"+abr+r"\3", pattern) 
    #regex pattern falls es mehrere einheitenpaare gibt
    pattern = r"\D*".join(patternlist)
 
    return pattern

def calculate(pintObj, task):
    print("from "+str(pintObj)+ " to "+task)
    return ureg.pintObj.to(task)