import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import os
from tkinter import ttk
import yaml

Global_color_list = ["red", "orange", "yellow", "green", "blue", "cyan", "purple",
                     "hot pink", "dark orange", "gold", "spring green", "navy",
                     "cadet blue", "magenta"]
# method = ['kp', 'bb']
settingWindowCounter = 1

# load config file
with open('config.yaml') as yaml_file:
    config = yaml.load(yaml_file, Loader=yaml.FullLoader)


def threshold_value(current_x, current_y, thres_x, thres_y):
    return min(max(current_x, 0), thres_x), min(max(current_y, 0), thres_y)


def segment_file_name(file_name):
    fns = file_name.split('.')
    if len(fns) == 1:
        return fns[0], ''
    else:
        return fns[0], fns[-1]


class GUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("图像处理")
        self.rootGeometry = (1680, 960)
        self.root.geometry('%dx%d+0+0' % (self.rootGeometry[0], self.rootGeometry[1]))
        self.root.grid_propagate(False)
        self.root.pack_propagate(False)
        self.rootSettingWindow = None
        self.root.bind('<KeyPress>', self.on_key_press)

        self.displayImage = None
        self.originalImageSize = None
        self.resizedImageSize = (300, 300)
        self.resizeImgFlag = config['resize_img']
        self.canvasImgZoomX = None
        self.canvasImgZoomY = None

        self.drawMethod_value_list = ['Keypoint', 'Bounding Box']
        self.drawPointSize = config['draw_label_size']['default']
        self.drawBBsize = config['draw_label_size']['default']
        self.drawMethod = self.drawMethod_value_list[config['default_draw_method']]
        self.drawBBcoordList = []  # list of coordinates for drawing bounding box (coordinates based on event.xy)
        self.drawTraceList = []  # used to trace canvas draw items for delete or ...

        self.ok_to_change_draw_method = True
        self.currentWorkingPath = None
        self.KPcoordList = []
        self.BBcoordList = []  # list of coordinates to display and save for BB (coordinates based on resized x y)
        self.trvSelectFile = ''
        self.trvSelectIid = None
        self.trvSize = None
        # self.saveFileName = ''
        self.saveFileNumberCounter = 0

        # image area
        self.imageFrame = tk.Frame(self.root, width=1400, height=850, highlightbackground="blue", highlightthickness=2)
        self.imageFrame.pack_propagate(False)
        self.imageCanvas = tk.Canvas(self.imageFrame, width=1280, height=720, bg='green')
        self.imageProcessFrame = tk.Frame(self.imageFrame, width=300, height=50,
                                          highlightbackground="red", highlightthickness=2)
        self.imageProcessFrame.pack_propagate(False)
        self.nextImageBTN = None
        self.previousImageBTN = None
        self.saveAndNextBTN = None
        self.coorDisplaybar = tk.Text(self.root, padx=20, pady=10, height=1, width=170, bg="light cyan")

        # working dir area
        self.workingDirFrame = tk.Frame(self.root, bg='black', highlightbackground="green", highlightthickness=2)
        self.btn1 = None  # select folder button
        self.folderName = tk.Label(self.workingDirFrame, text="", font=12, width=20, height=1,
                                   background='green', foreground="white")

        # files display tree area
        self.trvFrame = tk.Frame(self.root)
        self.cDsb = tk.Scrollbar(self.trvFrame)  # orient='horizontal'
        self.trv = ttk.Treeview(self.trvFrame, selectmode='none', height=12)

        # label setting area
        self.labelSettingFrame = tk.Frame(self.root, height=480, width=220,
                                          highlightbackground="green", highlightthickness=2)
        self.labelSettingFrame.grid_propagate(False)
        self.selectedLabel = tk.StringVar()
        self.labelComboBox = ttk.Combobox(self.labelSettingFrame, textvariable=self.selectedLabel)
        self.labelComboBoxMap = {}

        self.sizeRadioFrame = tk.Frame(self.labelSettingFrame)
        self.sizeRadioLabel = tk.Label(self.sizeRadioFrame, text="Size:", font=10)
        self.sizeRadioBtn = tk.Radiobutton(self.sizeRadioFrame)
        self.SRSiv = tk.IntVar()
        self.SRSiv.set(config['draw_label_size']['default'])
        self.sizeRadioString = [("1", 1), ("3", 3), ("5", 5), ("7", 7)]

        # output setting area
        self.outputFrame = tk.Frame(self.root, bg='black', highlightbackground="cyan", highlightthickness=2)
        self.btnOutput = None  # open output setting window button
        self.outputPathLabel = tk.Label(self.outputFrame, text="", font=12, width=20, height=1,
                                        background='firebrick4', foreground="white")
        self.SaveFileStructure = self.SFS()

        # menu area
        self.menuBar = tk.Menu(self.root)
        self.fileMenu = None

        self.interface()
        self.button()
        self.menu_bar()

    class SFS:
        def __init__(self):
            self.saveFilePath = ''
            self.saveFileType = 'txt'
            # self.opl = output_label

        def get_value(self, a):
            self.saveFilePath = a
            # print(self.saveFilePath)
            # self.opl.config(text=self.saveFilePath)

    def button(self):
        self.btn1 = tk.Button(self.workingDirFrame, text='Select directory', font=12,
                              command=self.list_file_in_folder)
        self.btn1.pack(side='bottom')

        self.btnOutput = tk.Button(self.outputFrame, text="Output Setting", font=12,
                                   command=self.open_setting_window)
        self.btnOutput.pack(side='top')
        # self.btnOutput.bind("<Button-1>", self.open_setting_window)

        self.nextImageBTN = tk.Button(self.imageProcessFrame, text=">>", font=12,
                                      command=self.show_next_img)
        self.nextImageBTN.pack(side='right')

        self.previousImageBTN = tk.Button(self.imageProcessFrame, text="<<", font=12,
                                          command=self.show_previous_img)
        self.previousImageBTN.pack(side='left')

        self.saveAndNextBTN = tk.Button(self.imageProcessFrame, text='SAVE', font=12,
                                        command=self.save_result_show_next)
        self.saveAndNextBTN.pack()

        for si, val in self.sizeRadioString:
            tk.Radiobutton(self.sizeRadioFrame, text=si, padx=5, variable=self.SRSiv,
                           command=self.change_label_size, value=val).pack(side='left')
        # self.root.bind('<Return>', self.save_result)

    def interface(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)
        self.root.columnconfigure(2, weight=3)
        self.root.columnconfigure(3, weight=3)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=4)
        self.root.rowconfigure(2, weight=4)
        self.root.rowconfigure(3, weight=1)

        self.labelSettingFrame.rowconfigure(0, weight=2)
        self.labelSettingFrame.rowconfigure(1, weight=2)
        self.labelSettingFrame.rowconfigure(2, weight=2)

        self.imageFrame.grid(row=0, column=0, columnspan=2, rowspan=3)
        self.coorDisplaybar.grid(row=3, column=0, columnspan=2, sticky='nw', padx=5)
        self.coorDisplaybar.config(state='disabled', wrap='none', xscrollcommand=self.cDsb.set)
        self.imageProcessFrame.pack(side='bottom')

        # working dir list (interface)
        self.workingDirFrame.grid(row=0, column=3, sticky='ne', padx=(0, 10), pady=10)
        self.folderName.pack(side='top')

        # tree view file list area (interface)
        self.trvFrame.grid(row=1, column=3, sticky='ne')
        self.cDsb.pack(side='right', fill=tk.Y)
        self.trv.pack()
        self.trv.config(yscrollcommand=self.cDsb.set, selectmode='browse')
        self.cDsb.config(command=self.trv.yview)

        # label setting area (interface)
        self.labelSettingFrame.grid(row=2, column=3, sticky='ne', padx=(0, 10))
        self.labelComboBox['values'] = self.drawMethod_value_list
        self.labelComboBox['state'] = 'readonly'
        self.labelComboBox.grid(row=1, sticky='we', padx=(15, 5))
        self.labelComboBox.bind('<<ComboboxSelected>>', self.label_method_changed)
        self.labelComboBox.current(config['default_draw_method'])

        self.sizeRadioFrame.grid(row=3)
        self.sizeRadioLabel.pack(side='left', fill=tk.Y)

        # output area (interface)
        self.outputFrame.grid(row=3, column=3, sticky='e', padx=(0, 10))
        self.outputPathLabel.pack(side='bottom')

        # working list (interface)
        trv_s = ttk.Style()
        trv_s.theme_use('clam')
        trv_s.configure('Treeview.Heading', background="grey")
        self.trv.heading('#0', text="Working Directory", anchor='center')
        self.trv.bind("<Double-1>", self.trv_double_click)

    def menu_bar(self):
        self.fileMenu = tk.Menu(self.menuBar, tearoff=0)
        self.fileMenu.add_command(label="Open Directory", command=self.list_file_in_folder)
        self.fileMenu.add_command(label="Save Setting", command=self.open_setting_window)
        # self.fileMenu.add_command(label="Open", command=donothing)
        # self.fileMenu.add_command(label="Save", command=donothing)
        # self.fileMenu.add_command(label="Save as...", command=donothing)
        self.fileMenu.add_separator()
        self.fileMenu.add_command(label="Close", command=self.root.destroy)
        self.menuBar.add_cascade(label='File', menu=self.fileMenu, font=('', 50))

        self.menuBar.add_cascade(label='Help')
        self.root.config(menu=self.menuBar)

    def donothing(self):
        pass

    def list_file_in_folder(self):
        # messagebox.showinfo("window1", "bing!")
        folder_selected = filedialog.askdirectory()
        if not folder_selected:
            return
        self.currentWorkingPath = folder_selected
        self.folderName.config(text=folder_selected, anchor='w')
        create_widget_tip(self.folderName)
        for item in self.trv.get_children():
            self.trv.delete(item)

        i = 1
        for root, subdir, files in os.walk(folder_selected):
            if root == self.currentWorkingPath:
                for file in files:
                    self.trv.insert("", 'end', iid=str(i), text=file, tags='selectable')
                    i += 1
        self.trvSize = i-1
        print(self.trvSize)

    def trv_double_click(self, event):
        tree = event.widget
        item_name = tree.identify_row(event.y)
        if item_name:
            tags = tree.item(item_name, 'tags')
            if tags and (tags[0] == 'selectable'):
                tree.selection_set(item_name)
                # select_file_name = tree.item(item_name, "text")
                self.saveFileNumberCounter = 0
                self.trvSelectFile = tree.item(item_name, "text")
                self.trvSelectIid = int(tree.focus())
                select_file_path = os.path.join(self.currentWorkingPath, self.trvSelectFile)
                self.display_image(select_file_path)

    def display_image(self, path):
        # path = filedialog.askopenfilename(filetypes=[('image files', '*.jpg')])
        self.clear_display()
        orig_image = Image.open(path)
        self.originalImageSize = orig_image.size
        print(self.originalImageSize)
        if self.resizeImgFlag:
            resized_img = orig_image.resize(self.resizedImageSize, Image.ANTIALIAS)  # Image.LANCZOS
        else:
            resized_img = orig_image
        ri_x, ri_y = resized_img.size[0], resized_img.size[1]
        self.displayImage = ImageTk.PhotoImage(resized_img)
        self.imageCanvas.pack(anchor='center', side='top')
        img_can_x, img_can_y = self.imageCanvas.winfo_reqwidth(), self.imageCanvas.winfo_reqheight()
        print(img_can_x, img_can_y, ri_x, ri_y)
        self.canvasImgZoomX, self.canvasImgZoomY = int((img_can_x-ri_x)/2), int((img_can_y-ri_y)/2)
        print(self.canvasImgZoomX, self.canvasImgZoomY)
        img_canv = self.imageCanvas.create_image(self.canvasImgZoomX, self.canvasImgZoomY,
                                                 anchor='nw', image=self.displayImage)
        # if self.drawMethod.lower() == 'keypoint':
        #     self.imageCanvas.tag_bind(img_canv, '<Button-1>', self.get_press_coordinate)
        # elif self.drawMethod.lower() == 'bounding box':
        #     self.imageCanvas.tag_bind(img_canv, '<Button-1>', self.get_press_coordinate)
        #     self.imageCanvas.tag_bind(img_canv, '<ButtonRelease-1>', self.get_release_coordinate)
        self.imageCanvas.tag_bind(img_canv, '<Button-1>', self.get_press_coordinate)
        self.imageCanvas.tag_bind(img_canv, '<ButtonRelease-1>', self.get_release_coordinate)

    def de_resize_coordinates(self, cur_x, cur_y):
        beilv_x = self.resizedImageSize[0] / self.originalImageSize[0]
        beilv_y = self.resizedImageSize[1] / self.originalImageSize[1]
        return round(cur_x / beilv_x), round(cur_y / beilv_y)

    def draw_point(self, dp_x, dp_y, color_id):
        global Global_color_list
        color = Global_color_list[color_id-1]
        x1, y1 = (dp_x - self.drawPointSize), (dp_y - self.drawPointSize)
        x2, y2 = (dp_x + self.drawPointSize), (dp_y + self.drawPointSize)
        my_draw = self.imageCanvas.create_oval(x1, y1, x2, y2, fill=color)
        self.drawTraceList.append(my_draw)

    def draw_bb(self, bb_list, color_id):
        global Global_color_list
        color = Global_color_list[color_id-1]
        x1, y1 = bb_list[0][0], bb_list[0][1]
        x2, y2 = bb_list[1][0], bb_list[1][1]
        my_draw = self.imageCanvas.create_rectangle(x1, y1, x2, y2, outline=color, width=self.drawBBsize)
        self.drawTraceList.append(my_draw)

    def get_press_coordinate(self, event):
        self.ok_to_change_draw_method = False
        ex = event.x
        ey = event.y

        if self.resizeImgFlag:
            cand_x, cand_y = threshold_value(ex - self.canvasImgZoomX, ey - self.canvasImgZoomY,
                                             self.resizedImageSize[0], self.resizedImageSize[1])
            final_x, final_y = self.de_resize_coordinates(cand_x, cand_y)
        else:
            final_x, final_y = threshold_value(ex - self.canvasImgZoomX, ey - self.canvasImgZoomY,
                                               self.originalImageSize[0], self.originalImageSize[1])

        if self.drawMethod.lower() == 'keypoint':
            self.KPcoordList.append((final_x, final_y))
            element = self.format_coordlistbar_output()
            self.coorDisplaybar.config(state='normal')
            self.coorDisplaybar.insert(tk.END, element)
            self.coorDisplaybar.config(state='disabled')
            self.draw_point(ex, ey, len(self.KPcoordList))

        elif self.drawMethod.lower() == 'bounding box':
            # if self.drawBBcoordList:
            #     print("drawBoundingBox heads out of list, Error!!!!")
            # else:
            #     self.drawBBcoordList.append([ex, ey])
            self.drawBBcoordList.append([ex, ey])
            self.BBcoordList.append([[final_x, final_y]])

    def get_release_coordinate(self, event):
        self.ok_to_change_draw_method = False
        bb_x, bb_y = event.x, event.y

        if self.resizeImgFlag:  # check image resize status
            cand_bbx, cand_bby = threshold_value(bb_x - self.canvasImgZoomX, bb_y - self.canvasImgZoomY,
                                                 self.resizedImageSize[0], self.resizedImageSize[1])
            final_x, final_y = self.de_resize_coordinates(cand_bbx, cand_bby)
        else:
            final_x, final_y = threshold_value(bb_x - self.canvasImgZoomX, bb_y - self.canvasImgZoomY,
                                               self.originalImageSize[0], self.originalImageSize[1])

        if self.drawMethod.lower() == 'bounding box':
            if len(self.drawBBcoordList) == 1:
                self.drawBBcoordList.append([bb_x, bb_y])
            else:
                print("BoundingBox tails out of list, Error!!!!")

            self.draw_bb(self.drawBBcoordList, len(self.BBcoordList))
            self.drawBBcoordList.clear()
            self.BBcoordList[-1].append([final_x, final_y])
            element = self.format_coordlistbar_output()
            self.coorDisplaybar.config(state='normal')
            self.coorDisplaybar.insert(tk.END, element)
            self.coorDisplaybar.config(state='disabled')

    def format_coordlistbar_output(self, overwrite=False):
        element = None
        if overwrite:
            result = ''
            if self.drawMethod.lower() == 'bounding box':
                bbl = self.BBcoordList
                for tmp in bbl:
                    head_x, head_y, tail_x, tail_y = tmp[0][0], tmp[0][1], tmp[1][0], tmp[1][1]
                    element = '[' + '(' + str(head_x) + ',' + str(head_y) + '),' + \
                              '(' + str(tail_x) + ',' + str(tail_y) + ')' + '] '
                    result += element
            elif self.drawMethod.lower() == 'keypoint':
                kpl = self.KPcoordList
                for tmp in kpl:
                    cx, cy = tmp[0], tmp[1]
                    element = '[' + str(cx) + ',' + str(cy) + ']'
                    result += element
            return result

        else:
            if self.drawMethod.lower() == 'bounding box':
                tmp = self.BBcoordList[-1]
                head_x, head_y, tail_x, tail_y = tmp[0][0], tmp[0][1], tmp[1][0], tmp[1][1]
                element = '[' + '(' + str(head_x) + ',' + str(head_y) + '),' + \
                          '(' + str(tail_x) + ',' + str(tail_y) + ')' + '] '
            elif self.drawMethod.lower() == 'keypoint':
                tmp = self.KPcoordList[-1]
                cx, cy = tmp[0], tmp[1]
                element = '[' + str(cx) + ',' + str(cy) + ']'
            return element

    def open_setting_window(self):
        global settingWindowCounter
        if settingWindowCounter == 1:
            self.rootSettingWindow = OutputSettingWindow(
                                            self.root,
                                            self.SaveFileStructure,
                                            self.outputPathLabel).open_sw()
            settingWindowCounter = 0
        elif settingWindowCounter == 0:
            self.rootSettingWindow.lift()

    def generate_savefile_name(self, readin_name, save_format='#'):
        result_name, _ = segment_file_name(readin_name)
        result = result_name + \
            save_format + \
            str(self.saveFileNumberCounter) + \
            '.' + self.SaveFileStructure.saveFileType
        self.saveFileNumberCounter += 1
        return result

    def save_result_show_next(self):
        if self.trvSelectFile == '':
            messagebox.showwarning(title='WARNING', message='None select files !')
            return
        result = []
        if self.drawMethod.lower() == 'keypoint':
            result = self.KPcoordList
        elif self.drawMethod.lower() == 'bounding box':
            result = self.BBcoordList

        if not result:
            messagebox.showerror(title='Error', message='Empty Content For Saving  !')
            return

        if self.SaveFileStructure.saveFilePath == '':
            messagebox.showerror(title='Error', message='Saving Path is Empty  !')
            return

        save_name = self.generate_savefile_name(self.trvSelectFile)
        complete_name = os.path.join(self.SaveFileStructure.saveFilePath, save_name)
        with open(complete_name, 'w') as f:
            f.write(str(result))

        self.show_next_img()

    def insert_empty_label(self):
        self.ok_to_change_draw_method = False
        if not self.displayImage:
            messagebox.showwarning("None image selected!")
            return

        if self.drawMethod.lower() == 'keypoint':
            self.KPcoordList.append(config['default_empty_label'])
        elif self.drawMethod.lower() == 'bounding box':
            self.BBcoordList.append([config['default_empty_label'], config['default_empty_label']])

        element = self.format_coordlistbar_output()
        self.coorDisplaybar.config(state='normal')
        self.coorDisplaybar.insert(tk.END, element)
        self.coorDisplaybar.config(state='disabled')
        self.drawTraceList.append('IEL')

    def delete_previous_label(self):
        if not self.displayImage:
            messagebox.showwarning('Warning', "None image selected!")
            return
        if self.drawMethod.lower() == 'keypoint' and self.KPcoordList:
            self.KPcoordList.pop(-1)
        elif self.drawMethod.lower() == 'bounding box' and self.BBcoordList:
            self.BBcoordList.pop(-1)
        else:
            messagebox.showinfo('Info', "Empty list! \n Nothing to delete")
            return

        # delete all display and rewrite
        self.coorDisplaybar.config(state='normal')
        self.coorDisplaybar.delete('1.0', tk.END)
        element = self.format_coordlistbar_output(True)
        if not element:
            self.ok_to_change_draw_method = True
        self.coorDisplaybar.insert(tk.END, element)
        self.coorDisplaybar.config(state='disabled')
        dtl = self.drawTraceList.pop(-1)
        if dtl != 'IEL':
            self.imageCanvas.delete(dtl)

    def show_next_img(self):
        if not self.trvSelectIid:
            return
        elif self.trvSelectIid == self.trvSize:
            messagebox.showinfo('Last file', 'End of the File list !')
            return
        self.saveFileNumberCounter = 0
        self.trvSelectIid += 1
        self.trv.selection_set(self.trvSelectIid)
        self.trv.see(self.trvSelectIid)
        self.trvSelectFile = self.trv.item(self.trvSelectIid, "text")
        select_file_path = os.path.join(self.currentWorkingPath, self.trvSelectFile)
        self.display_image(select_file_path)

    def show_previous_img(self):
        if not self.trvSelectIid:
            return
        elif self.trvSelectIid == 1:
            messagebox.showinfo('First file', 'No previous file in the list !')
            return
        self.trvSelectIid -= 1
        self.trv.selection_set(self.trvSelectIid)
        self.trv.see(self.trvSelectIid)
        self.trvSelectFile = self.trv.item(self.trvSelectIid, "text")
        select_file_path = os.path.join(self.currentWorkingPath, self.trvSelectFile)
        self.display_image(select_file_path)

    def label_method_changed(self, others):
        msgbox = None
        lcg = self.labelComboBox.get()
        # print(lcg, self.drawMethod)
        if lcg == self.drawMethod:
            return
        else:
            if not self.ok_to_change_draw_method:
                msgbox = messagebox.askyesno("Warning", "Change Label type will empty candidate list, are you sure")
            else:
                self.drawMethod = lcg
                return

        if msgbox:
            self.drawMethod = lcg
            self.clear_display(clear_img=False)
        else:
            self.labelComboBox.current(self.drawMethod_value_list.index(self.drawMethod))

    def change_label_size(self):
        tmp = self.SRSiv.get()
        self.drawPointSize = tmp
        self.drawBBsize = tmp

    def on_key_press(self, event):
        e_key = event.keysym
        ekl = config['event_key_list']
        for key, val in ekl.items():
            if e_key == val:
                print(e_key)
                self.do_command_from_keyboard(key)

    def do_command_from_keyboard(self, key):
        if key == 'SNN':
            self.saveAndNextBTN.config(relief=tk.SUNKEN)  # simulate button press
            self.saveAndNextBTN.after(200, lambda: self.saveAndNextBTN.config(relief=tk.RAISED))
            self.save_result_show_next()

        elif key == 'NI':
            self.nextImageBTN.config(relief=tk.SUNKEN)
            self.nextImageBTN.after(200, lambda: self.nextImageBTN.config(relief=tk.RAISED))
            self.show_next_img()
        elif key == 'PI':
            self.previousImageBTN.config(relief=tk.SUNKEN)
            self.previousImageBTN.after(200, lambda: self.previousImageBTN.config(relief=tk.RAISED))
            self.show_previous_img()
        elif key == 'IEL':
            self.insert_empty_label()
        elif key == 'DL':
            self.delete_previous_label()

    def clear_display(self, clear_img=True, clear_draw=True):
        self.ok_to_change_draw_method = True
        if clear_img:
            self.imageCanvas.delete('all')
        else:
            if clear_draw:
                while self.drawTraceList:
                    self.imageCanvas.delete(self.drawTraceList.pop(-1))

        self.coorDisplaybar.configure(state='normal')
        self.coorDisplaybar.delete('1.0', tk.END)
        self.coorDisplaybar.configure(state='disabled')

        self.KPcoordList = []
        self.BBcoordList = []
        self.drawTraceList = []

    def tree_view_scroll_to(self, selected_id):
        pass

