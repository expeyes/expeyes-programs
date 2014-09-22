# -*- coding: utf-8 -*-

"""
Set of constants used for programming expEYES-Jr
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

def menuADC(es, **kw):
    """
    callback function to measure a voltage from an ADC
    @param es an EyesServer instance
    @param kw a keyword dictionary: the key "val" identifies 
    an ADC of expeyes-jr box
    @return a dictionary voltage -> value
    """
    es.recheck()
    n=int(kw["val"])
    if (not es.ok) or n not in range(13):
        return
    kw["voltage"]=es.p.get_voltage(n)
    return kw
