#     __                                    ___            __
#    /\ \__  __                            /\_ \    __    /\ \
#    \ \ ,_\/\_\    ___ ___      __    ____\//\ \  /\_\   \_\ \     __
#     \ \ \/\/\ \ /' __` __`\  /'__`\ /',__\ \ \ \ \/\ \  /'_` \  /'__`\
#      \ \ \_\ \ \/\ \/\ \/\ \/\  __//\__, `\ \_\ \_\ \ \/\ \L\ \/\  __/
#       \ \__\\ \_\ \_\ \_\ \_\ \____\/\____/ /\____\\ \_\ \___,_\ \____\
#        \/__/ \/_/\/_/\/_/\/_/\/____/\/___/  \/____/ \/_/\/__,_ /\/____/
#
#        a beautifully simple gui to slide old photographs into TODAY
#

# set up delodify
from deoldify import device
from deoldify.device_id import DeviceId
device.set(device = DeviceId.GPU0)
from deoldify.visualize import *
torch.backends.cudnn.benchmark = True

# other modules
import tkinter as tk
import tkinter.filedialog
from tkinter import ttk
from PIL import Image, ImageTk
import shutil
import os
import urllib.request
import io

# canvas
canv_width  = 500
canv_height = 400
bg_color    = "#ECECEC"

