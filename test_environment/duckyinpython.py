# License : GPLv2.0
# copyright (c) 2023  Dave Bailey
# Author: Dave Bailey (dbisu, @daveisu)


import time
import digitalio
from digitalio import DigitalInOut, Pull
from adafruit_debouncer import Debouncer
import board
from board import *
import pwmio
import asyncio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.mouse import Mouse

# instance of mouse
mouse = Mouse(usb_hid.devices)

# comment out these lines for non_US keyboards
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS as KeyboardLayout
from adafruit_hid.keycode import Keycode

# define keyboard(accidentally deleted)
kbd = Keyboard(usb_hid.devices)
layout = KeyboardLayout(kbd)

# uncomment these lines for non_US keyboards
# replace LANG with appropriate language
#from keyboard_layout_win_LANG import KeyboardLayout
#from keycode_win_LANG import Keycode

duckyCommands = {
    'WINDOWS': Keycode.WINDOWS, 'GUI': Keycode.GUI,
    'APP': Keycode.APPLICATION, 'MENU': Keycode.APPLICATION, 'SHIFT': Keycode.SHIFT,
    'ALT': Keycode.ALT, 'CONTROL': Keycode.CONTROL, 'CTRL': Keycode.CONTROL,
    'DOWNARROW': Keycode.DOWN_ARROW, 'DOWN': Keycode.DOWN_ARROW, 'LEFTARROW': Keycode.LEFT_ARROW,
    'LEFT': Keycode.LEFT_ARROW, 'RIGHTARROW': Keycode.RIGHT_ARROW, 'RIGHT': Keycode.RIGHT_ARROW,
    'UPARROW': Keycode.UP_ARROW, 'UP': Keycode.UP_ARROW, 'BREAK': Keycode.PAUSE,
    'PAUSE': Keycode.PAUSE, 'CAPSLOCK': Keycode.CAPS_LOCK, 'DELETE': Keycode.DELETE,
    'END': Keycode.END, 'ESC': Keycode.ESCAPE, 'ESCAPE': Keycode.ESCAPE, 'HOME': Keycode.HOME,
    'INSERT': Keycode.INSERT, 'NUMLOCK': Keycode.KEYPAD_NUMLOCK, 'PAGEUP': Keycode.PAGE_UP,
    'PAGEDOWN': Keycode.PAGE_DOWN, 'PRINTSCREEN': Keycode.PRINT_SCREEN, 'ENTER': Keycode.ENTER,
    'SCROLLLOCK': Keycode.SCROLL_LOCK, 'SPACE': Keycode.SPACE, 'TAB': Keycode.TAB,
    'BACKSPACE': Keycode.BACKSPACE,
    'A': Keycode.A, 'B': Keycode.B, 'C': Keycode.C, 'D': Keycode.D, 'E': Keycode.E,
    'F': Keycode.F, 'G': Keycode.G, 'H': Keycode.H, 'I': Keycode.I, 'J': Keycode.J,
    'K': Keycode.K, 'L': Keycode.L, 'M': Keycode.M, 'N': Keycode.N, 'O': Keycode.O,
    'P': Keycode.P, 'Q': Keycode.Q, 'R': Keycode.R, 'S': Keycode.S, 'T': Keycode.T,
    'U': Keycode.U, 'V': Keycode.V, 'W': Keycode.W, 'X': Keycode.X, 'Y': Keycode.Y,
    'Z': Keycode.Z, 'F1': Keycode.F1, 'F2': Keycode.F2, 'F3': Keycode.F3,
    'F4': Keycode.F4, 'F5': Keycode.F5, 'F6': Keycode.F6, 'F7': Keycode.F7,
    'F8': Keycode.F8, 'F9': Keycode.F9, 'F10': Keycode.F10, 'F11': Keycode.F11,
    'F12': Keycode.F12, 'MOUSE': {'action': 'MOVE', 'x': 0, 'y': 0, 'z': 0},
    'CLICK': {'action': 'CLICK'}, 'RIGHT_CLICK': {'action': 'RIGHT_CLICK'},
    'MIDDLE_CLICK': {'action': 'MIDDLE_CLICK'},
}

