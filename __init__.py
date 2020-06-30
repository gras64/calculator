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
            text = self.units_converter(text)
            self.units_operator(text)
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
            if self.voc_match(unit, "units"):
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
        for item in text.items():
            item = list(item)
            if "milli" in item[0]:
                del text[item[0]]
                if not item[1] is False:
                    item[1] = item[1]/1000
                item[0] = item[0].replace("milli", "")
                text.update({item[0] : item[1]})
            elif "centi" in item[0]:
                del text[item[0]]
                if not item[1] is False:
                    item[1] = item[1]/100
                item[0] = item[0].replace("centi", "")
                text.update({item[0] : item[1]})
            elif "deci" in item[0]:
                del text[item[0]]
                if not item[1] is False:
                    item[1] = item[1]/10
                item[0] = item[0].replace("deci", "")
                text.update({item[0] : item[1]})
            elif "micro" in item[0]:
                del text[item[0]]
                if not item[1] is False:
                    item[1] = item[1]/1000000
                item[0] = item[0].replace("micro", "")
                text.update({item[0] : item[1]})
            elif "nano" in item[0]:
                del text[item[0]]
                if not item[1] is False:
                    item[1] = item[1]/1000000
                item[0] = item[0].replace("nano", "")
                text.update({item[0] : item[1]})
            elif "kilo" in item[0]:
                del text[item[0]]
                if not item[1] is False:
                    item[1] = item[1]*1000
                item[0] = item[0].replace("kilo", "")
                text.update({item[0] : item[1]})
            elif "mega" in item[0]:
                del text[item[0]]
                if not item[1] is False:
                    item[1] = item[1]*100000
                item[0] = item[0].replace("mega", "")
                text.update({item[0] : item[1]})
            elif "giga" in item[0]:
                del text[item[0]]
                if not item[1] is False:
                    item[1] = item[1]*1000000000
                item[0] = item[0].replace("giga", "")
                text.update({item[0] : item[1]})
        self.log.info("after unit converter "+str(text))
        return text
    
    def units_operator(self, unit): ### add units calculation here
        
        calculation = []
        result = []
        f = True
        while True:
            try:
                for item in unit.items():
                    item = list(item)
                    if item[1] is False: #### add your formulas here
                        ### Ohm's law
                        if "ohm" in item[0]:
                            result = unit["volt"]/unit["ampere"]
                            break
                        elif "volt" in item[0]:
                            result = unit["ohm"]*unit["ampere"]
                            break
                        elif "ampere" in item[0]:
                            result = unit["volt"]/unit["ohm"]
                            break
                        elif "watt" in item[0]:
                            if "volt"  in unit.keys() and "ampere" in unit.keys():
                                result = unit["volt"]*unit["ampere"]
                            elif "ampere" in unit.keys() and "ohm" in unit.keys():
                                result = (unit["ampere"]**2)*unit["ohm"]
                            elif "volt" in unit.keys() and "ohm" in unit.keys():
                                result = (unit["volt"]**2)*unit["ohm"]
                            break
                        ### circle
                        if "diameter" in item[0]:
                            if "radius" in unit.keys():
                                result = unit["radius"]*2
                            elif "scope"  in unit.keys():
                                result = (unit["scope"]/(2*math.pi))*2
                            elif "surface" in unit.keys():
                                result = unit["surface"]/math.pi
                                result = math.sqrt(result)*2
                            break
                        elif "radius" in item[0]:
                            if "diameter" in unit.keys():
                                result = unit["diameter"]/2
                            elif "scope"  in unit.keys():
                                result = unit["scope"]/(2*math.pi)
                            elif "surface" in unit.keys():
                                result = unit["surface"]/math.pi
                                result = math.sqrt(result)
                            break
                        #elif "scope" in item[0]: ###
                        #    if "diameter" in unit.keys():
                        #        result = unit["diameter"]/2
                        #    elif "radius"  in unit.keys():
                        #        result = unit["scope"]/(2*math.pi)
                        #    elif "surface" in unit.keys():
                        #        result = unit["surface"]/math.pi
                        #        result = math.sqrt(result)
                        #     break
                        #
                        ### breaking distance car
                        elif "brakingdistance" in item[0]:
                            result = (unit["kmh"]/10)*(unit["kmh"]/10)
                            break
                        else:
                            break
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
        for item in unit.items():
            if item[1] is False:
                item = list(item)
                item[1] = str(result)
                result = item
            else:
                calculation.append(str(item[1])+" "+str(item[0])+" ")
        calculation = " ".join(calculation)
        result = (str(result[1])+" "+str(result[0])+" ")
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


    def gross_net(self, message):
        self.speak("test")

    def shutdown(self):
        super(Calculator, self).shutdown()

def create_skill():
    return Calculator()