class OutputSettingWindow:
    def __init__(self, parent, root_output_structure, root_output_path_label):
        self.parent = parent
        self.setting_window = tk.Toplevel(self.parent)
        self.setting_window.title("Output Setting")
        self.rootOutputPathLabel = root_output_path_label  # test part
        self.local_output_path = None

        self.btnApply = None  # apply button
        self.btnChangePath = None  # change path button

        self.setting_window.protocol('WM_DELETE_WINDOW', self.close_output_setting_without_saving)
        self.root_OPS = root_output_structure
        self.saveFolderDisplay = tk.Label(self.setting_window, text=self.root_OPS.saveFilePath,
                                          width=25, height=2,
                                          font=12, background='green', foreground="white")

        self.button()
        self.interface()

    def button(self):
        self.btnApply = tk.Button(self.setting_window, text='Apply', fg='red',
                                  command=self.apply_output_setting)
        self.btnApply.grid(row=2, column=0, columnspan=2, pady=20)

        self.btnChangePath = tk.Button(self.setting_window, text='Choose Directory',
                                       command=self.get_folder_dir)
        self.btnChangePath.grid(row=0, column=1)

    def interface(self):
        self.setting_window.columnconfigure(0, weight=2)
        self.setting_window.columnconfigure(1, weight=2)

        self.setting_window.rowconfigure(0, weight=2)
        self.setting_window.rowconfigure(1, weight=2)
        self.setting_window.rowconfigure(2, weight=2)

        self.saveFolderDisplay.config(text=self.root_OPS.saveFilePath)
        self.saveFolderDisplay.grid(row=0, column=0)

    def open_sw(self):
        x = self.parent.winfo_x()
        y = self.parent.winfo_y()
        x_offset, y_offset = self.parent.winfo_width()*0.3, self.parent.winfo_height()*0.3
        self.setting_window.geometry("500x300+%d+%d" % (x+x_offset, y+y_offset))
        return self.setting_window

    def apply_output_setting(self):
        global settingWindowCounter
        settingWindowCounter = 1
        self.root_OPS.get_value(self.local_output_path)
        self.rootOutputPathLabel.config(text=self.root_OPS.saveFilePath, anchor='w')
        create_widget_tip(self.rootOutputPathLabel)
        self.setting_window.destroy()

    def close_output_setting_without_saving(self):
        global settingWindowCounter
        settingWindowCounter = 1
        self.setting_window.destroy()

    def bring_to_top(self):
        self.setting_window.lift()

    def get_folder_dir(self):
        self.setting_window.attributes('-topmost', 0)
        folder_selected = filedialog.askdirectory()
        self.setting_window.attributes('-topmost', 1)
        self.local_output_path = folder_selected
        self.saveFolderDisplay.config(text=folder_selected, anchor='w')