# ex: "MOUSE MOVE -100 0" moves the mouse 100 pixels left.
# for clicking: "MOUSE <insert click type here>"
# there is either: "CLICK", "MIDDLE_CLICK", or "RIGHT_CLICK"
def runMouseCommand(command):
    action = command['action']
    if action == 'MOVE':
        mouseX = int(command.get('x', 0))
        mouseY = int(command.get('y', 0))
        mouse.move(x=mouseX, y=mouseY)
    elif action == 'CLICK':
        mouse.click(mouse.LEFT_BUTTON)
    elif action == 'RIGHT_CLICK':
        mouse.click(mouse.RIGHT_BUTTON)
    elif action == 'MIDDLE_CLICK':
        mouse.click(mouse.MIDDLE_BUTTON)

def convertLine(line):
    newline = []
    mouse_command = {'action': ''}

    # loop on each key - the filter removes empty values
    for key in filter(None, line.split(" ")):
        key = key.upper()

        # MOUSE command check
        if key == 'MOUSE':
            mouse_command['action'] = ''
            continue  # continue with MOUSE command
        elif key in {'MOVE', 'CLICK', 'RIGHT_CLICK', 'MIDDLE_CLICK'}:
            mouse_command['action'] = key
            # add coords to MOVE command
            if key == 'MOVE':
                if len(newline) >= 2:
                    try:
                        mouse_command['x'] = int(newline[-2])
                        mouse_command['y'] = int(newline[-1])
                        runMouseCommand(mouse_command)
                        continue
                    except ValueError:
                        print(f"Invalid MOUSE MOVE command: Invalid coordinates - {newline[-2]} {newline[-1]}")
                        continue
            # handle other mouse commands here
            elif key == 'CLICK':
                mouse_command['action'] = 'CLICK'
                runMouseCommand(mouse_command)
            elif key == 'RIGHT_CLICK':
                mouse_command['action'] = 'RIGHT_CLICK'
                runMouseCommand(mouse_command)
            elif key == 'MIDDLE_CLICK':
                mouse_command['action'] = 'MIDDLE_CLICK'
                runMouseCommand(mouse_command)
        else:
            # find the keycode for the command in the list
            command_keycode = duckyCommands.get(key, None)
            if command_keycode is not None:
                # if it exists in the list, use it
                newline.append(command_keycode)
            elif hasattr(Keycode, key):
                # if it's in the Keycode module, use it (allows any valid keycode)
                newline.append(getattr(Keycode, key))
            else:
                # if it's not a known key name, show the error for diagnosis
                print(f"Unknown key: <{key}>")

    return newline

def runScriptLine(line):
    for k in line:
        if isinstance(k, dict):
            runMouseCommand(k)
        else:
            kbd.press(k)
            kbd.release_all()

def sendString(line):
    layout.write(line)

def parseLine(line):
    global defaultDelay
    mouse_command = {'action': '', 'x': 0, 'y': 0}

    if line.startswith("REM"):
        # ignore ducky script comments
        pass
    elif line.startswith("DELAY"):
        time.sleep(float(line[6:]) / 1000)
    elif line.startswith("STRING"):
        sendString(line[7:])
    elif line.startswith("PRINT"):
        print("[SCRIPT]: " + line[6:])
    elif line.startswith("IMPORT"):
        runScript(line[7:])
    elif line.startswith("DEFAULT_DELAY") or line.startswith("DEFAULTDELAY"):
        defaultDelay = int(line.split()[-1]) * 10
    elif line.startswith("LED"):
        if led.value:
            led.value = False
        else:
            led.value = True
    elif line.startswith("MOUSE"):
        words = line.split()
        mouse_command['action'] = words[1]
        if mouse_command['action'] == 'MOVE' and len(words) == 4:
            mouse_command['x'] = int(words[2])
            mouse_command['y'] = int(words[3])
            runMouseCommand(mouse_command)
    else:
        newScriptLine = convertLine(line)
        runScriptLine(newScriptLine)

    time.sleep(float(defaultDelay) / 1000)
        
#init button
button1_pin = DigitalInOut(GP22) # defaults to input
button1_pin.pull = Pull.UP      # turn on internal pull-up resistor
button1 =  Debouncer(button1_pin)