class Window(tk.Frame):

    # Define settings upon initialization. Here you can specify
    def __init__(self, master=None):
        
        tk.Frame.__init__(self, master, bg=bg_color)   
        #reference to the master widget, which is the tk window                 
        self.master = master
        self.init_window()

    # initialize window
    def init_window(self):

        # load_method = (None, "open_file", "load_url")
        self.load_method=None

        # setup
        self.master.title("TimeSlide")
        self.pack(fill=tk.BOTH, expand=1)

        # creating a menu instance
        menu = tk.Menu(self.master)
        self.master.config(menu=menu)

        # create the file menu
        file = tk.Menu(menu)
        file.add_command(label="Open Local Photo...", command=self.open_file)
        file.add_command(label="Exit", command=self.client_exit)
        menu.add_cascade(label="File", menu=file)

        # image canvas
        self.canvas = tk.Canvas(self, width=canv_width, height=canv_height,
            background='black')
        self.image_id = self.canvas.create_image(canv_width, canv_height,
            anchor='se')
        self.canvas.pack()

        # FRAME - load old photo

        frame_load = tk.LabelFrame(self, text="Step 1: Load Old Photo",
            pady=4, bg=bg_color)
        frame_load.pack(fill="x", padx=4)
        
        # open_file button
        btn_open_photo = ttk.Button(frame_load, text="Open Local Photo...",
            command=self.open_file)
        btn_open_photo.pack(side=tk.LEFT)
        label_or = ttk.Label(frame_load, text="  or  ", background=bg_color)
        label_or.pack(sid=tk.LEFT, padx=22)
        
        # load_url button
        btn_load_url = ttk.Button(frame_load, text="Load URL",
            command=self.load_url)
        btn_load_url.pack(side=tk.RIGHT)
        
        # url_string
        self.str_url = tk.Text(frame_load, width=40, height=1)
        self.str_url.pack(side=tk.RIGHT, padx=4)

        # FRAME - colorize

        frame_colorize = tk.LabelFrame(self, text="Step 2: Colorize",
            pady=4, bg=bg_color)
        frame_colorize.pack(fill="x", padx=4)

        # colorize check box
        self.colorize_int = tk.IntVar()
        self.colorize_int.set(1)
        chk_colorize = ttk.Checkbutton(frame_colorize, text="Colorize",
            variable=self.colorize_int, offvalue=0, onvalue=1)
        chk_colorize.pack(side=tk.LEFT)
       
        # colorize model dropdown
        self.model_vars = tk.StringVar(frame_colorize)
        self.model_vars.set("Stable")
        model_label = tk.Label(frame_colorize, text='Model:', bg=bg_color)
        model_label.pack(side=tk.LEFT, padx=(15,0))
        self.colorize_model = tk.OptionMenu(frame_colorize, self.model_vars,
            "Stable", "Artistic")
        self.colorize_model.pack(side=tk.LEFT, padx=0)
        
        # colorize render factor
        min_rndr_fctr = 7
        max_rndr_fctr = 45
        self.scale_rf = tk.Scale(frame_colorize,
            from_=min_rndr_fctr, to=max_rndr_fctr, orient="horizontal",
            length=150, bg=bg_color)
        self.scale_rf.pack(side=tk.RIGHT, fill="x")
        self.scale_rf.set(30)
        label_rf = ttk.Label(frame_colorize, text="Render Factor: ",
            background=bg_color)
        label_rf.pack(sid=tk.RIGHT)

        # FRAME - finish

        frame_finish = tk.LabelFrame(self, text="Step 3: Finish Up",
            pady=4, bg=bg_color)
        frame_finish.pack(fill="x", padx=4)
       
        # timeslide button
        self.btn_timeslide = ttk.Button(frame_finish, text="Slide Time!",
            command=self.timeslide)
        self.btn_timeslide['state'] = 'disabled'
        self.btn_timeslide.pack(side=tk.LEFT)

        # save as button
        self.btn_save_photo = ttk.Button(frame_finish, text="Save New Photo...",
            command=self.save_file)
        self.btn_save_photo['state'] = 'disabled'
        self.btn_save_photo.pack(side=tk.LEFT)

    # open file
    def open_file(self):

        # load file dialog
        file_types = [
            ('Image files', '*.jpg *.jpeg *.png'),
        ]
        self.file_path = tk.filedialog.askopenfilename(filetypes=file_types)
        
        # open image and resize
        img = Image.open(self.file_path)
        img = img.resize((canv_width, canv_height), Image.ANTIALIAS)
        self.canvas.img_tk = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.image_id, image=self.canvas.img_tk)

        # enable timeslide button
        self.btn_timeslide['state'] = 'normal'

        # set load method
        self.load_method="open_file"

    # load from url
    def load_url(self):
        
        # load raw data and display
        raw_data = urllib.request.urlopen(self.str_url.get("1.0",tk.END)).read()
        img = Image.open(io.BytesIO(raw_data))
        img = img.resize((canv_width, canv_height), Image.ANTIALIAS)
        self.canvas.img_tk = ImageTk.PhotoImage(img)
        self.canvas.itemconfig(self.image_id, image=self.canvas.img_tk)

        # enable timeslide button
        self.btn_timeslide['state'] = 'normal'

        # set load method
        self.load_method="load_url"

    # timeslide
    def timeslide(self):

        # do colorization
        if (self.colorize_int.get() == 1):

            # determine colorizer model
            if (self.model_vars.get() == "Artistic"):
                colorizer = get_image_colorizer(artistic=True)
            elif (self.model_vars.get() == "Stable"):
                colorizer = get_image_colorizer(artistic=False)

            # get render factor
            render_factor = self.scale_rf.get()

            if self.load_method in "open_file":
                self.result_path = colorizer.plot_transformed_image(
                    path = self.file_path, render_factor = render_factor,
                    compare = False)
            elif self.load_method in "load_url":
                print(self.str_url.get("1.0",tk.END))
                self.result_path = colorizer.plot_transformed_image_from_url(
                    url=self.str_url.get("1.0",tk.END), path='//tmp/tmp.png',
                    render_factor = render_factor, compare = False)
            img = Image.open(self.result_path)
            img = img.resize((canv_width, canv_height), Image.ANTIALIAS)
            self.canvas.img_tk = ImageTk.PhotoImage(img)
            self.canvas.itemconfig(self.image_id, image=self.canvas.img_tk)

        else:
            pass

        # enable save button
        self.btn_save_photo['state'] = 'normal'

    def save_file(self):
        file_types = [
            ('Image files', '*.jpg *.jpeg')
        ]
        save_file = tk.filedialog.asksaveasfile(filetypes = file_types)
        from_path = str(os.getcwd()) + "/" + str(self.result_path)
        print(from_path)
        print(save_file.name)
        shutil.copyfile(from_path, save_file.name)

    # exit
    def client_exit(self):
        exit()

# configure primary window        
root = tk.Tk()
root.geometry("%ix584" % canv_width)
root.configure(bg=bg_color)

# creation of an instance
app = Window(root)

# mainloop 
root.mainloop()  