from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.parse import extract_number

_author__ = 'gras64'

class Calculator(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    def initialize(self):
        self.tax = self.settings.get('tax') \
            if self.settings.get('tax') else "9.3"
        self.sale = self.settings.get('sale') \
            if self.settings.get('sale') else "30"

    @intent_file_handler('addition.intent')
    def addition_intent(self, message):
        if message.data.get("numberone"):
            numberone = message.data.get("numberone")
            #numberone = 5
            numberone = extract_number(numberone)
            numberone = int(numberone)
            self.speak(numberone)
            if type(numberone) != int:
                self.speak_dialog("pleasenumbers")
        else:
            self.speak_dialog("fail")
        if message.data.get("numbertwo"):
            numbertwo = message.data.get("numbertwo")
            #numbertwo = 7
            numbertwo = extract_number(numbertwo)
            numbertwo = int(numbertwo)
            self.speak(numbertwo)
            if type(numbertwo) != int:
                self.speak_dialog("pleasenumbers")
        else:
            self.speak_dialog("fail")
        answer = numberone + numbertwo
        #answer = 3
        self.speak_dialog("calculator",
                            data={"answer": answer})

    @intent_file_handler('division.intent')
    def division_intent(self, message):
        if message.data.get("numberone"):
            numberone = message.data.get("numberone")
            #numberone = 5
            numberone = extract_number(numberone)
            numberone = int(numberone)
            self.speak(numberone)
            if type(numberone) != int:
                self.speak_dialog("pleasenumbers")
        else:
            self.speak_dialog("fail")
        if message.data.get("numbertwo"):
            numbertwo = message.data.get("numbertwo")
            #numbertwo = 7
            numbertwo = extract_number(numbertwo)
            numbertwo = int(numbertwo)
            self.speak(numbertwo)
            if type(numbertwo) != int:
                self.speak_dialog("pleasenumbers")
        else:
            self.speak_dialog("fail")
        answer = numberone / numbertwo
        #answer = 3
        self.speak_dialog("calculator",
                            data={"answer": answer})

    @intent_file_handler('multiplikation.intent')
    def multiplication_intent(self, message):
        if message.data.get("numberone"):
            numberone = message.data.get("numberone")
            #numberone = 5
            numberone = extract_number(numberone)
            numberone = int(numberone)
            self.speak(numberone)
            if type(numberone) != int:
                self.speak_dialog("pleasenumbers")
        else:
            self.speak_dialog("fail")
        if message.data.get("numbertwo"):
            numbertwo = message.data.get("numbertwo")
            #numbertwo = 7
            numbertwo = extract_number(numbertwo)
            numbertwo = int(numbertwo)
            self.speak(numbertwo)
            if type(numbertwo) != int:
                self.speak_dialog("pleasenumbers")
        else:
            self.speak_dialog("fail")
        answer = numberone * numbertwo
        #answer = 3
        self.speak_dialog("calculator",
                            data={"answer": answer})

    @intent_file_handler('subtraktion.intent')
    def subtraktion_intent(self, message):
        if message.data.get("numberone"):
            numberone = message.data.get("numberone")
            #numberone = 5
            numberone = extract_number(numberone)
            numberone = int(numberone)
            self.speak(numberone)
            if type(numberone) != int:
                self.speak_dialog("pleasenumbers")
        else:
            self.speak_dialog("fail")
        if message.data.get("numbertwo"):
            numbertwo = message.data.get("numbertwo")
            #numbertwo = 7
            numbertwo = extract_number(numbertwo)
            numbertwo = int(numbertwo)
            self.speak(numbertwo)
            if type(numbertwo) != int:
                self.speak_dialog("pleasenumbers")
        else:
            self.speak_dialog("fail")
        answer = numberone - numbertwo
        #answer = 3
        self.speak_dialog("calculator",
                            data={"answer": answer})

    @intent_handler(IntentBuilder("grossnet").require("tell_me").optionally("net").
                    optionally("gross").optionally("purchase").optionally("sale").require("calculator"))
    def gross_net(self, message):
        self.speak("test")

    def shutdown(self):
        super(Calculator, self).shutdown()

def create_skill():
    return Calculator()

