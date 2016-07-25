# coding: utf-8
from Tkinter import *
from ttk import *
import datetime
from tools import *
from detail import DetailFrame
from home import HomeFrame


class App(object):

    # 需要初始化所有构造frame的数据
    def initialize(self):
        Home_data = {}
        Deta_Data = {}
        matches = []

        today = datetime.datetime.today()
        for d in [-2, -1, 0, 1]:
            e = today + datetime.timedelta(days=d)
            e = e.strftime("%Y-%m-%d")
            matches.append(get_match_list(e))
        Home_data = {
            "matches": matches
        }

        # 获取所有detail所需的数据
        for item in matches:
            for info in item:
                fid = info.get("fid")
                Deta_Data[fid] = {
                    "fid":        info.get("fid"),
                    "homelogo":   info.get("homelogo"),
                    "awaylogo":   info.get("awaylogo"),
                    "homescore":  info.get("homescore"),
                    "awayscore":  info.get("awayscore"),
                    "homesxname": info.get("homesxname"),
                    "awaysxname": info.get("awaysxname"),
                }

        ret  = {
            "home_data": Home_data,
            "deta_data": Deta_Data
        }
        return ret

    def __init__(self):
        root = Tk()
        root.title('比分')
        root.geometry("%sx%s+%s+%s" % (400, 800, 600, 50))
        root.resizable(width=False, height=False)

        container = Frame(root)
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        data = self.initialize()
        home_data = data.get("home_data", {})
        deta_data = data.get("deta_data", {})

        self.frames = {}
        self.canvas = {}
        fore = Frame(container)
        home = HomeFrame(fore, self, **home_data)
        self.frames["fore"] = fore
        self.canvas["fore"] = home

        fore.grid(row=0, column=0, sticky="nsew")

        # 预先生成好所有需要的frame，暂时没想到好的办法- -!
        for k, v in deta_data.iteritems():
            frame = Frame(container)
            canva = DetailFrame(frame, self, **v)
            self.frames[k] = frame
            self.canvas[k] = canva
            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame("fore")

        root.mainloop()

    # frame之间切换
    def show_frame(self, choice):
        frame = self.frames.get(choice)
        canva = self.canvas.get(choice)
        frame.tkraise()
        # frame之间切换的时候重新绑定各自的鼠标滚轮scroll事件
        frame.bind_all("<MouseWheel>", lambda event, canvas=canva.Canvas: self.onMouseWheel(event, canvas))

    def onMouseWheel(self, event, canvas):
        canvas.yview_scroll(-1*(event.delta/120), "units")

if __name__ == "__main__":
    app = App()
