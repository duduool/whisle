# -*- coding: utf-8 -*-
import ttk
from Tkinter import *
from ttk import *
from tools import *


class HomeFrame(ttk.Frame):

    def __init__(self, parent, app, **kwargs):
        Frame.__init__(self, parent)
        self.app = app
        self.background = get_tk_image("http://c.m.500.com/mobile/touch/images/bifen/index-header.jpg", resize=(400, 50))

        # 填充数据初始化
        matches = kwargs.get("matches", [])
        self.Max = len(matches)
        self.index = self.Max/2

        self.draw_head(parent)
        canvas = Canvas(parent, borderwidth=0)
        # 保存canvas对象
        self.Canvas = canvas
        frame = Frame(canvas)
        vsb = Scrollbar(parent, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=vsb.set)

        vsb.pack(side=RIGHT, fill=Y)
        canvas.pack(side=LEFT, fill=BOTH, expand=True)
        canvas.create_window((0, 0), window=frame, anchor=NW)

        frame.bind("<Configure>", lambda event, canvas=canvas: self.onFrameConfigure(canvas))

        if not matches: return
        # 预先生成首页所需要的frmae
        self.frames = {}
        for i in range(self.Max):
            f = Frame(frame)
            self.draw_match_list(f, matches[i])
            f.grid(row=0, column=0, sticky="nsew")
            self.frames[i] = f

        self.show_frame(self.index) # 默认显示

    def draw_head(self, parent):
        style = Style()
        style.configure("T.TFrame", background="dark gray")

        tframe = Frame(parent, width=400, height=60, style="T.TFrame")
        mframe = Frame(parent, width=400, height=20)

        # 头部对阵区
        canvas_bg = Canvas(tframe, width=400, height=50)
        canvas_bg.pack(expand=YES, fill=BOTH)
        canvas_bg.create_image(0, 0, image=self.background, anchor=NW)
        canvas_bg.create_text(150, 25, text="足球", fill="white", font="Consolas 18 bold")
        canvas_bg.create_text(250, 25, text="篮球", fill="white", font="Consolas 18 bold")
        canvas_bg.create_line(100,  8, 300,  8, fill="white", width=2)
        canvas_bg.create_line(100, 42, 300, 42, fill="white", width=2)
        canvas_bg.create_line(100,  8, 100, 42, fill="white", width=2)
        canvas_bg.create_line(200,  8, 200, 42, fill="white", width=2)
        canvas_bg.create_line(300,  8, 300, 42, fill="white", width=2)

        # 中部按钮区
        Button(mframe, text="上一期", command=lambda: self.show_left()).pack(side=LEFT, expand=YES, fill=BOTH)
        Button(mframe, text="下一期", command=lambda: self.show_right()).pack(side=LEFT, expand=YES, fill=BOTH)

        tframe.pack(side=TOP, fill=X)
        mframe.pack(side=TOP, fill=X)

    def draw_match_list(self, vframe, matches):
        style = Style()
        style.configure("BW.TLabel", foreground="dark gray")
        style.configure("BW.TFrame", background="gray")

        bframe = Frame(vframe, width=400, height=700, style="BW.TFrame")
        bframe.pack(side=TOP, fill=X)

        if not matches:
            return
        # 对阵列表布局
        Frames = []
        # 每一帧的布局，必须跟root放在同一层级，要不图片显示不出来
        for info in matches:
            fid = info.get("fid")
            order = info.get("order")
            matchtime = info.get("matchtime")
            simpleleague = info.get("simpleleague")
            tk_hlogo = info.get("homelogo")
            tk_alogo = info.get("awaylogo")
            homescore = info.get("homescore")
            awayscore = info.get("awayscore")
            homesxname = info.get("homesxname")
            awaysxname = info.get("awaysxname")
            newFrame = Frame(bframe, width=400, height=65)
            topFrame = Frame(newFrame, width=400)
            btmFrame = Frame(newFrame, width=400)
            Label(topFrame, text=order + " " + simpleleague, anchor=W, style="BW.TLabel").pack(side=LEFT)
            Label(topFrame, text=matchtime[5:], anchor=E, style="BW.TLabel").pack(side=RIGHT)
            l0 = Label(btmFrame, image=tk_hlogo, anchor=E)
            l6 = Label(btmFrame, image=tk_alogo, anchor=W)
            l1 = Label(btmFrame, text=homesxname, font=("微软雅黑", 12), anchor=W, width=7)
            l5 = Label(btmFrame, text=awaysxname, font=("微软雅黑", 12), anchor=E, width=7)
            l2 = Label(btmFrame, text=homescore, font="Consolas 23", anchor=E, width=4)
            l4 = Label(btmFrame, text=awayscore, font="Consolas 23", anchor=W, width=4)
            l3 = Label(btmFrame, text=":" if homescore else "VS", font="Consolas 10", width=2)
            for l in [l0, l1, l2, l3, l4, l5, l6]:
                l.pack(side=LEFT, fill=BOTH, expand=YES) # homelogo
                l.bind("<ButtonRelease-1>", lambda event, choice=fid: self.app.show_frame(choice))
            topFrame.grid(row=0, sticky=N+S+W+E, ipady=1)
            btmFrame.grid(row=1, sticky=N+S+W+E)
            Frames.append(newFrame)

        for i, frame in enumerate(Frames):
            # frame.grid_propagate(False)
            frame.grid(row=i, ipady=2, pady=1, sticky=N+S+W+E)

    def onFrameConfigure(self, canvas):
        '''Reset the scroll region to encompass the inner frame'''
        canvas.configure(scrollregion=canvas.bbox("all"))

    def show_left(self):
        if self.index <= 0:
            self.index = 0
        else:
            self.index -= 1
        self.show_frame(self.index)

    def show_right(self):
        if self.index >= self.Max-1:
            self.index = self.Max-1
        else:
            self.index += 1
        self.show_frame(self.index)

    def show_frame(self, cont):
        frame = self.frames[cont]
        frame.tkraise()

if __name__ == "__main__":
    root = Tk()
    root.title('比分')
    root.geometry("%sx%s+%s+%s" % (400, 800, 600, 50))
    root.resizable(width=False, height=False)

    params = {
        "background": get_tk_image("http://c.m.500.com/mobile/touch/images/bifen/index-header.jpg", resize=(400, 50)),
        "matches": [get_match_list()]
    }
    h = HomeFrame(root, {}, **params)
    root.bind_all("<MouseWheel>", lambda event, canvas=h.Canvas: canvas.yview_scroll(-1*(event.delta/120), "units"))
    root.mainloop()