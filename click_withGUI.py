import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from PIL import Image, ImageTk
import os
from tkinter import ttk

Global_color_list = ["red", "orange", "yellow", "green", "blue", "cyan", "purple",
                     "hot pink", "dark orange", "gold", "spring green", "navy",
                     "cadet blue", "magenta"]
method = ['kp', 'bb']
settingWindowCounter = 1


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
        self.root.geometry('%dx%d' % (self.rootGeometry[0], self.rootGeometry[1]))
        self.root.grid_propagate(False)
        self.root.pack_propagate(False)
        self.rootSettingWindow = None
        self.root.bind('<KeyPress>', self.onKeyPress)

        self.displayImage = None
        self.originalImageSize = None
        self.resizedImageSize = (300, 300)
        self.resizeImgFlag = False
        self.canvasImgZoomX = None
        self.canvasImgZoomY = None

        self.drawPointSize = 5
        self.drawBBsize = 5
        self.drawMethod = 'bb'
        self.drawBBcoordList = []  # list of coordinates for drawing bounding box (coordinates based on event.xy)

        self.currentWorkingPath = None
        self.coordList = []
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
        self.nextImageBTN = tk.Button(self.imageProcessFrame, text=">>[->]", font=12)
        self.previousImageBTN = tk.Button(self.imageProcessFrame, text="<<[<-]", font=12)
        self.saveAndNextBTN = tk.Button(self.imageProcessFrame, text='SAVE[Enter]', font=12)
        self.coorDisplaybar = tk.Text(self.root, padx=20, pady=10, height=1, width=170, bg="light cyan")

        # working dir area
        self.workingDirFrame = tk.Frame(self.root, bg='black', highlightbackground="green", highlightthickness=2)
        self.btn1 = tk.Button(self.workingDirFrame, text='Select directory', font=12)
        self.folderName = tk.Label(self.workingDirFrame, text="", font=12, width=20, height=1,
                                   background='green', foreground="white")
        self.trv = ttk.Treeview(self.root, selectmode='none', height=10)
        self.cDsb = tk.Scrollbar(self.root, orient='horizontal')

        # output setting area
        self.outputFrame = tk.Frame(self.root, bg='black', highlightbackground="cyan", highlightthickness=2)
        self.btnOutput = tk.Button(self.outputFrame, text="Output Setting", font=12)
        self.outputPathLabel = tk.Label(self.outputFrame, text="", font=12, width=20, height=1,
                                        background='firebrick4', foreground="white")
        self.SaveFileStructure = self.SFS()

        self.button()
        self.interface()

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
        # self.btn1.grid(row=0, column=3, padx=5, pady=10, sticky="NW")
        self.btn1.pack(side='bottom')
        self.btn1.bind("<Button-1>", self.list_file_in_folder)

        self.btnOutput.pack(side='top')
        self.btnOutput.bind("<Button-1>", self.open_setting_window)

        self.nextImageBTN.pack(side='right')
        self.nextImageBTN.bind('<Button-1>', self.show_next_img)
        self.previousImageBTN.pack(side='left')
        self.previousImageBTN.bind('<Button-1>', self.show_previous_img)
        self.saveAndNextBTN.pack()
        # self.saveAndNextBTN.bind('<Enter>', self.save_result)
        self.saveAndNextBTN.bind('<Button-1>', self.save_result_show_next)
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

        self.imageFrame.grid(row=0, column=0, columnspan=2, rowspan=3)
        self.coorDisplaybar.grid(row=3, column=0, columnspan=2, sticky='nw', padx=5)
        self.coorDisplaybar.config(state='disabled', wrap='none', xscrollcommand=self.cDsb.set)
        self.imageProcessFrame.pack(side='bottom')

        # working dir list interface
        self.workingDirFrame.grid(row=0, column=3, sticky='e', padx=(0, 10))
        self.folderName.pack(side='top')
        self.trv.grid(row=1, column=3, padx=10, pady=15, sticky="ne")

        # output area interface
        self.outputFrame.grid(row=3, column=3, sticky='e', padx=(0, 10))
        self.outputPathLabel.pack(side='bottom')

        # working list interface
        trv_s = ttk.Style()
        trv_s.theme_use('clam')
        trv_s.configure('Treeview.Heading', background="grey")
        self.trv.heading('#0', text="Working Directory", anchor='center')
        self.trv.bind("<Double-1>", self.trv_double_click)

    def list_file_in_folder(self, other_para):
        # messagebox.showinfo("window1", "bing!")
        folder_selected = filedialog.askdirectory()
        self.currentWorkingPath = folder_selected
        self.folderName.config(text=folder_selected)

        for item in self.trv.get_children():
            self.trv.delete(item)

        i = 1
        for root, subdir, files in os.walk(folder_selected):
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
                # print(self.trvSelectIid, "!@##$")
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
        if self.drawMethod == 'kp':
            self.imageCanvas.tag_bind(img_canv, '<Button-1>', self.get_press_coordinate)
        elif self.drawMethod == 'bb':
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
        self.imageCanvas.create_oval(x1, y1, x2, y2, fill=color)

    def draw_bb(self, bb_list, color_id):
        global Global_color_list
        color = Global_color_list[color_id-1]
        x1, y1 = bb_list[0][0], bb_list[0][1]
        x2, y2 = bb_list[1][0], bb_list[1][1]
        self.imageCanvas.create_rectangle(x1, y1, x2, y2, outline=color, width=self.drawBBsize)

    def get_press_coordinate(self, event):
        Cx = event.x
        Cy = event.y

        if self.drawMethod == 'kp':
            self.draw_point(Cx, Cy, len(self.coordList))

        if self.resizeImgFlag:
            cand_x, cand_y = threshold_value(Cx - self.canvasImgZoomX, Cy - self.canvasImgZoomY,
                                             self.resizedImageSize[0], self.resizedImageSize[1])
            final_x, final_y = self.de_resize_coordinates(cand_x, cand_y)
        else:
            final_x, final_y = threshold_value(Cx - self.canvasImgZoomX, Cy - self.canvasImgZoomY,
                                               self.originalImageSize[0], self.originalImageSize[1])

        if self.drawBBcoordList:
            print("drawBoundingBox heads out of list, Error!!!!")
        else:
            self.drawBBcoordList.append([Cx, Cy])
        if self.drawMethod == 'kp':
            self.coordList.append((final_x, final_x))
            element = self.format_coordlistbar_output()
            # element = '[' + str(final_x) + ',' + str(final_y) + ']'
            self.coorDisplaybar.config(state='normal')
            self.coorDisplaybar.insert(tk.END, element)
            self.coorDisplaybar.config(state='disabled')
        elif self.drawMethod == 'bb':
            self.BBcoordList.append([[final_x, final_y]])

    def get_release_coordinate(self, event):
        bb_X, bb_Y = event.x, event.y

        if self.resizeImgFlag:  # check image resize status
            cand_bbx, cand_bby = threshold_value(bb_X - self.canvasImgZoomX, bb_Y - self.canvasImgZoomY,
                                                 self.resizedImageSize[0], self.resizedImageSize[1])
            final_x, final_y = self.de_resize_coordinates(cand_bbx, cand_bby)
        else:
            final_x, final_y = threshold_value(bb_X - self.canvasImgZoomX, bb_Y - self.canvasImgZoomY,
                                               self.originalImageSize[0], self.originalImageSize[1])

        if len(self.drawBBcoordList) == 1:
            self.drawBBcoordList.append([bb_X, bb_Y])
        else:
            print("BoundingBox tails out of list, Error!!!!")
        if self.drawMethod == 'bb':
            self.draw_bb(self.drawBBcoordList, len(self.BBcoordList))
            self.drawBBcoordList = []
            self.BBcoordList[-1].append([final_x, final_y])
            element = self.format_coordlistbar_output()
            self.coorDisplaybar.config(state='normal')
            self.coorDisplaybar.insert(tk.END, element)
            self.coorDisplaybar.config(state='disabled')

    def format_coordlistbar_output(self):
        element = None
        if self.drawMethod == 'bb':
            tmp = self.BBcoordList[-1]
            head_x, head_y, tail_x, tail_y = tmp[0][0], tmp[0][1], tmp[1][0], tmp[1][1]
            element = '[' + '(' + str(head_x) + ',' + str(head_y) + '),' + \
                      '(' + str(tail_x) + ',' + str(tail_y) + ')' + '] '
        elif self.drawMethod == 'kp':
            tmp = self.coordList[-1]
            cx, cy = tmp[0], tmp[1]
            element = '[' + str(cx) + ',' + str(cy) + ']'
        return element

    def open_setting_window(self, kg):
        global settingWindowCounter
        if settingWindowCounter == 1:
            self.rootSettingWindow = OutputSettingWindow(
                                            self.root,
                                            self.SaveFileStructure,
                                            self.outputPathLabel).open_sw()
            settingWindowCounter = 0
        elif settingWindowCounter == 0:
            self.rootSettingWindow.lift()

    def update_output_path_label(self):
        self.outputPathLabel.config(text=self.SaveFileStructure.saveFilePath)

    def generate_savefile_name(self, readin_name, save_format='#'):
        result_name, _ = segment_file_name(readin_name)
        result = result_name + \
            save_format + \
            str(self.saveFileNumberCounter) + \
            '.' + self.SaveFileStructure.saveFileType
        self.saveFileNumberCounter += 1
        return result

    def save_result_show_next(self, other):
        if self.trvSelectFile == '':
            messagebox.showwarning(title='WARNING', message='None select files !')
            return
        result = []
        if self.drawMethod == 'kp':
            result = self.coordList
        elif self.drawMethod == 'bb':
            result = self.BBcoordList

        if not result:
            messagebox.showerror(title='Error', message='Empty Content For Saving  !')
            return

        if self.SaveFileStructure.saveFilePath == '':
            messagebox.showerror(title='Error', message='Saving Path is Empty  !')
            return
        # print(self.trvSelectIid)
        save_name = self.generate_savefile_name(self.trvSelectFile)
        complete_name = os.path.join(self.SaveFileStructure.saveFilePath, save_name)
        with open(complete_name, 'w') as f:
            f.write(str(result))

        self.show_next_img()

    def show_next_img(self):
        if self.trvSelectIid == self.trvSize:
            messagebox.showinfo('Last file', 'End of the File list !')
            return
        self.trvSelectIid += 1
        self.trv.selection_set(self.trvSelectIid)
        # cur_item = self.trv.focus(self.trvSelectIid)
        self.trvSelectFile = self.trv.item(self.trvSelectIid, "text")
        select_file_path = os.path.join(self.currentWorkingPath, self.trvSelectFile)
        self.display_image(select_file_path)

        # self.saveFileNumberCounter = 0
        # cur_item = self.trv.focus()
        # self.trvSelectFile = self.trv.item(cur_item, "text")
        # select_file_path = os.path.join(self.currentWorkingPath, self.trvSelectFile)
        # self.display_image(select_file_path)

    def show_previous_img(self):
        if self.trvSelectIid == 1:
            messagebox.showinfo('First file', 'No previous file in the list !')
            return
        self.trvSelectIid -= 1
        self.trv.selection_set(self.trvSelectIid)
        # cur_item = self.trv.focus(self.trvSelectIid)
        self.trvSelectFile = self.trv.item(self.trvSelectIid, "text")
        select_file_path = os.path.join(self.currentWorkingPath, self.trvSelectFile)
        self.display_image(select_file_path)
        # rows = self.trv.selection()
        # for row in rows:
        #     self.trv.next()
        #     self.trv.move(row, self.trv.parent(row), self.trv.index(row)-1)

        # self.saveFileNumberCounter = 0
        # cur_item = self.trv.focus()
        # self.trvSelectFile = self.trv.item(cur_item, "text")
        # select_file_path = os.path.join(self.currentWorkingPath, self.trvSelectFile)
        # self.display_image(select_file_path)

    def onKeyPress(self, event):
        ch = event.keysym
        print(ch)
        print("key pressed")
        # if '1' <= ch <= maxkey:
            # Retrieve this button from the dict
            # b = buttons[ch]

            # Simulate pushing the button
            # b.config(relief=tk.SUNKEN)
            # button_cb(ch)

            # Let it pop back up after 200 milliseconds
            # b.after(200, lambda: b.config(relief=tk.RAISED))
    def clear_display(self):
        self.imageCanvas.delete('all')

        self.coorDisplaybar.configure(state='normal')
        self.coorDisplaybar.delete('1.0', tk.END)
        self.coorDisplaybar.configure(state='disabled')

        self.coordList = []
        self.BBcoordList = []


