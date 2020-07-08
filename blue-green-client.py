#!/usr/bin/env python3

import urwid
import asyncio
from aiohttp import ClientSession

url = "http://localhost:3000/api/version"

# Set up color scheme for UI
palette = [
    ('titlebar','white','dark red','bold'),
    ('greenbox', 'white', 'dark green'),
    ('bluebox', 'white', 'dark blue'),
    ('redbox', 'white', 'dark red'),
    ('graybox', 'white', 'light gray'),
    ('blackbox', 'black', 'black'),
    ('normal', 'light gray', 'black'),
    ('editbox', 'black', 'light gray'),
    ('button', 'black', 'dark cyan'),
    ('buttonf', 'white', 'dark blue')]

total_try = 10
webget_complete = 0
task_is_running = False


green_ver = None
blue_ver = None
# green_total = 0
# blue_total = 0
loop = asyncio.get_event_loop()

async def fetch(url, session, boxnum, asyncState):
    global green_ver
    global blue_ver
    # global green_total
    # global blue_total
    response = ""
    try:
        async with session.get(url) as response:
            response = await response.text()

            # put our first response to green_ver
            if green_ver == None:
                green_ver = response[0]
            # put our 2nd response to blue_ver
            elif blue_ver == None and response[0] != green_ver:
                blue_ver = response[0]

            # if green_ver is None, that means we're running the first time
            # if green_ver == None and blue_ver == None:
            #     # to make things simple, we just get the first char returned as the version number
            #     # so remember to change this in the nodejs server
            #     green_ver = response[0]
            #     result_gridlist[boxnum].ChangeGreen()
            #     result_gridlist[boxnum].ChangeVer(response[0])

            #     green_total += 1
            #     return

            # we are running the 2nd time
            # if response[0] != green_ver and green_ver != None and blue_ver == None:
            #     blue_ver = response[0]
            #     result_gridlist[boxnum].ChangeBlue()
            #     result_gridlist[boxnum].ChangeVer(response[0])
            #     blue_total += 1
            #     return

            # we already pass the 1st and 2nd run
            if response[0] == green_ver:
                result_gridlist[boxnum].ChangeGreen()
                result_gridlist[boxnum].ChangeVer(response[0])
                # green_total += 1
                asyncState.green_total = asyncState.green_total + 1
            elif response[0] == blue_ver:
                result_gridlist[boxnum].ChangeBlue()
                result_gridlist[boxnum].ChangeVer(response[0])
                # blue_total += 1
                asyncState.blue_total = asyncState.blue_total + 1
            else:
                result_gridlist[boxnum].ChangeRed()
                result_gridlist[boxnum].ChangeVer(response[0])
    except Exception as e:
        result_gridlist[boxnum].ChangeGray()
        result_gridlist[boxnum].ChangeVer("X")
        status_text.set_text("Cannot connect to server!!!")
        #print(e)


#------ result text window
# green_text = urwid.Text(u"80% version 1")
# blue_text = urwid.Text(u"20% version 2")
# bg_pile = urwid.Pile([green_text, blue_text])
# bgfill = urwid.Filler(bg_pile, valign='top', top=1, bottom=1)



async def run(r):
    global task_is_running
    # global green_total
    # global blue_total
    tasks = []

    asyncState = type('', (), {})()

    while task_is_running == True:
        # Fetch all responses within one Client session,
        # keep connection alive for all requests.
        # green_total = 0
        # blue_total = 0
        asyncState.green_total = 0
        asyncState.blue_total = 0

        async with ClientSession() as session:
            for i in range(r):
                task = asyncio.ensure_future(fetch(url.format(i), session, i, asyncState))
                tasks.append(task)

            await asyncio.gather(*tasks)

            # calculate percentage
            blue_percent = asyncState.blue_total/r
            green_percent = asyncState.green_total/r
            blue_text.set_text("Blue: " + "{:.0%}".format(blue_percent))
            green_text.set_text("Green:" + "{:.0%}".format(green_percent))
            # blue_text.set_text("Blue: " + str(blue_total))
            # green_text.set_text("Green:" + str(green_total))
            # blue_text.set_text("Blue: " + str(asyncState.blue_total))
            # green_text.set_text("Green:" + str(asyncState.green_total))
            await asyncio.sleep(1)

    #print("task not running")


# widget class for result color box display
class ResultBox(urwid.WidgetWrap):

    def __init__(self):
        block = u"   \n X \n   "

        self.textbox = urwid.Text(block)
        self.boxmap = urwid.AttrMap(self.textbox, 'blackbox')
        self.__super.__init__(self.boxmap)

    def ChangeGray(self):
        self.boxmap.set_attr_map({None:'graybox'})

    def ChangeBlue(self):
        self.boxmap.set_attr_map({None:'bluebox'})

    def ChangeGreen(self):
        self.boxmap.set_attr_map({None:'greenbox'})

    def ChangeRed(self):
        self.boxmap.set_attr_map({None:'redbox'})

    def Hide(self):
                self.boxmap.set_attr_map({None:'blackbox'})

    def ChangeVer(self, ver):
        preblk = u"   \n "
        postblk = u" \n   "
        mytext = preblk + ver + postblk
        self.textbox.set_text(mytext)

# quit when "q" is press
def exit_on_q(key):
    if key in ('q', 'Q'):
        raise urwid.ExitMainLoop()

# change to total_try value when the try radio button selection changed
def try_radiobtn_change(rbtn, state, data):
    if state:
        global total_try
        total_try = data

