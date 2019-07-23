from mycroft import MycroftSkill, intent_file_handler


class Calculator(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_file_handler('calculator.intent')
    def handle_calculator(self, message):
        self.speak_dialog('calculator')


def create_skill():
    return Calculator()

