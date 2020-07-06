# <img src='https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/calculator.svg' card_color='#000000' width='50' height='50' style='vertical-align:bottom'/> Calculator
a not so simple calculator skill for Mycroft AI as an alternative to wolfram alpha

## About
With this skill you can do a lot of arithmetic operations. you can also use formulas like ohm's law. the skill supports the factors of units, formulas brackets, net and gross as well as sales price and calculations of any length "theoretically".in the new set version, the skill can also calculate the units back to their original form.

possible factors are: giga, mega, kilo, centi, deci, milli, micro and nano.

## Examples
* "what is 12 and 2.4 and 6.2 and 12.5"
* "addiere 4 and 5 from that gross" 
* "divide 600 by 2 from that net"
* "divide Bracket on 9 and 3 Bracket off and 2"
* "what is 9 times 72 from that sale"
* "multiply 2 with 3"
* "what is 5 minus 4"
* "subtract 7 with 6"
* "what is ohm from 40 ampere and 60 volt"
* "what is tension from 40 milliampere and 60 millivolt"
* "what is the breaking point at 130 kmh"
* ....... 

## Credits
gras64

## Category
Productivity

## Tags
#'calculation

## Development
I designed a system that is very easy to expand and expand and is very flexible

### add units
you only have to create new formulas the associated units are created independently with the factors, in gigawatts, megawatts, kilowatts, milliwatts "Enter" microwatts, nanowatts, centiwatts, deciwatts. A definition with the name of the unit you are looking for must be created under formula_switcher. then a formula like in the example with ohm's law. 

if you want to set additional triggers you can also use units.voc and units.value for the translation. for example to make "volt" out of "voltage"

### add formulas
if you want to add new formulas see my examples below "#### add your formulas here".

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

### Todo
* edit before calculation
* formulate more
* much more
