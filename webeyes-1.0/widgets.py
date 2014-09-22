# -*- coding: utf-8 -*-

"""
This module defines a set of widgets able to interact with an expeyes-jr
box. The profile of all widget functions is: first parameter, an instance
of EyesServer, second paramter, a keyword directory coming from a GET or 
a POST dataset; returns HTML code as a unicode string.
"""

from eyesJr import adc_list

def menuADC(eserver):
    """
    creates an HTML widget to display the voltage at a choosen ADC input.
    This widget features a roll-down menu and a display for measurements
    @param eserver an instance of EyesServer
    @return HTML code as a unicode string
    """
    return """
    <fieldset id="menuadc" class="widget">
      <legend>Measuring the voltage from an ADC entry</legend>
      {select} 
      <div class="voltage" style="display:inline;"></div>
    </fieldset>
""".format(select=selectfield(
               [("Select an ADC", -1)] + adc_list,
               extra="title='Modifiy the option to trigger one measurement' onchange='menuADC(this);'"
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

