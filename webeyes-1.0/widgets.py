# -*- coding: utf-8 -*-

"""
This module defines a set of widgets able to interact with an expeyes-jr
box. The profile of all widget functions is: first parameter, an instance
of EyesServer, second paramter, a keyword directory coming from a GET or 
a POST dataset; returns HTML code as a unicode string.
"""

from eyesJr import adc_list

def menuADC(eserver, **kw):
    """
    !!!! TO BE REWORKED !!!!! this one should need no **kw since it uses a $.getJSON call !!!
    creates an HTML widget to display the voltage at a choosen ADC input
    this widget features a roll-down menu and a display for measurements
    @param eserver an instance of EyesServer
    @param kw a dictionary of parameter->value records; this widget will
    be activated when the dictionary contains the keyword "adc" with an
    integer value between 0 and 12 (number of an ADC entry of eyes-jr)
    @return HTML code as a unicode string
    """
    return """
{select} 
<div id="voltage" style="display:inline;"></div>
""".format(select=selectfield(
               [("Select an ADC", -1)] + adc_list,
               extra="onchange='adcWjson(this);'"
               ))


def selectfield(dico, extra=""):
    """
    create a SELECT element with a dictionary of labels and values
    eventually selecting a default label
    @param dico a list of pairs (label, value)
    @param extra source for extra attributes
    @return HTML code
    """
    result="<select {extra}>".format(extra=extra)
    for label,val in dico:
        result+= "<option value='{val}'>{label}</option>".format(
                label=label, val=val)
    result += "</select>"
    return result

