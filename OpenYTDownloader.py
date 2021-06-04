import subprocess
import sys

def installDependencies():
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pytube"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "pillow"])
    subprocess.check_call([sys.executable, "-m", "pip", "install", "ffmpeg-python"])

installDependencies()

from pytube import YouTube
import ffmpeg
from tkinter.ttk import *
import win32clipboard
from threading import Thread
from tkinter import *
from tkinter import messagebox
from tkinter import filedialog
import time
import re
import urllib.parse
from PIL import Image, ImageTk
import io
import os

ClipboardText = ""
VideoThumbnail = False
Loading = False
vid_thumbnail_pack = False
listbox = False
title_label = False

class GetClipboardText(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while not Loading:
            time.sleep(0.5)
            if not Loading:
                data = get_paste_buffer()
                match = re.search("^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+$", data)
                if match and data != vid_URL.get():
                    print("found clipboard data")
                    print(vid_URL.get())
                    print(data)
                    vid_URL.delete(0, END)
                    vid_URL.insert(END, data)
                    loadStreams(vid_URL.get())

class loadingAnimation(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True
        self.start()
    def run(self):
        while True:
            time.sleep(0.001)
            while Loading:
                print("Loading")
                im = Image.open("loading.gif")
                try:
                    while 1:
                        im.seek(im.tell()+1)
                        global LoadingThumbnail, LoadingThumbnail_pack
                        LoadingThumbnail = ImageTk.PhotoImage(im, format="gif -index {}".format(im.tell()))
                        LoadingThumbnail_pack = Label(win, image=LoadingThumbnail, bd=0, bg="#2F2E4F")
                        LoadingThumbnail_pack.place(x=830,y=25)
                        time.sleep(0.075)
                        LoadingThumbnail_pack.destroy()
                        
                except EOFError:
                    pass # end of sequence

def get_paste_buffer():
            win32clipboard.OpenClipboard(0)
            try:
                result = win32clipboard.GetClipboardData()
            except TypeError:
                result = ''  #non-text
                print("Clipboard does not contain text.")
            win32clipboard.CloseClipboard()
            return result 

def getDownloadPath():
    home = os.path.expanduser("~")
    return os.path.join(home, "Downloads")

def startLoading(clear):
    global Loading, vid_thumbnail_pack, listbox, title_label
    Loading = True 
    if clear:
        download_button["state"] = DISABLED
        if vid_thumbnail_pack and listbox and title_label:
            print("your in")
            vid_thumbnail_pack.destroy()
            listbox.destroy()
            title_label.destroy()

def stopLoading():
    global Loading
    LoadingThumbnail_pack.destroy()
    Loading = False

def mouse_down(event):
    global x, y
    x, y = event.x, event.y

def mouse_up(event):
    global x, y
    x, y = None, None

def mouse_drag(event):
    global x, y
    try:
        deltax = event.x - x
        deltay = event.y - y
        x0 = win.winfo_x() + deltax
        y0 = win.winfo_y() + deltay
        win.geometry("+%s+%s" % (x0, y0))
    except:
        pass

def loadThumnail(vid, thumbnail_size = 400):
    print("Loading thumnail...")
    thumbnail_url = vid.thumbnail_url
    print(thumbnail_url)

    raw_data = urllib.request.urlopen(thumbnail_url).read()
    im = Image.open(io.BytesIO(raw_data))

    width, height = im.size
    if width > height:
        new_width = thumbnail_size
        new_height = int(height // (width/thumbnail_size))
    elif height > width:
        new_height = thumbnail_size
        new_width = int(width // (height/thumbnail_size))
    else:
        new_height, new_width = thumbnail_size

    size = (new_width, new_height)
    im = im.resize(size, resample=0)
    global VideoThumbnail, Loading, vid_thumbnail_pack 
    VideoThumbnail = ImageTk.PhotoImage(im)
    vid_thumbnail_pack = Label(win, image=VideoThumbnail, bd=0, bg="#2F2E4F")
    vid_thumbnail_pack.place(x=40,y=100)

def loadTitle(vid):
    global title_label
    title_font = ("Berlin Sans FB Demi", 13, "bold")
    title = vid.title
    print(title)
    title_label = Label(win, font=title_font, text=title, fg="#ffffff", bg="#2F2E4F", anchor=W, width=39)
    title_label.place(x=40,y=325)

def loadDescription(vid):
    description = vid.description.partition('\n')[0]
    print(description)
    description_label = Label(win, text="Description: {}".format(description), bg="#2F2E4F")
    description_label.place(x=0,y=275)

def enableButton(parameter):
    if download_button["state"] == DISABLED:
        download_button["state"] = 'normal'
        download_button["text"] = 'Download'

def getStreams(vid):
    global listbox, stream_maps
    listbox = Listbox(win, 
    height = 15, 
    width = 55, 
    bd = 0,
    bg = "#403F5C",
    activestyle = 'dotbox', 
    font = "Helvetica",
    fg = "white",
    highlightbackground = "#16135C", 
    highlightcolor= "#16135C",
    selectforeground="#ffffff", 
    selectbackground="#2F2B8C",
    justify=CENTER
    )

    listbox.bind("<<ListboxSelect>>", enableButton)

    # insert elements by their
    # index and names.
    stream_list = {}
    try:
        for streamObj in vid.streams:
            stream = str(streamObj)
            print(stream)
            if re.search('type=\"(\w+)\"', stream):
                stype=re.search('type=\"(\w+)\"', stream).group(1)

            if re.search('itag=\"(\d+)\"', str(stream)):
                itag=re.search('itag=\"(\d+)\"', str(stream)).group(1)

            if re.search('mime_type=\"(\w+\/\w+)\"', stream):
                mime_type=re.search('mime_type=\"(\w+\/\w+)\"', stream).group(1)

            if re.search('res=\"(\w+)\"', stream):
                res=re.search('res=\"(\w+)\"', stream).group(1)
            elif re.search('abr=\"(\w+)\"', stream):
                res=re.search('abr=\"(\w+)\"', stream).group(1)[:-4]

            if re.search('fps=\"(\w+)\"', stream):
                fps=re.search('fps=\"(\w+)\"', stream).group(1)
            
            if mime_type and res and fps:
                new_key = int(res[:-1])
                if mime_type not in stream_list:
                    stream_list[mime_type] = {}
                stream_list[mime_type][new_key] = [itag, "Resolution: {} ---- Framerate: {} ---- Format: {}".format(res, fps, mime_type), mime_type.split('/')[1], stype, res]

        stream_maps = {}
        i = 0
        for m_type in stream_list.keys():
            for k in sorted(stream_list[m_type].keys(), reverse=True):  
                print(stream_list[m_type][k])
                listbox.insert(i, stream_list[m_type][k][1])
                stream_maps[i] = stream_list[m_type][k] # iTag, Stream String, format, a/v
                i += 1
        listbox.place(x=467,y=100)

    except Exception as e:
        stopLoading()
        print("Could not load video streams: {}".format(e))
        messagebox.showerror(title="Failed to load streams", message="Could not load video streams: {}".format(e))

def mixAV():
    print("Mixing A/V...")
    vid_path = os.path.join(download_path, "temp_video.webm")
    audio_path = os.path.join(download_path, "temp_audio.webm")
    input_video = ffmpeg.input(vid_path)
    input_audio = ffmpeg.input(audio_path)
    output_path = os.path.join(download_path, "{}.webm".format(vid.title))
    startLoading()
    ffmpeg.concat(input_video, input_audio, v=1, a=1).output(output_path).run()
    stopLoading()

progression = []
def on_progress(p1, p2, bytes_left):
    global progression, progress, s
    if bytes_left != 0:
        progression.append(bytes_left)
    if len(progression) > 0:
        p = (1-(bytes_left/progression[0]))*100
        progress['value']=p
        progress.update()
        
def complete(p1, p2):
    global download_button
    print("Complete!")
    download_button["text"] = "Complete!"
    print(p1)
    print(p2)
    download_button["state"] = DISABLED
    progress['value']=100
    progress.update()
    s.configure("red.Horizontal.TProgressbar", foreground='#0c0b33', background='#0c0b33')

def loadStreams(url):
    global vid, vid_streams
    startLoading(True)
    vid = YouTube(url, on_progress_callback=on_progress, on_complete_callback=complete)
    loadThumnail(vid)
    loadTitle(vid)
    #loadDescription(vid)
    getStreams(vid)
    stopLoading()
    
def choosePath():
    global download_path
    download_path = filedialog.askdirectory(initialdir = download_path)
    if download_path:
        download_path = os.path.normpath(download_path)
        path_label.delete(0, END)
        path_label.insert(END, download_path)

def GetBestAudioStream():
    bitrate = 0
    for k, streamObj in stream_maps.items():
        if streamObj[3] == "audio":
            if bitrate < int(streamObj[4]):
                bitrate = int(streamObj[4])
                audio_stream = k
                print("{}: {}".format(streamObj, bitrate))

    itag = stream_maps[audio_stream][0]
    return vid.streams.itag_index[int(itag)]

def downloadStream():
    global vid
    download_button["state"] = DISABLED
    download_button["text"] = "Downloading..."
    selected_index = listbox.curselection()[0]
    itag = stream_maps[selected_index][0]
    selected_videos = {}
    selected_videos["video"] = vid.streams.itag_index[int(itag)]
    # Check to see if the stream is webm
    if stream_maps[selected_index][2] == "webm" and not stream_maps[selected_index][3] == "audio":
        # Download the audio along with it
        audio_stream = GetBestAudioStream()
        selected_videos["audio"] = audio_stream

    if len(selected_videos) > 1:
        for k, download_stream in selected_videos.items():
            print(download_stream)
            if k == "audio":
                download_stream.download(output_path=download_path, filename="temp_audio")
            else:
                download_stream.download(output_path=download_path, filename="temp_video")
        mixAV()

    else:
        selected_videos["video"].download(output_path=download_path)

win = Tk()

UI_width = 1000
UI_height = 520
win['bg'] = "#2F2E4F"

# Handle borderless and centered window
win.overrideredirect(True)
x, y = None, None
win.geometry("{}x{}".format(UI_width, UI_height))

# Get screen resolution
screen_width = win.winfo_screenwidth()
screen_height = win.winfo_screenheight()

# Gets both half the screen width/height and window width/height
positionRight = int(screen_width/2 - UI_width/2)
positionDown = int(screen_height/2 - UI_height/2)

# Positions the window in the center of the page.
win.geometry("+{}+{}".format(positionRight, positionDown))

# Mouse drag window events
win.bind('<ButtonPress-1>', mouse_down)
win.bind('<B1-Motion>', mouse_drag)
win.bind('<ButtonRelease-1>', mouse_up)

# ===============================================================================================================
# Main UI Content
# ===============================================================================================================

# Close button
button = Button(win, text='X', command=win.destroy, bg="#403F5C", bd=2, fg="#ffffff", font="BOLD")
button.pack(side=TOP, anchor=NE)

# YouTube URL
Font_tuple = ("Comic Sans MS", 18, "bold")
vid_URL = Entry(win, font=Font_tuple, width=40, bg="#0c0b33", fg="#ffffff", bd=2, justify='center', selectforeground="#ffffff", selectbackground="#403F5C")
vid_URL.insert(END, 'Copy A YouTube URL')
vid_URL.pack(anchor=N, ipady=5)

# Init Video Thumbnail
vid_thumbnail_pack = Label()

# Default path title
path_title = Label(win, text="Download Directory:", fg="#ffffff", font=Font_tuple, bg="#2F2E4F")
path_title.place(x=40,y=375)

# Default path
download_path = getDownloadPath()
Font_tuple = ("Comic Sans MS", 18, "bold")
path_label = Entry(win, fg="#ffffff", font=Font_tuple, bg="#0c0b33", selectbackground="#403F5C", width=33, justify=LEFT)
path_label.insert(END, download_path)
path_label.pack(ipadx=5, ipady=50)
path_label.place(x=40,y=420)

# Browse Button
button_font = ("Comic Sans MS", 18, "bold")
path_button = Button(win, text='Browse', command=choosePath, bg="#403F5C", bd=2, fg="#ffffff", font=button_font)
path_button.place(x=555,y=425)

# Download Button
button_font = ("Comic Sans MS", 18, "bold")
download_button = Button(win, text='Download', command=downloadStream, bg="#403F5C", bd=2, fg="#ffffff", font=button_font, width=19)
download_button.place(x=670,y=425)
download_button["state"] = DISABLED

# Progress bar
s = Style()
s.theme_use('clam')
s.configure("red.Horizontal.TProgressbar", foreground='#4E49EB', background='#4E49EB')

progress = Progressbar(win, style="red.Horizontal.TProgressbar", orient = HORIZONTAL, length=498, maximum=100, mode = 'determinate')
progress.place(x=40,y=467)

win.wm_attributes("-topmost", 1) # :( unfortunately there isn't a way to make taskbar icons in tkinter... really regretting this choice :(

# ===============================================================================================================
# END UI Content
# ===============================================================================================================

# Threads
GetClipboardText()
loadingAnimation()
win.mainloop()