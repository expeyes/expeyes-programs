# -*- coding: utf-8 -*-

"""
This module defines a set of widgets able to interact with an expeyes-jr
box. The profile of all widget functions is: first parameter, an instance
of EyesServer, second paramter, a keyword directory coming from a GET or 
a POST dataset; returns HTML code as a unicode string.
"""

"""
@var adc_list a list of pairs label, number useful to call
expeyes-jr's primitive getvoltage()
"""
adc_list=[
    ("Analog Comparator output", 0), 
    ("A1", 1),
    ("A2", 2),
    ("IN1", 3),
    ("IN2", 4),
    ("SEN", 5),
    ("SQR1 readback", 6),
    ("SQR2 readback", 7),
    ("SQR1 output", 8),
    ("SQR2 output", 9),
    ("OD1 output", 10),
    ("CCS output control", 11),
    ("PVS readback", 12),
    ]

def allADCwidget(eserver, **kw):
    """
    creates a widget to display the voltage at a choosen ADC input
    @param eserver an instance of EyesServer
    @param kw a dictionary of parameter->value records; this widget will
    be activated when the dictionary contains the keyword "adc" with an
    integer value between 0 and 12.
    @return HTML code as a unicode string
    """
    try:
        adc=kw["adc"]
        n=int(adc)
    except:
        n=-1
    if eserver.ok and n in range(len(adc_list)):
        adc_name=""
        for label, val in adc_list:
            if str(val)==adc:
                adc_name=label
        v="Voltage at {name} = {val} V".format(
            name=adc_name, 
            val=eserver.p.get_voltage(n))
    else:
        v=""
    return """
{select} 
<div id="voltage" style="display:inline;">{voltage}</div>
""".format(voltage=v, 
            select=selectfield(
               "adc",
               [("Select an ADC", -1)] + adc_list,
               extra="onchange='submit();'"
               ))

def allADCwidgetJSON(eserver, **kw):
    """
    !!!! TO BE REWORKED !!!!! this one should need no **kw since it uses a $.getJSON call !!!
    creates a widget to display the voltage at a choosen ADC input
    @param eserver an instance of EyesServer
    @param kw a dictionary of parameter->value records; this widget will
    be activated when the dictionary contains the keyword "adc" with an
    integer value between 0 and 12.
    @return HTML code as a unicode string
    """
    try:
        adc=kw["adc"]
        n=int(adc)
    except:
        n=-1
    if eserver.ok and n in range(len(adc_list)):
        adc_name=""
        for label, val in adc_list:
            if str(val)==adc:
                adc_name=label
        v="Voltage at {name} = {val} V".format(
            name=adc_name, 
            val=eserver.p.get_voltage(n))
    else:
        v=""
    return """
{select} 
<div id="voltage" style="display:inline;">{voltage}</div>
""".format(voltage=v, 
            select=selectfield(
               "adc",
               [("Select an ADC", -1)] + adc_list,
               extra="onchange='submit();'"
               ))


def selectfield(name, dico, extra=""):
    """
    create a SELECT element with a dictionary of labels and values
    eventually selecting a default label
    @param name the name attribute of the select element
    @param dico a list of pairs (label, value)
    @param extra source for extra attributes
    @return HTML code
    """
    result="<select name='{name}' {extra}>".format(name=name, extra=extra)
    for label,val in dico:
        result+= "<option value='{val}'>{label}</option>".format(
                label=label, val=val)
    result += "</select>"
    return result

