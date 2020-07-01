# <img src='https://raw.githack.com/FortAwesome/Font-Awesome/master/svgs/solid/calculator.svg' card_color='#000000' width='50' height='50' style='vertical-align:bottom'/> Calculator
a not so simple calculator skill for Mycroft AI as an alternative to wolfram alpha

## About
With this skill you can do a lot of arithmetic operations. you can also use formulas like ohm's law. the skill supports the conversion of units, formulas brackets, net and gross as well as sales price and calculations of any length "theoretically".

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
if you want to set up other units you have to specify them in the file "units.voc" and translate them into "units.value" in English. In addition, you should enter in the "units.voc" all forms like "gigawatt, megawatt, kilowatt, milliwatt" Enter "microwatt".

### add formulas
if you want to add new formulas see my examples below "#### add your formulas here".

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

### Todo
* edit before calculation
* formulate more
* much more
