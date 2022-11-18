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


class GUI:

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("图像处理")
        self.rootGeometry = (1680, 960)
        self.root.geometry('%dx%d' % (self.rootGeometry[0], self.rootGeometry[1]))
        self.rootSettingWindow = None

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

        # image area
        self.imageFrame = tk.Frame(self.root, width=1360, height=800, highlightbackground="blue", highlightthickness=2)
        self.imageFrame.grid_propagate(False)
        self.imageCanvas = tk.Canvas(self.imageFrame, width=1280, height=720, bg='green')
        self.coorDisplaybar = tk.Text(self.root, padx=10, pady=10, height=1, width=150, bg="light cyan")

        # working dir area
        self.btn1 = tk.Button(self.root, text='Select directory', font=22)
        self.folderName = tk.Label(self.root, text="", font=22, background='green', foreground="white")
        self.trv = ttk.Treeview(self.root, selectmode='none', height=10)
        self.cDsb = tk.Scrollbar(self.root, orient='horizontal')

        # output setting area
        self.outputFrame = tk.Frame(self.root, bg='black', highlightbackground="cyan", highlightthickness=2)
        self.btnOutput = tk.Button(self.outputFrame, text="Output Setting", font=12)
        self.outputPathLabel = tk.Label(self.outputFrame, text="", font=12, width=20, height=1, background='firebrick4', foreground="white")
        self.SaveFileStructure = self.SFS(self.outputPathLabel)

        self.button()
        self.interface()

    class SFS:
        def __init__(self, outpathlabel):
            self.saveFilePath = ''
            self.saveFileType = 'txt'
            self.opl = outpathlabel

        def get_value(self, a):
            self.saveFilePath = a
            # print(self.saveFilePath)
            self.opl.config(text=self.saveFilePath)

    def button(self):
        self.btn1.grid(row=0, column=0, padx=5, pady=10, sticky="NW")
        self.btn1.bind("<Button-1>", self.list_file_in_folder)

        self.btnOutput.pack(side='top')
        self.btnOutput.bind("<Button-1>", self.open_setting_window)

    def interface(self):
        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=3)
        self.root.columnconfigure(2, weight=3)
        self.root.columnconfigure(3, weight=3)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=4)
        self.root.rowconfigure(2, weight=4)
        self.root.rowconfigure(3, weight=1)

        self.coorDisplaybar.grid(row=3, column=0, columnspan=2, sticky='nw', padx=5)
        self.coorDisplaybar.config(state='disabled', wrap='none', xscrollcommand=self.cDsb.set)

        self.folderName.grid(row=0, column=1, columnspan=2, padx=10, pady=15, sticky="NW")
        self.trv.grid(row=1, column=3, padx=10, pady=15, sticky="NE")
        self.imageFrame.grid(row=1, column=0, columnspan=2, rowspan=2)
        self.outputFrame.grid(row=3, column=3, sticky='e')
        self.outputPathLabel.pack(side='bottom')

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

    def trv_double_click(self, event):
        tree = event.widget
        item_name = tree.identify_row(event.y)
        if item_name:
            tags = tree.item(item_name, 'tags')
            if tags and (tags[0] == 'selectable'):
                tree.selection_set(item_name)
                select_file_name = tree.item(item_name, "text")
                select_file_path = os.path.join(self.currentWorkingPath, select_file_name)
                self.display_image(select_file_path)
                # print("you clicked on", tree.item(item_name, "text"))

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
        self.imageCanvas.pack(anchor='center', expand=True)
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

    def draw_point(self, dp_X, dp_Y, color_id):
        global Global_color_list
        color = Global_color_list[color_id-1]
        x1, y1 = (dp_X - self.drawPointSize), (dp_Y - self.drawPointSize)
        x2, y2 = (dp_X + self.drawPointSize), (dp_Y + self.drawPointSize)
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
            self.rootSettingWindow = SettingWindow(self.root, self.SaveFileStructure).open_sw()
            settingWindowCounter = 0
        elif settingWindowCounter == 0:
            self.rootSettingWindow.lift()

    def clear_display(self):
        self.imageCanvas.delete('all')

        self.coorDisplaybar.configure(state='normal')
        self.coorDisplaybar.delete('1.0', tk.END)
        self.coorDisplaybar.configure(state='disabled')

        self.coordList = []
        self.BBcoordList = []


class SettingWindow:
    def __init__(self, parent, var):
        self.parent = parent
        self.setting_window = tk.Toplevel(self.parent)
        self.setting_window.title("Output Setting")

        self.btnApply = tk.Button(self.setting_window, text='Apply', fg='red',
                                  command=self.close_output_setting_window)
        self.btnChangePath = tk.Button(self.setting_window, text='Choose Directory',
                                       command=self.get_folder_dir)

        self.setting_window.protocol('WM_DELETE_WINDOW', self.close_output_setting_window)
        self.getVar = var
        # self.saveFilePath = var.saveFilePath
        self.saveFolderDisplay = tk.Label(self.setting_window, text=self.getVar.saveFilePath,
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

        self.saveFolderDisplay.config(text=self.getVar.saveFilePath)
        self.saveFolderDisplay.grid(row=0, column=0)

    def open_sw(self):
        x = self.parent.winfo_x()
        y = self.parent.winfo_y()
        x_offset, y_offset = self.parent.winfo_width()*0.6, self.parent.winfo_height()*0.6
        self.setting_window.geometry("500x300+%d+%d" % (x+x_offset, y+y_offset))
        return self.setting_window

    def close_output_setting_window(self, ):
        global settingWindowCounter
        settingWindowCounter = 1
        self.getVar.get_value(self.getVar.saveFilePath)
        self.setting_window.destroy()

    def bring_to_top(self):
        self.setting_window.lift()

    def get_folder_dir(self):
        folder_selected = filedialog.askdirectory()
        self.getVar.saveFilePath = folder_selected
        self.saveFolderDisplay.config(text=folder_selected)

if __name__ == "__main__":
    cf = GUI()
    cf.root.mainloop()
