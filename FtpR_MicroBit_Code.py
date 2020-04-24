'''
Python (and MicroPython) uses modules to keep reusable bits of code (classes, methods...)
that we can access using the "from" keyword
With "microbit import *" We are saying to “load all the code from the microbit module”
(the * sign is used to indicate “everything”).

The microbit module contains all the functions and methods we need to communicate to the micro:bit hardware,
such as the LED display, buttons or the I/O pins.

We also import the math module to perform some specific math functions further in the code.
'''
from microbit import *
import math

'''
Define the functions that send the MIDI data OUT
Each function defines a specific midi event and a midi channel
The parameters of the functions are: the channel number;
the MIDI note number, and the velocity
'''
def midiNoteOn(chan, n, vel):

    # "MIDI_NOTE_ON" variable represents the status byte (the hexadecimal value)
    # 9 is the MIDI event (Note ON) and 0 is the channel we send the signal to (ch.1)
    MIDI_NOTE_ON = 0x90

    # If parameters values are not appropriate, the function stops without sending any message
    if chan > 15:
        return
    if n > 127:
        return
    if vel > 127:
        return

    # The message from hexadecimal and decimal values is translated in binary, to be sent as 3 bytes.
    # The first byte is the Status byte (event and channel); the "|" bitwise "OR" operation ensures
    # that if we specify a channel in the parameters the binary message will be sent to that accordingly.
    # The second and third byte are the two data bytes (note number and velocity)
    msg = bytes([MIDI_NOTE_ON | chan, n, vel])

    # "uart" object initiated on the startup has a method ".write"
    # that allows us to write/send the MIDI data binary message to the MIDI bus
    uart.write(msg)

# For the next two functions the only difference is the midi Event
def midiNoteOff(chan, n, vel):
    MIDI_NOTE_OFF = 0x80
    if chan > 15:
        return
    if n > 127:
        return
    if vel > 127:
        return
    msg = bytes([MIDI_NOTE_OFF | chan, n, vel])
    uart.write(msg)


def midiControlChange(chan, n, value):
    MIDI_CC = 0xB0
    if chan > 15:
        return
    if n > 127:
        return
    if value > 127:
        return
    msg = bytes([MIDI_CC | chan, n, value])
    uart.write(msg)

'''
We define on the startup to initialise the uart object bus and set the proper values for MIDI transmission
The object is used in the previous functions for the message sending (".write")
The only value that depends on the circuit design is "tx" value;
it depends on which pin we connected the data line of the MIDI connector to (in our case "pin0")
'''
def Start():
    uart.init(baudrate=31250, bits=8, parity=None, stop=1, tx=pin0)

# On startup we initiate the variables
Start()
lastA = False
lastB = False
lastC = False
last_pot = 0

# To each button is assigned a specific Midi note
BUTTON_A_NOTE = 36
BUTTON_B_NOTE = 39
BUTTON_C_NOTE = 43

'''
We start a digital clock inside an infinite while loop.
During the time the microprocessor will be ON, it will check
every 10ms (time range set as the parameter of the "sleep" function at the bottom)
if there is a condition satisfying any of the statements.
'''
while True:

    '''
    As soon as button a, b or c are pressed, the microprocessor sends a NoteON event
    to the respective Notes, and stores the last state of the button on the variable "lastA" /B/C.
    The process checks every 10 ms if the state of the button is changed.
    If so, it sends the NoteOFF event related to the button that changed its state, and so on.
    '''
    a = button_a.is_pressed()
    b = button_b.is_pressed()
    c = pin1.is_touched()
    pot = pin2.read_analog()
    if a is True and lastA is False:
        midiNoteOn(0, BUTTON_A_NOTE, 127)
        display.show("a")
    elif a is False and lastA is True:
        midiNoteOff(0, BUTTON_A_NOTE, 127)
        display.clear()
    if b is True and lastB is False:
        midiNoteOn(0, BUTTON_B_NOTE, 127)
        display.show("b")
    elif b is False and lastB is True:
        midiNoteOff(0, BUTTON_B_NOTE, 127)
        display.clear()
    if c is True and lastC is False:
        midiNoteOn(0, BUTTON_C_NOTE, 127)
        display.show("c")
    elif c is False and lastC is True:
        midiNoteOff(0, BUTTON_C_NOTE, 127)
        display.clear()
    lastA = a
    lastB = b
    lastC = c

    '''
    If the potentiometer value changes within 10ms
    we send to channel 0 a control change event of an Undefined Control Function (n=23)
    with the value represented by the velocity variable.
    To the Undefined Control Function will be later assigned a specific role in the PD Patch.
    The value sent is an intereger, result of the floor function
    that scales the potentiometer range from 0-1024 to a range from 0-126.
    '''
    if last_pot != pot:
        velocity = math.floor(pot / 1024 * 127)
        midiControlChange(0, 23, velocity)
        last_pot = pot

    sleep(10)