class OutputSettingWindow:
    def __init__(self, parent, root_output_structure, root_output_path_label):
        self.parent = parent
        self.setting_window = tk.Toplevel(self.parent)
        self.setting_window.title("Output Setting")
        self.rootOutputPathLabel = root_output_path_label  # test part
        self.local_output_path = None

        self.btnApply = tk.Button(self.setting_window, text='Apply', fg='red',
                                  command=self.apply_output_setting)
        self.btnChangePath = tk.Button(self.setting_window, text='Choose Directory',
                                       command=self.get_folder_dir)

        self.setting_window.protocol('WM_DELETE_WINDOW', self.close_output_setting_without_saving)
        self.root_OPS = root_output_structure
        self.saveFolderDisplay = tk.Label(self.setting_window, text=self.root_OPS.saveFilePath,
                                          width=25, height=2,
                                          font=12, background='green', foreground="white")

        self.button()
        self.interface()

    def button(self):
        self.btnApply.grid(row=2, column=0, columnspan=2, pady=20)
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
        x_offset, y_offset = self.parent.winfo_width()*0.6, self.parent.winfo_height()*0.6
        self.setting_window.geometry("500x300+%d+%d" % (x+x_offset, y+y_offset))
        return self.setting_window

    def apply_output_setting(self):
        global settingWindowCounter
        settingWindowCounter = 1
        self.root_OPS.get_value(self.local_output_path)
        self.rootOutputPathLabel.config(text=self.root_OPS.saveFilePath)
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
        self.saveFolderDisplay.config(text=folder_selected)


if __name__ == "__main__":
    cf = GUI()
    cf.root.mainloop()