#init payload selection switch
payload1Pin = digitalio.DigitalInOut(GP4)
payload1Pin.switch_to_input(pull=digitalio.Pull.UP)
payload2Pin = digitalio.DigitalInOut(GP5)
payload2Pin.switch_to_input(pull=digitalio.Pull.UP)
payload3Pin = digitalio.DigitalInOut(GP10)
payload3Pin.switch_to_input(pull=digitalio.Pull.UP)
payload4Pin = digitalio.DigitalInOut(GP11)
payload4Pin.switch_to_input(pull=digitalio.Pull.UP)

def getProgrammingStatus():
    # check GP0 for setup mode
    # see setup mode for instructions
    progStatusPin = digitalio.DigitalInOut(GP0)
    progStatusPin.switch_to_input(pull=digitalio.Pull.UP)
    progStatus = not progStatusPin.value
    return(progStatus)


defaultDelay = 0

def runScript(file):
    global defaultDelay

    duckyScriptPath = file
    try:
        f = open(duckyScriptPath,"r",encoding='utf-8')
        previousLine = ""
        for line in f:
            line = line.rstrip()
            if(line[0:6] == "REPEAT"):
                for i in range(int(line[7:])):
                    #repeat the last command
                    parseLine(previousLine)
                    time.sleep(float(defaultDelay)/1000)
            else:
                parseLine(line)
                previousLine = line
            time.sleep(float(defaultDelay)/1000)
    except OSError as e:
        print("Unable to open file ", file)

def selectPayload():
    global payload1Pin, payload2Pin, payload3Pin, payload4Pin
    payload = "payload.dd"
    # check switch status
    # payload1 = GPIO4 to GND
    # payload2 = GPIO5 to GND
    # payload3 = GPIO10 to GND
    # payload4 = GPIO11 to GND
    payload1State = not payload1Pin.value
    payload2State = not payload2Pin.value
    payload3State = not payload3Pin.value
    payload4State = not payload4Pin.value

    if(payload1State == True):
        payload = "payload.dd"

    elif(payload2State == True):
        payload = "payload2.dd"

    elif(payload3State == True):
        payload = "payload3.dd"

    elif(payload4State == True):
        payload = "payload4.dd"

    else:
        # if all pins are high, then no switch is present
        # default to payload1
        payload = "payload.dd"

    return payload

async def blink_led(led):
    print("Blink")
    if(board.board_id == 'raspberry_pi_pico'):
        blink_pico_led(led)
    elif(board.board_id == 'raspberry_pi_pico_w'):
        blink_pico_w_led(led)

async def blink_pico_led(led):
    print("starting blink_pico_led")
    led_state = False
    while True:
        if led_state:
            #led_pwm_up(led)
            #print("led up")
            for i in range(100):
                # PWM LED up and down
                if i < 50:
                    led.duty_cycle = int(i * 2 * 65535 / 100)  # Up
                await asyncio.sleep(0.01)
            led_state = False
        else:
            #led_pwm_down(led)
            #print("led down")
            for i in range(100):
                # PWM LED up and down
                if i >= 50:
                    led.duty_cycle = 65535 - int((i - 50) * 2 * 65535 / 100)  # Down
                await asyncio.sleep(0.01)
            led_state = True
        await asyncio.sleep(0)

async def blink_pico_w_led(led):
    print("starting blink_pico_w_led")
    led_state = False
    while True:
        if led_state:
            #print("led on")
            led.value = 1
            await asyncio.sleep(0.5)
            led_state = False
        else:
            #print("led off")
            led.value = 0
            await asyncio.sleep(0.5)
            led_state = True
        await asyncio.sleep(0.5)

async def monitor_buttons(button1):
    global inBlinkeyMode, inMenu, enableRandomBeep, enableSirenMode,pixel
    print("starting monitor_buttons")
    button1Down = False
    while True:
        button1.update()

        button1Pushed = button1.fell
        button1Released = button1.rose
        button1Held = not button1.value

        if(button1Pushed):
            print("Button 1 pushed")
            button1Down = True
        if(button1Released):
            print("Button 1 released")
            if(button1Down):
                print("push and released")

        if(button1Released):
            if(button1Down):
                # Run selected payload
                payload = selectPayload()
                print("Running ", payload)
                runScript(payload)
                print("Done")
            button1Down = False

        await asyncio.sleep(0)

def testPayloadExecution(layout):
    # define a ducky script string for testing
    ducky_script = """MOUSE MOVE 100 100"""

    for line in ducky_script.splitlines():
        parseLine(line)

# uncomment to run these tests(if commented)
testPayloadExecution(layout)