def stop_button_click(btn, data):
    global task_is_running
    task_is_running = False
    status_text.set_text("All Stopped")

def quit_button_click(btn, data):
    # do clean up
    raise urwid.ExitMainLoop()

# call back when start button clicked
def start_button_click(btn, data):
    global url
    global green_ver
    global blue_ver
    global task_is_running

    status_text.set_text("Tasks started")

    for x in range(100):
         if x < total_try:
             result_gridlist[x].ChangeGray()
         else:
             result_gridlist[x].Hide()

    # initialize the blue green version numbers
    green_ver = None
    blue_ver = None

    # the urlbox should contain prefix "URL: "
    # so we split the string and just get the real url

    urlbox, attr = url_edit.get_text()
    url = urlbox.split("URL: ",1)[1]

    task_is_running = True
    #loop = asyncio.get_event_loop()
    future = asyncio.ensure_future(run(total_try))
    loop.create_task(run(total_try))
    #loop.run_until_complete(future)


############## UI starts here #####################

#------ result text window
blue_text = urwid.Text(u"80% version 1")
green_text = urwid.Text(u"20% version 2")
bg_pile = urwid.Pile([blue_text, green_text])
bgfill = urwid.Filler(bg_pile, valign='top', top=1, bottom=1)

#------ draw 100 boxes and hide them
result_gridlist = []
for x in range(100):
    mybox = ResultBox()
    result_gridlist.append(mybox)


grid = urwid.GridFlow(result_gridlist, 3, 1, 1, 'left')
gfill = urwid.Filler(grid, valign='top', top=1, bottom=1)

btm_div = urwid.SolidFill(u'|')
btm_div_pad = urwid.Padding(btm_div, align='center', left=1, right=1)

# create column here to form the bottom part of the window
bottom_col = urwid.Columns([gfill, (3, btm_div_pad),  (15, bgfill)])




#------ all radio buttons for number of trys

try_num_text = urwid.Text(u"Number of trys")

bgroup = [] # button group
r1 = urwid.RadioButton(bgroup, u"10")
r2 = urwid.RadioButton(bgroup, u"20")
r3 = urwid.RadioButton(bgroup, u"40")
r4 = urwid.RadioButton(bgroup, u"60")
r5 = urwid.RadioButton(bgroup, u"80")
r6 = urwid.RadioButton(bgroup, u"100")


urwid.connect_signal(r1, 'change', try_radiobtn_change, 10)
urwid.connect_signal(r2, 'change', try_radiobtn_change, 20)
urwid.connect_signal(r3, 'change', try_radiobtn_change, 40)
urwid.connect_signal(r4, 'change', try_radiobtn_change, 60)
urwid.connect_signal(r5, 'change', try_radiobtn_change, 80)
urwid.connect_signal(r6, 'change', try_radiobtn_change, 100)


r1m = urwid.AttrWrap(r1, 'normal', 'buttonf')
r2m = urwid.AttrWrap(r2, 'normal', 'buttonf')
r3m = urwid.AttrWrap(r3, 'normal', 'buttonf')
r4m = urwid.AttrWrap(r4, 'normal', 'buttonf')
r5m = urwid.AttrWrap(r5, 'normal', 'buttonf')
r6m = urwid.AttrWrap(r6, 'normal', 'buttonf')

pile = urwid.Pile([try_num_text, urwid.Divider(), r1m, r2m, r3m, r4m, r5m, r6m])
radiobtn_filler = urwid.Filler(pile, valign='top', top=1, bottom=1)

#---------- URL box

url_edit = urwid.Edit(('normal',"URL: "), url, False)
urlmap = urwid.AttrMap(url_edit, 'editbox')
urlfill = urwid.Filler(urlmap, valign='top', top=1, bottom=1)

#---------- start stop buttons

b1 = urwid.Button("Start")
b2 = urwid.Button("Stop")
b3 = urwid.Button("Quit")

urwid.connect_signal(b1, 'click', start_button_click, 'start')
urwid.connect_signal(b2, 'click', stop_button_click, 'stop')
urwid.connect_signal(b3, 'click', quit_button_click, 'quit')

b1map = urwid.AttrWrap(b1, 'button', 'buttonf')
b2map = urwid.AttrWrap(b2, 'button', 'buttonf')
b3map = urwid.AttrWrap(b3, 'button', 'buttonf')

#------------ forming top window
bcol = urwid.Columns([(10,b1map), (10,b2map), (10,b3map)], dividechars=2)
bfill = urwid.Filler(bcol, valign='top', top=1, bottom=1)

topright_pile = urwid.Pile([urlfill, bfill])

top_col = urwid.Columns([(20, radiobtn_filler), topright_pile])

#-------- middle divider bar with status

status_text = urwid.Text(u"Test Stopped")
status_fill = urwid.Filler(status_text, valign='top', top=1, bottom=0)
div = urwid.Divider('-')
divfill = urwid.Filler(div, valign='top', top=0, bottom=1)

#-------- put top, middle and bottom UI together

main_pile = urwid.Pile([(11, top_col), (1, status_fill), (1, divfill), bottom_col])

#------- put all that in the frame with title bar
title_text = urwid.Text(u"Blue Green Deployment Demo")
title = urwid.AttrMap(title_text, 'titlebar')
mainframe = urwid.Frame(header=title, body=main_pile)

evloop = urwid.AsyncioEventLoop(loop=loop)

floop = urwid.MainLoop(mainframe, palette, event_loop=evloop, unhandled_input=exit_on_q)
floop.run()