class WidgetTip:

    def __init__(self, widget):
        self.widget = widget
        self.tipWindow = None
        self.id = None
        self.tipX, self.tipY = 0, 0
        self.text = None

    def show_tip(self, text):
        self.text = text
        if self.tipWindow or not self.text:
            return
        x, y, cx, cy = self.widget.bbox('insert')
        x = x + self.widget.winfo_rootx() - 57
        y = y + cy + self.widget.winfo_rooty() + 27
        self.tipWindow = tk.Toplevel(self.widget)
        self.tipWindow.wm_overrideredirect(True)
        self.tipWindow.wm_geometry("+%d+%d" % (x, y))
        label = tk.Label(self.tipWindow, text=self.text, justify='left',
                         background="#ffffe0", relief='solid', borderwidth=1,
                         font=("tahoma", "12", "normal"))
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tipWindow
        self.tipWindow = None
        if tw:
            tw.destroy()


def create_widget_tip(widget):
    wt = WidgetTip(widget)
    txt = widget.cget('text')

    def enter(event):
        # print(txt)
        wt.show_tip(txt)

    def leave(event):
        wt.hidetip()

    widget.bind('<Enter>', enter)
    widget.bind('<Leave>', leave)


if __name__ == "__main__":
    cf = GUI()
    cf.root.mainloop()
