import wx

def call_back_open(frame,filename):
    """
    make a custom callback function
    :param frame: the main frame of Microhope's application
    :param filename: the name of a file which the main frame will open
    """
    def cb(event):
        """
        This callback function will open a file from the read-only
        directory /usr/share/microhope/microhope, while keeping
        the initial directory of the application.
        """
        frame.example_open(filename)
        return
    return cb

def add_examples(mh_frame):
    """
    add some examples
    :param mh_frame: the main frame of Microhope's application
    """
    submenu = mh_frame.i_file_sub
    examples = [
        ("blink.c",_('Blinks a LED on PB0')),
        ("adc.c",_('Reads ADC channel 0 and diplays the result on the LCD')),
        ('adc-loop.c',_('Reads ADC channel 0 and diplays the result on the LCD in loop')),
        ("adc-v2.c",_('ADC -version 2')),
        ("adc-v3.c",_('ADC -version 3')),
        ("copy.c",_('Copies a PORTA and display it on PORTB')),
        ("copy2.c",_('Copy 2')),
        ('copy3.c',_('Copy 3')),
        ("echo.c","echo.c"),
        ("echo-v2.c","echo-v2.c"),
        ("pwm-tc0.c",_("PWM-tc0 version 1")),
        ("h-bridge.c",_("H-Bridge Controlling motor")),
        ("pwm-tc0-v2.c",_("PWM tc0 version 2")),
        ("cro.c",_("To make microHOPE as small CRO")),
        ("cro2.c",_("To make microHOPE as small CRO (version 2)")),
        ('hello.c',_('Print message in LCD')),
        ("hello-blink.c",_("Blinking messages in LCD")),
    ]
    starting_id = 400
    for i, (filename, helpstring) in enumerate(examples, start=400):
        submenu.Append(i, filename,helpstring,kind = wx.ITEM_RADIO)
        mh_frame.Bind(wx.EVT_MENU, call_back_open(mh_frame, filename), id=i)
    return
    
