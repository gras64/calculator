import re
from mycroft import MycroftSkill, intent_file_handler, intent_handler
from adapt.intent import IntentBuilder
from mycroft.util.parse import extract_number, normalize, extract_numbers
from mycroft.util.format import pronounce_number, nice_date, nice_time

_author__ = 'gras64'

class Calculator(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        self.tax = self.settings.get('tax') \
            if self.settings.get('tax') else "9.3"
        self.sale = self.settings.get('sale') \
            if self.settings.get('sale') else "30"
        self.log.info("boot")
    
    @intent_handler(IntentBuilder("cal").one_of("tell_me", "replacement_word").optionally("calculate").
                    one_of("addition", "division", "multiplication", "subtraction").build())
    def calculate_handler(self, message):
            self.log.info("boot") #require("number").
            text = message.utterance_remainder()
            number = extract_number(text, lang=self.lang)
            #if type(number) is int:
            self.calculate_worker(message.data['utterance'])

    def calculate_worker(self, text):
        text = self.num_worker(text)
        self.log.info("found "+text)
        text = self.oparator_worker(text)
        text = self.num_cleaner(text)
        text = self.oparator_validator(text)
        text = self.oparator_calculator(text)


    def num_worker(self, line): ## translate numbers to int
        num = ""
        number = ""
        if not extract_numbers(line, lang=self.lang) == []:
            num = extract_numbers(line, short_scale=False, ordinals=False,
                        lang=self.lang)
        num = re.sub(r'(\.0)', '', str(num))
        num = re.findall(r'\d+', num)
        if not num is False:
            for item in num:
                #print("item #"+item)
                if not pronounce_number(int(item), lang=self.lang, short_scale=True) ==[]:
                    number = pronounce_number(int(item), lang=self.lang, short_scale=True)
                else:
                    number = ""
                line = line.replace(number, str(item))
        return line

    def num_cleaner(self, text):
        text = re.sub("[^0-9/* +-]", "", text) #delete text
        text = re.findall(r'[0-9][0-9/* +-]+[0-9]', text) # only operator and number
        return text
        #* 4 + 5 / 7 to  4 + 5 / 7

    def oparator_worker(self, text): ## detect operators and replace
        line = text
        operator = None
        for word in line.split():
            #self.log.info("text1 "+text+" "+word)
            if self.oparator_match(word):
                for s in line.split():
                    if self.voc_match(s, "replacement_word"):
                        text = text.replace(s, str(word))
            operator = self.oparator_match(word)
            if not operator is None:
                text = text.replace(word, str(operator))
        return text
        
    def oparator_match(self, word):
        if self.voc_match(word, "addition"):
            operator = "+"
        elif self.voc_match(word, "subtraction"):
            operator = "-"
        elif self.voc_match(word, "multiplication"):
            operator = "*"
        elif self.voc_match(word, "division"):
            operator = "/"
        else:
            operator = None
        return operator

    def oparator_calculator(self, text):
        calculation = text[0]
        result = eval(text[0])
        self.speak_dialog("result", data={"calculation":calculation, "result":result})
        self.log.info(eval(text[0]))
        pass

    def oparator_validator(self, text): #### todo
        return text
        pass


    def gross_net(self, message):
        self.speak("test")

    def shutdown(self):
        super(Calculator, self).shutdown()

def create_skill():
    return Calculator()

