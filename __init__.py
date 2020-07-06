import re
import json
import math
#from sympy.physics import units
from mycroft import MycroftSkill, intent_file_handler, intent_handler
from adapt.intent import IntentBuilder
from mycroft.util.parse import extract_number, normalize, extract_numbers
from mycroft.util.format import pronounce_number, nice_date, nice_time

_author__ = 'gras64'

class Calculator(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        tax = self.settings.get('tax').replace(",", ".") \
            if self.settings.get('tax').replace(",", ".") else "9.3"
        sale = self.settings.get('sale') \
            if self.settings.get('sale') else "30"
        self.sale = "* "+str((100+float(sale))/100) # * 1.30
        self.net = "* "+str((100-float(tax))/100) # * 0.907
        self.gross = "* "+str((100+float(tax))/100) # * 1.093
        self.log.info("calculator factor load: sale="+self.sale+" gross="+self.gross+" net="+self.net)
        self.units_value = self.translate_namedvalues('units.value')
        ### init unit
        formula = formula_switcher()
        self.init_units = []
        for unit in formula.dir():
            if not '__' in unit:
                units = [unit, "milli"+unit, "centi"+unit, "deci"+unit, "micro"+unit, "nano"+unit, "kilo"+unit, "mega"+unit, "giga"+unit]
                self.init_units.extend(units)
        self.init_units.remove('switch')
        self.init_units.remove('dir')
        self.init_units.remove('units')
        self.log.info("init units "+str(self.init_units))
        self.load_unit_vocab() 

    def load_unit_vocab(self): ### expand vocab
        for unit in self.init_units:
            self.register_vocabulary(unit, 'units')
            #self.log.info("add vocab "+str(unit))

    @intent_handler(IntentBuilder("cal").one_of("tell_me", "replacement_word").optionally("calculate").
                    one_of("addition", "division", "multiplication", "subtraction", "net", "gross", "sale", "percent", "units").build())
    def calculate_handler(self, message):
            self.log.info("boot")
            text = message.utterance_remainder()
            number = extract_number(text, lang=self.lang)
            #if type(number) is int:
            self.calculate_worker(message.data['utterance'], message)

    def calculate_worker(self, text, message):
        text = self.num_worker(text)
        self.log.info("found "+text)
        if message.data.get("units", False): ### select unit or default calculation
            text = self.units_worker(text)
            text , factors = self.units_converter(text)
            self.units_operator(text, factors)
        else:
            text = self.oparator_worker(text)
            text = self.num_cleaner(text)
            text = self.oparator_validator(text)
            if not text is False:
                text = self.oparator_calculator(text)


    def num_worker(self, line):
        ### translate numbers to int
        num = ""
        number = ""
        if not extract_numbers(line, lang=self.lang) == []:
            num = extract_numbers(line, short_scale=False, ordinals=False,
                        lang=self.lang)
        #num = re.sub(r'(\.0)', '', str(num))
        #num = re.findall(r'\d+', num)
        if not num is False:
            for item in num:
                print("item #"+str(item))
                if not pronounce_number(float(item), lang=self.lang, short_scale=True) ==[]:
                    number = pronounce_number(float(item), lang=self.lang, short_scale=True)
                else:
                    number = ""
                line = line.replace(number, str(item))
                self.log.info(str(line))
        return line

    def num_cleaner(self, text):
        text = re.sub("[^0-9/* +-.),(]", "", text) #delete text
        text = re.findall(r'[0-9(][0-9/* +-.),(]+[)0-9]', text) # only operator and number
        return text
        #* 4 + 5 / 7 to  4 + 5 / 7

    def oparator_worker(self, text): ## detect operators and replace
        line = text.split()
        operator = None
        ### what is the net amount of 30 << swap "net amount" with "30" (bad fix)
        for nr, word in enumerate(line): 
            if self.voc_match(word, "from") :
                f = nr-1
                d = nr-2
                t = nr+1
                if not self.oparator_match(word) is None:
                    line[f], line[t] = line[t], line[f]
                else:
                    try:
                        line[d], line[f], line[nr], line[t] = line[t], line[nr], line[d], line[f]
                    except:
                        pass
                self.log.info("swap "+ line[f]+ " with "+line[t])
        text= " ".join(line)
        ###
        for word in line:
            #self.log.info("text1 "+text+" "+word)
            if self.oparator_match(word):
                for s in line:
                    if self.voc_match(s, "replacement.word"):
                        text = text.replace(s, str(word))
            operator = self.oparator_match(word)
            if not operator is None: ##### todo problem with "and from that"
                if operator is "from_that":
                    text = text.replace(word, ")")
                    text = "( "+text
                else:
                    text = text.replace(word, str(operator))
            self.log.info("after operator"+text)
        return text
    

    def units_worker(self, text):
        ### extract units
        line = text.split() 
        units = {}
        for nr, unit in enumerate(line):
            if unit in self.init_units or self.voc_match(unit, "units"):
                s = nr-1
                try:
                    unit = self.units_value[unit] ### translate units to english
                except:
                    pass
                unit = unit.replace(" ", "") ##?
                try:
                    number = float(line[s])
                except:
                    number = False
                units.update({unit : number})
        ###
        self.log.info(str(units))
        return units
    
    def units_converter(self, text): ### todo make it better
        factors = {}
        for key, value in list(text.items()):
            del text[key]
            if "milli" in key:
                akey = key.replace("milli", "")
                factor = '/1000'
            elif "centi" in key:
                akey = key.replace("centi", "")
                factor = '/100'
            elif "deci" in key:
                akey = key.replace("deci", "")
                factor = '/10'
            elif "micro" in key:
                akey = key.replace("micro", "")
                factor = '/1000000'
            elif "nano" in key:
                akey = key.replace("nano", "")
                factor = '/1000000000'
            elif "kilo" in key:
                akey = key.replace("kilo", "")
                factor = '*1000'
            elif "mega" in key:
                akey = key.replace("mega", "")
                factor = '*100000'
            elif "giga" in key:
                akey = key.replace("giga", "")
                factor = '*key'
            else:
                factor = '*1'
                akey = key
            #text[akay] = [value, factor]
            if not value is False:
                text.update({akey : eval(str(value)+factor)}) ### calculate factor
            else:
                text.update({akey : value})
            factors.update({akey : [key, factor]})
        self.log.info("after unit converter "+str(text))
        return text, factors

    def units_operator(self, unit, factors): ### add units calculation here
        calculation = []
        result = []
        f = True
        while True:
            try:
                for key, value in list(unit.items()):
                    if value is False: #### add your formulas here
                        formula = formula_switcher()
                        result = formula.switch(unit, key) ###see class formula_switcher
                break
            except KeyError as var:
                var = str(var)
                self.log.info("fail with "+var)
                unit[var] = self.get_response("var.not.found", data={"var":str(var)})
                if self.voc_match(unit[var], "cancel"):
                    return
                unit[var] = extract_number(unit[var], short_scale=False, ordinals=False,
                        lang=self.lang)     
        ### preparation the output
        for key, value in list(unit.items()):
            akey = factors[key][0] ### factors back
            if "/" in factors[key][1]:
                factor = factors[key][1].replace("/", "*")
            elif "*" in factors[key][1]:
                factor = factors[key][1].replace("*", "/")
            if value is False:
                value = str(result)
                okey = akey
                result = eval(str(value)+factor) ### factors back
            else:
                value = eval(str(value)+factor)
                calculation.append(str(value)+" "+str(akey)+" ")
        calculation = " ".join(calculation)
        result = (str(result)+" "+str(okey)+" ")
        self.speak_dialog("result", data={"calculation":calculation, "result":result})

        
    def oparator_match(self, word): ### add aperators here
        if self.voc_match(word, "addition"):
            operator = "+"
        elif self.voc_match(word, "subtraction"):
            operator = "-"
        elif self.voc_match(word, "multiplication"):
            operator = "*"
        elif self.voc_match(word, "division"):
            operator = "/"
        elif self.voc_match(word, "net"):
            operator = self.net # *1.093
        elif self.voc_match(word, "gross"):
            operator = self.gross # *0.907
        elif self.voc_match(word, "sale"):
            operator = self.sale
        elif self.voc_match(word, "clip.on"):
            operator = "("
        elif self.voc_match(word, "clip.off"):
            operator = ")"
        #elif self.voc_match(word, "percent"): ##### todo fix
        #    operator = "/100" ### todo
        elif self.voc_match(word, "from.that"):
            operator = "from_that"           
        else:
            operator = None
        return operator

    def oparator_calculator(self, text):
        calculation = text[0]
        result = round(eval(text[0]), 2)
        calculation = calculation.replace(".", ",")
        if self.lang == "de-de":
            result = str(result).replace(".", ",")
        self.speak_dialog("result", data={"calculation":calculation, "result":result})
        self.log.info(eval(text[0]))

    def oparator_validator(self, text):
        ### calculated and reduced until calculation possible
        if ")" in text: ### if ( not found
            if not "(" in text:
                text = "( "+text
        ###
        f = True
        while f is True:
            try:
                if not eval(text[0]) is False:
                    f = False
            except SyntaxError:
                text = text[0].split(' ')
                text.pop()
                if len(text) <= 1:
                    text = text.clear()
                    f = False
                    continue
                text[0] = " ".join(text)
                self.log.info("text fail and fix"+str(text))
                f = True
        else:
            if text == None:
                ##### todo send it to fallback
                responce  = self.get_response("fail")
                self.calculate_worker(responce)
                return False
        self.log.info("text "+str(text))
        return text

    def shutdown(self):
        super(Calculator, self).shutdown()

def create_skill():
    return Calculator()

class formula_switcher():
    units = {}
    def dir(self):
        return dir(formula_switcher)
    def switch(self, unit, key):
        global units
        units = unit
        default = "Incorrect"
        return getattr(self, key, lambda: default)()
    #### add your formulas here
    ### Ohm's law
    def ohm(self):
        return units["volt"]/units["ampere"]
    def volt(self):
        return units["ohm"]*units["ampere"]
    def ampere(self):
        return units["volt"]/units["ohm"]
    def watt(self):
        if "volt"  in units.keys() and "ampere" in units.keys():
            return units["volt"]*units["ampere"]
        elif "ampere" in units.keys() and "ohm" in units.keys():
            return (units["ampere"]**2)*units["ohm"]
        elif "volt" in units.keys() and "ohm" in units.keys():
            return (units["volt"]**2)*units["ohm"]
        ### circle
    def diameter(self):
        if "radius" in units.keys():
            return units["radius"]*2
        elif "scope"  in units.keys():
            return (units["scope"]/(2*math.pi))*2
        elif "surface" in units.keys():
            radius = units["surface"]/math.pi
            return math.sqrt(radius)*2
    def radius(self):
        if "diameter" in units.keys():
            return units["diameter"]/2
        elif "scope"  in units.keys():
            return units["scope"]/(2*math.pi)
        elif "surface" in units.keys():
            radius = units["surface"]/math.pi
            return math.sqrt(radius)
    def scope(self):
        if "diameter" in units.keys():
            radius = units["diameter"]/2
            return 2*math.pi*radius
        elif "radius"  in units.keys():
            return 2*math.pi*units["radius"]
        elif "surface" in units.keys():
            result = units["surface"]/math.pi
            radius = math.sqrt(result)
            return 2*math.pi*radius
    def surface(self):
        if "diameter" in units.keys():
            radius = units["diameter"]/2
            return math.pi*(radius**2)
        elif "radius"  in units.keys():
            return math.pi*(units["radius"]**2)
        elif "scope" in units.keys():
            radius = units["surface"]/(2*math.pi)
            return math.pi*(radius**2)
    ### breaking distance car
    def brakingdistance(self):
        return (units["kmh"]/10)*(units["kmh"]/10)

