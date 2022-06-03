import os
import struct
import subprocess
import tempfile
import PySimpleGUI as sg
import numpy as np

BARS_NUMBER = 10
OUTPUT_BIT_FORMAT = "16bit"
RAW_TARGET = "/dev/stdout"
RATE = 44100

conpat = """
[general]
bars = %d
[output]
method = raw
raw_target = %s
bit_format = %s
"""

config = conpat % (BARS_NUMBER, RAW_TARGET, OUTPUT_BIT_FORMAT)
bytetype, bytesize, bytenorm = ("H", 2, 65535) if OUTPUT_BIT_FORMAT == "16bit" else ("B", 1, 255)


# VARS CONSTS:
_VARS = {'window': False,
         'stream': False,
         'audioData': np.array([])}

# pysimpleGUI INIT:
AppFont = 'Any 16'
sg.theme('DarkBlue2')
CanvasSizeWH = 500

layout = [[sg.Graph(canvas_size=(CanvasSizeWH, CanvasSizeWH),
                    graph_bottom_left=(-16, -16),
                    graph_top_right=(116, 116),
                    background_color='#1A2835',
                    key='graph')],
          [sg.ProgressBar(4000, orientation='h',
                          size=(20, 20), key='-PROG-')],
          [sg.Button('Listen', font=AppFont),
           sg.Button('Stop', font=AppFont, disabled=True),
           sg.Button('Exit', font=AppFont)]]
_VARS['window'] = sg.Window('Realtime PyAudio EQ Display',
                            layout, finalize=True)

graph = _VARS['window']['graph']


# FUNCTIONS:


def drawAxis():
    graph.DrawLine((0, 1), (101, 1), color='#809AB6')  # Y Axis
    graph.DrawLine((1, 0), (1, 101), color='#809AB6')  # X Axis


def drawTicks():
    pad = 1
    divisionsX = 10
    multi = int(RATE/divisionsX)
    offsetX = int(100/divisionsX)

    divisionsY = 10
    offsetY = int(100/divisionsY)

    # ( x ➡️ , y ⬆️  ) Coordiante reference
    for x in range(0, divisionsX+1):
        # print('x:', x)
        graph.DrawLine(((x*offsetX)+pad, -3), ((x*offsetX)+pad, 3),
                       color='#809AB6')
        graph.DrawText(int((x*multi/1000)), ((x*offsetX), -6), color='#809AB6')

    for y in range(0, divisionsY+1):
        graph.DrawLine((-3, (y*offsetY)+pad), (3, (y*offsetY)+pad),
                       color='#809AB6')


def drawAxesLabels():
    graph.DrawText('kHz', (-10, 0), color='#809AB6')
    graph.DrawText('Freq. Level - Amplitude', (-5, 50),
                   color='#809AB6', angle=90)

def run():
    with tempfile.NamedTemporaryFile() as config_file:
        config_file.write(config.encode())
        config_file.flush()
        
        process = subprocess.Popen(["cava", "-p", config_file.name], stdout=subprocess.PIPE)
        chunk = bytesize * BARS_NUMBER
        fmt = bytetype * BARS_NUMBER
        
        if RAW_TARGET != "/dev/stdout":
            if not os.path.exists(RAW_TARGET):
                os.mkfifo(RAW_TARGET)
            source = open(RAW_TARGET, "rb")
        else:
            source = process.stdout
        
        while True:
            data = source.read(chunk)
            if len(data) < chunk:
                break
            # sample = [i for i in struct.unpack(fmt, data)]  # raw values without norming
            sample = [i / bytenorm for i in struct.unpack(fmt, data)]
            updateUI(sample)

def fun(x):
    return x*BARS_NUMBER

def drawEQ(data):
    vfunc = np.vectorize(fun)
    BINS = vfunc(data)
    BINS = np.round(BINS)
    print(BINS)

    # Make Bars
    barStep = BARS_NUMBER  # Height, width of bars
    pad = 2  # padding left,right,top,bottom
    for col, val in enumerate(BINS):
        print('column:', col, ' gets ', val, 'Bars')
        for bar in range(0, int(val)):
            # print('bar', bar
            # ( x ➡️ , y ⬆️  ) Coordiante reference
            if bar < 3:
                barColor = '#00FF0E'
            elif bar < 6:
                barColor = 'yellow'
            elif bar < 9:
                barColor = 'orange'
            else:
                barColor = 'red'

            graph.draw_rectangle(top_left=((col*barStep)+pad, barStep*(bar+1)),
                                 bottom_right=((col*barStep)+barStep,
                                               (bar*barStep)+pad),
                                 line_color='black',
                                 line_width=2,
                                 fill_color=barColor)  # Conditional
            # graph.draw_rectangle(top_left=((col*barStep)+pad, barStep*(bar+1)),
            #                      bottom_right=((col*barStep)+barStep,
            #                                    (bar*barStep)+pad),
            #                      line_color='black',
            #                      line_width=2,
            #                      fill_color=barColor)  # Conditional

def updateUI(data):
    graph.erase()
    drawAxis()
    drawTicks()
    drawAxesLabels()    
    drawEQ(data)

drawAxis()
drawTicks()
drawAxesLabels()

if __name__ == "__main__":
    run()

_VARS['window'].close()
