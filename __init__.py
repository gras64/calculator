import re
import yaml ##
from os.path import os, abspath, dirname, join
import json
import math
#import spacy
from json_database import JsonStorage
#from sympy.physics import units
from mycroft.messagebus.message import Message
from mycroft import MycroftSkill, intent_file_handler, intent_handler
from adapt.intent import IntentBuilder
from adapt.engine import IntentDeterminationEngine
from mycroft.util.parse import extract_number, normalize, extract_numbers
from mycroft.util.format import pronounce_number, nice_date, nice_time
from .lib.pint_worker import worker

_author__ = 'gras64'

class Calculator(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        formulfiles = {
            "en-us":"default_en.txt",
            "de-de":"default_en.txt",
        }
        spacy_lang = {
            "en-us": "de_core_news_lg",
            "de-de": "de_core_news_lg",
        }
 #       self.nlp = spacy.load(spacy_lang[self.lang])
        pint_formul = join(
            abspath(dirname(__file__)), formulfiles[self.lang]
        )
        self.ureg = UnitRegistry(pint_formul)
        tax = self.settings.get('tax').replace(",", ".") \
            if self.settings.get('tax').replace(",", ".") else "9.3"
        sale = self.settings.get('sale') \
            if self.settings.get('sale') else "30"
        self.register_entity_file('task.entity')
        self.sale = "* "+str((100+float(sale))/100) # * 1.30
        self.net = "* "+str((100-float(tax))/100) # * 0.907
        self.gross = "* "+str((100+float(tax))/100) # * 1.093
        self.operators={"addition":"+","subtraction":"-","multiplication":"*", ### add aperators here
                 "division": "/", "net": self.net, "gross": self.gross, "sale": self.sale, "clip.on":"(",
                 "clip.off":")", "from.that": "from_that"} #net   *1.093 , gross *0.907
        self.factors ={"milli": "/1000", "centi": "/100", "deci": "/10", "micro": "/1000000",
                "nano":"/1000000000", "kilo": "*1000", "mega":"*100000", "giga":"*1000000000"}
        self.log.info("calculator factor load: sale="+self.sale+" gross="+self.gross+" net="+self.net)
        self.units_value = self.translate_namedvalues('units.value')
        self.log.info(str(self.units_value))
        self.tasks_value = self.translate_namedvalues('tasks.value')
        ### init unit
        self.init_units = []
        self.wish_overview = {}
        formula = formula_switcher()
        for unit in dir(formula):
            if not '__' in unit and not "switch" in unit and not "units" in unit:
                self.log.info(unit)
                self.init_units.extend([unit] + [key+unit for key in self.factors.keys()]) ### load intents of watt miliwatt magawatt ...
                try:
                    operations = getattr(formula, unit)
                    for operation in dir(operations):
                        if not '__' in operation:
                            formula = operation
                            try:
                                formula = self.tasks_value[operation]
                            except:
                                pass
                            self.wish_overview.update({operation : [unit, formula]}) ######
                except:
                    pass
        calculate = 3 * self.ureg.meter + 4 * self.ureg.cm
        self.log.info("calculate "+repr(calculate))
        test = self.ureg
        self.write_variable([key for key in dir(self.ureg)], "all_units")
        self.write_variable(self.init_units, "initunits")
        self.write_variable(self.wish_overview, "formulas") ############################################################################
        self.log.info("init units "+str(self.init_units))
        self.log.info("formulas startup "+str(self.wish_overview))
        self.load_unit_vocab()
        self.load_test_sentence()
        #self.load_formulas()
        
        liste=["meter", "kilometer"]
        for i in liste:
            a = 1 * self.ureg[i]
            self.log.info(a.format_babel(locale='de_DE'))

    def load_test_sentence(self):
        sentence = ("wie viel volt ergeben sich aus 30 ampere und 40 watt",
                    "wie lang ist der zurückgelegte Weg nach 50 millisekunden bei 12 meter pro sekunde und 30 ampere",
                    "was ist die fallgeschwindigkeit nach 12 sekunden",
                    #"wie ist der weg bei 150 centimeter umfang und 2 meter mit 5 sekunden durchhaltevermögen",
                    "wie ist die spannung bei 20 ampere und 3000 milliohm")
        for text in sentence:
            worker(text)
        #    self.formul_calculate_handler(text)


    def unit_extractor(self, string):
        pass
        #self.log.info("type "+str(type(r))+str(r.dimensionality))
        #pint.unit.build_unit_class.<locals>.Unit
        #r.dimensionality
        #<UnitsContainer({'[current]': -2, '[length]': 2, '[mass]': 1, '[time]': -3})> # Basis SI; die werden im endeffekt verglichen

        #self.log.info(r)
        #if pintObj[0][1].is_compatible_with(r):
        #    u=pintObj[0][1]
        #self.log.info(r)

  #      doc=self.nlp(text)
   #     for token in doc:
    #        output = " ".join(["("+token.text+" "+token.pos_+")" for token in doc if token.pos_ == 'NOUN' or token.pos_ == 'NUM'])     
     #   self.log.info(output)
        #self.log.info(str(text.split(' und ')))

    def write_variable(self, data, file):
        with self.file_system.open(file, "w") as my_file:
            my_file.write(json.dumps(data))  # use `json.loads` to do the reverse
    
    def load_formulas(self):
        input_file = open(join(dirname(__file__), 'formulas.yml'), "r")
        yaml_doc = yaml.load(input_file)
        return yaml_doc

    def load_unit_vocab(self): ### expand
        """

        register_vocabulary for ['durchmesser', 'radius', 'umfang']
        """
        for unit in self.init_units:
            self.register_vocabulary(unit, 'units')
        for key in self.wish_overview.keys():
            self.log.info("test load unit vocab"+str([self.wish_overview[key][1] for key in self.wish_overview.keys()]))
            self.register_vocabulary(self.wish_overview[key][1], 'tasks')

    @intent_handler(IntentBuilder("cal").one_of("tell_me", "replacement_word").optionally("calculate").
                    one_of("addition", "division", "multiplication", "subtraction", "net", "gross", "sale", "percent").build())
    def simple_calculate_handler(self, message):
        text = message.utterance_remainder()
        number = extract_number(text, lang=self.lang)
        #if number is (""):
        #    return False
        #if type(number) is int:
        self.utterance = message.data['utterance']
        self.calculate_worker(self.utterance, message)

    @intent_file_handler('formula.calculate.intent')
    def formul_handler(self, message):
        task = message.data.get('task')
        text = message.data.get('unitstr')
        number = extract_number(text, lang=self.lang)
        text = self.num_worker(text)
        self.log.info("found "+str(text)+" task "+str(task))
        #self.units_operator(self.units_converter(self.units_worker(text)))

    #@intent_handler(IntentBuilder("formul").one_of("tell_me", "replacement_word").optionally("calculate").
    #                one_of("units", "tasks").build())
    #def formul_calculate_handler(self, message):
    #    text = message.utterance_remainder()
    #    number = extract_number(text, lang=self.lang)
    #    text = self.num_worker(text)
    #    self.log.info("found "+text)
    #    self.units_operator(self.units_converter(self.units_worker(text)))     ######### work with formulas

    def calculate_worker(self, text, message):
        text = self.num_worker(text)
        self.log.info("found "+text)
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
        """[summary]

        Args:
            text ([type]): "wie ist der duchmesser bei 30 meter umfang"

        Returns:
            [type]: [description]
        """
        line = text.split()
        operator = None
        ### what is the net amount of 30 << swap "net amount" with "30" (bad fix)
        for nr, word in enumerate(line): 
            if self.voc_match(word, "from") : ### turn around with from
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
                ###
        text= " ".join(line)
        ###
        [line.pop(i) for i, word in enumerate(line) if self.voc_match(word, "replacement.word")] #schmeißt replacement words raus
        for word in line:
            #self.log.info("text1 "+text+" "+word)
            operator = self.oparator_match(word)
            if operator: ##### todo problem with "and from that"
                if operator == "from_that":
                    text = text.replace(word, ")")
                    text = "( "+text
                else:
                    text = text.replace(word, str(operator))
            self.log.info("after operator"+text)
        return text
    

    def units_worker(self, text):
        """[summary]

        Args:
            text ([str]): "wie ist der durchmesser bei 30 millimeter umfang"

        Returns:
            units ([dict]): {'diameter': [False, False], 'scope': [30.0, 'millimeter']}
        """
        ### extract units
        self.log.info("start unitworker"+str(text))
        line = text.split() 
        units = {}
        formula =[]
        for nr, unit in enumerate(line):
            if self.voc_match(unit, "from") : ### turn around with from
                if line[nr+2] in self.init_units or self.voc_match(line[nr+2], "units"):
                    line[nr+1], line[nr+2], line[nr], line[nr-1] = line[nr-1], line[nr], line[nr+2], line[nr+1]
                try:
                    if line[nr+3] in self.init_units or self.voc_match(line[nr+3], "units"):
                        line[nr+1], line[nr+2], line[nr], line[nr-1], line[nr+3] = line[nr-1], line[nr], line[nr+3], line[nr+2], line[nr+1]
                except:
                    pass
        ###
        self.log.info("after from "+str(line)) #
        for nr, unit in enumerate(line):
            if unit in [self.wish_overview[key][1] for key in self.wish_overview.keys()] or self.voc_match(unit, "tasks") or unit in self.init_units: ### formulas and unit
                formula = unit
                self.log.info("unit "+str(unit)+" "+str(nr))
                for key in self.wish_overview.keys():
                    if unit in self.wish_overview[key][1]:
                        formula = key
                        #if not line[nr-1] in self.init_units:
                        if line[nr-1] in self.init_units or self.voc_match(line[nr-1], "units"):
                            self.log.info("line "+line[nr-1])
                            u = nr-1
                            s = nr-2
                            try:
                                unit = self.units_value[line[u]] ### translate units to english
                            except:
                                pass
                            unit = unit.replace(" ", "") ##?
                            try:
                                number = float(line[s])
                            except:
                                number = False
                            self.log.info("testnumber "+str(number))
                            self.log.info("liste "+str(self.init_units)+ " unit "+unit)
                            units.update({formula : [number, line[u]]})
                        elif line[nr-2] in self.init_units or self.voc_match(line[nr-2], "units"):
                            u = nr-2 
                            s = nr-3
                            try:
                                unit = self.units_value[line[u]] ### translate units to english
                            except:
                                pass
                            unit = unit.replace(" ", "") ##?
                            try:
                                number = float(line[s])
                            except:
                                number = False
                            self.log.info("testnumber2 "+str(number))
                            units.update({formula : [number, line[u]]})
                        else:
                            u = nr-1
                            self.log.info("else "+str({formula : [False, False]}))
                            units.update({formula : [False, False]})
            if unit in self.init_units or self.voc_match(unit, "units"):
                unitexpander = []
                for uni in [self.wish_overview[key][0] for key in self.wish_overview.keys()]:
                    unitexpander.extend([uni, "milli"+uni, "centi"+uni, "deci"+uni, "micro"+uni, "nano"+uni, "kilo"+uni, "mega"+uni, "giga"+uni]) 
                #not unit in unitexpander:
                self.log.info("exclude"+str([self.wish_overview[key][0] for key in self.wish_overview.keys()])) ### only unit without formula
                if not unit in unitexpander:
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
                    self.log.info("self "+str({unit : [number, False]}))
                    units.update({unit : [number, False]})
        ###
        self.log.info("after unitworker"+str(units))
        return units
    
    def units_converter(self, units): ### todo make it better
        """[summary]

        Args:
            unit ([dict]): {'diameter': [False, False], 'scope': [30.0, 'millimeter']}

        Returns:
            units ([dict]): {"diameter": [false, false, "diameter", "*1"], "scope": [0.03, "meter", "millimeter", "/1000"]}
        """
        #factors = {}
        self.log.info("before unitconvertation "+str(units))
        for key, value in list(units.items()):
            val = value[0]
            unit = value[1]
            del units[key]
            if unit is False:
                key, akey, factor = self.factor_matcher(key)
                if not val is False:
                    self.log.info("bkey "+str(akey))
                    units.update({akey : [eval(str(val)+factor), str(value[1]), key, factor]}) ### calculate factor
                else:
                    self.log.info("unit2 "+str(akey))
                    units.update({akey : [val, value[1], key, factor]})
                #factors.update({akey : [key, factor]})
            else:
                unit, akey, factor = self.factor_matcher(unit)
                if not val is False:
                    self.log.info("akey "+str(akey))
                    units.update({key : [eval(str(val)+factor), str(akey), unit, factor]}) ### calculate factor
                else:
                    self.log.info("unit3 "+str(akey))
                    self.log.info("unit "+str(unit))
                    self.log.info("key "+str(key))
                    self.log.info("value "+str(value[1]))
                    units.update({key : [val, akey, unit, factor]})
                #factors.update({key : [unit, factor]})
            #units[akay] = [value, factor]
        self.log.info("after unit converter "+str(units))
        self.write_variable(units, "units") ############################################################################
        #self.log.info("factor after converter "+str(factors))
        return units

    def factor_matcher(self, key):
        for keyf, value in self.factors.items():
            if keyf in word:
                akey = word.replace(keyf, "")
                factor = value
                break
        else:
            factor = "*1"
            akey = key
        return key, akey, factor

    def oparator_match(self, word):
        for key, value in self.operators.items():
            if self.voc_match(word, key) is None:
                operator = value
                break
        else:
            operator=None
        return operator

    def units_shorter(self, unit): #### apsolete
        return {value[1]: value[0] for key, value in unit.items()}
        #return {value[1]: value[0] for value in unit.values()}

    def units_operator(self, units):
        """[summary]

        Args:
            units ([dict]): {"diameter": [False, False, "diameter", "*1"], "scope": [0.03, "meter", "millimeter", "/1000"]}
            or
            units ([dict]): {'ampere': [False, False, 'ampere', '*1'], 'volt': [0.04, 'False', 'millivolt', '/1000'], 'ohm': [30.0, 'False', 'ohm', '*1']}

        Returns:
            [type]: [description]
        """
        self.log.info("units_operator "+str(units))
        calculation = []
        result = []
        f = True
        while True:
            try:
                for key, whole in list(units.items()):
                    value = whole[0]
                    unit = whole[1]
                    self.log.info("test1 "+key)
                    if value is False: #### go to formulas here
                        self.log.info("test2"+key)
                        formulas = self.load_formulas()
                        #self.write_variable(formulas, "formulas_backup") #########################
                        self.log.info("formulas basic "+str(formulas))
                        self.log.info("wish"+str(self.wish_overview.keys()))
                        if key in self.wish_overview.keys():
                            self.log.info("test checko 1 "+str(formulas[self.wish_overview[key][0]]))
                            self.write_variable(str([line for line in formulas[self.wish_overview[key][0]]]), "saveformula")
                            result = exec(str([line for line in formulas[self.wish_overview[key][0]]]))
                            self.log.info("result: "+str(result))
                        else:
                            self.log.info("test checko 2"+str(formulas[key]))
                            self.write_variable(str(formulas[key]), "saveformula")
                        """for uni in formulas:
                            self.log.info("keys "+uni)
                            if key is not uni:
                                self.log.info("test check1"+str(formulas[key]))
                            else:
                                self.log.info("test check2"+str(formulas[key]))
                        if unit is False:
                            #pass
                            result = formula.switch(self.units_shorter(units), key) ###see class formula_switcher
                        else:
                            self.log.info("one "+str(formulas[formul][key]))
                            formel = self.formulas
                            #operation = getattr(switch, self.formulas[key][0])
                            #operation = "quadratmeter"
                            self.log.info("key "+key)
                            self.log.info("uni "+str(value))
                            self.log.info("formul "+str(formul))
                            exe = self.units_shorter(units)
                            self.log.info(str(exe[formul]))
                            file1 = open("/home/andreas/Downloads/myfile4.txt","a")#append mode 
                            file1.write(str(formulas[self.units_shorter(units)[unit]][key]))
                            file1.close() 
                            self.log.info("formulas second"+str(formulas))
                            self.log.info("formule "+ str(self.formulas))
                            self.log.info("end"+str(self.units_shorter(units))+"+"+str(self.formulas[key][0])+"."+str(key))
                            self.log.info("test keine ahnung"+str(formulas["meter"]))
                            self.log.info("test end"+str(formulas[str(self.units_shorter(units))][key]))
                            result = eval(str(formulas["meter"][key]))
                            #result = formula.switch(self.units_shorter(unit), self.formulas[key][0]+"."+key)
                            self.log.info("output "+str(result))
                        """
                break
            except KeyError as var:
                var = str(var)
                self.log.info("fail with "+var)
                units[var] = self.get_response("var.not.found", data={"var":str(var)})
                if self.voc_match(units[var], "cancel"):
                    return
                units[var] = extract_number(units[var], short_scale=False, ordinals=False,
                        lang=self.lang)     
        ### preparation the output
        name = False
        for key, whole in list(units.items()):
            value = whole[0]
            unit = whole[2]
            calc_factors = whole[3]
            akey = calc_factors[key][0] ### factors back
            if "/" in factor[key][1]:
                factor = calc_factors[key][1].replace("/", "*")
            elif "*" in calc_factors[key][1]:
                factor = calc_factors[key][1].replace("*", "/")
            if value is False:
                if isinstance(result, tuple): ##for force unit
                    self.log.info("test force unit")
                    name = result[1]
                    result = result[0]
                value = str(result)
                okey = akey
                self.log.info("value "+str(value)+" name "+str(name))
                try:
                    result = eval(str(value)+factor) ### factors back
                except:
                    self.exit_output()
                    return False
            else:
                value = eval(str(value)+str(factor))
                calculation.append(str(value)+" "+str(akey)+" ")
        calculation = " ".join(calculation)
        if name is False:
            result = (str(result)+" "+str(okey)+" ")
        else:
            result = (str(result)+" "+str(name)+" ") ### if force unit
        self.speak_dialog("result", data={"calculation":calculation, "result":result})
        self.gui.show_text(calculation+" = "+result)

    def oparator_calculator(self, text):
        calculation = text[0]
        result = round(eval(text[0]), 2)
        calculation = calculation.replace(".", ",")
        if self.lang == "de-de":
            result = str(result).replace(".", ",")
        self.speak_dialog("result", data={"calculation":calculation, "result":result})
        self.gui.show_text(calculation+" = "+result)
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
            except:
                self.exit_output()
        else:
            if text == None:
                self.exit_output()
                return False
        self.log.info("text "+str(text))
        return text

    def exit_output(self): ##### todo send it to fallback
        message = self.utterance
        self.log.info("send '"+message+"'")
        response  = self.get_response("fail")
        if response is None:
            self.log.info("calculating fail")
        else:
            self.calculate_worker(responce)

    def shutdown(self):
        super(Calculator, self).shutdown()

def create_skill():
    return Calculator()

from pint import UnitRegistry
from collections import OrderedDict
import re
ureg = UnitRegistry()


class pint_calculator():
    string = []
    units = []
    

    def translate_unit(self, unitname, translation):
        global string, splitted
    
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

    def calculate(self, units, string):
        splitted=string.lower().split(" ")
        #ruft translate_unit() auf wenn er eine übersetzbare Einheit findet
        patternlist=[]
        for word in splitted:
            for unit, trans in units.items():
                if re.match(r".*"+unit,word):
                    rx=translate_unit(unit, trans)
                    if re.match(r"^{.*}",rx): 
                        patternlist.append(rx)
                    else:
                        patternlist[-1]+=".*"+rx
                    break
        print(str(patternlist))


class formula_switcher():
    """old code

    Returns:
        [type]: [description]
    """
    units = {}
    def switch(self, unit, key):
        global units
        units = unit
        print("unit "+str(unit))
        default = "Incorrect"
        print("key "+str(key))
        return getattr("meter", "diameter", lambda: default)()
        #return self.formula_switcher.meter.diameter()
        #return getattr(self, key, lambda: default)()
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
    class meter():
        print("test1")
        def diameter(self):
            print("test2")
            if "radius" in units.keys():
                return units["radius"]*2 #### force unit meter
            elif "scope"  in units.keys():
                return (units["scope"]/(2*math.pi))*2
            elif "surface" in units.keys():
                radius = units["surface"]/math.pi
                return math.sqrt(radius)*2
        def radius(self):
            print("test3")
            if "diameter" in units.keys():
                return units["diameter"]/2
            elif "scope"  in units.keys():
                return units["scope"]/(2*math.pi)
            elif "surface" in units.keys():
                radius = units["surface"]/math.pi
                return math.sqrt(radius)
        def scope(self):
            print("test4")
            if "diameter" in units.keys():
                radius = units["diameter"]/2
                return 2*math.pi*radius
            elif "radius"  in units.keys():
                return 2*math.pi*units["radius"]
            elif "surface" in units.keys():
                result = units["surface"]/math.pi
                radius = math.sqrt(result)
                return 2*math.pi*radius
        def brakingdistance(self):
            if "kmh" in units.keys():
                return (units["kmh"]/10)*(units["kmh"]/10)
    class quadratmeter():
        def surface(self):
            print("test5")
            if "diameter" in units.keys():
                radius = units["diameter"]/2
                return math.pi*(radius**2)
            elif "radius"  in units.keys():
                return math.pi*(units["radius"]**2)
            elif "scope" in units.keys():
                radius = units["surface"]/(2*math.pi)
                return math.pi*(radius**2)
    ### breaking distance car



