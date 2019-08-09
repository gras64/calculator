from mycroft import MycroftSkill, intent_file_handler
from mycroft.util.parse import extract_number

class Calculator(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)
        addition_intent = IntentBuilder("calculate").
            require("numberone").require("operationone").
            require("numbertwo").
            optionally("operationtwo").build()
        self.register_intent(addition_intent,
                             self.handle_addition_intent)

    def handle_hello_world_intent(self, message):
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


    def shutdown(self):
        super(Calculator, self).shutdown()

def create_skill():
    return Calculator()

