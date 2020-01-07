import psutil
import os
import platform
import tkinter as tk
from tkinter import ttk
import xtra_widgets as xw
import reader
import datetime
from time import sleep
import matplotlib
from matplotlib import pyplot as plt
import matplotlib.dates as mdates
from matplotlib.lines import Line2D
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
matplotlib.use('TkAgg')


TITLE_FONT = ('Helvetica', 20, 'bold')
FIELD_FONT = ('Helvetica', 10, 'bold')
FIELD_CONTENT_FONT = ('Helvetica', 10)

HEATMAP_OPTIMIZATION_FACTOR = 0


class NetTrackerApp(tk.Tk):

    def __init__(self, *args, **kwargs):
        tk.Tk.__init__(self, *args, **kwargs)
        self.title("Internet Connection Tracker (ICT beta v0.1) - by Everton Colombo")
        container = tk.Frame(self)

        container.pack(side="top", fill="both", expand=True)

        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {}

        for F in (HomePage,):
            frame = F(container, self)

            self.frames[F] = frame

            frame.grid(row=0, column=0, sticky="nsew")

        self.show_frame(HomePage)

    def show_frame(self, cont):
        frame = self.frames[cont]
        if hasattr(frame, "geometry"):  self.geometry(frame.geometry)
        if hasattr(frame, "on_enter"): frame.on_enter()
        frame.tkraise()


class HomePage(tk.Frame):

    def on_enter(self):
        print("on_enter() called in HomePage")
        self.update_outages_list()
        self.update_heatmap()

    def __init__(self, parent, controller):
        tk.Frame.__init__(self, parent)

        self.title = tk.Label(self, text="Home", font=TITLE_FONT)
        self.summary_frame = tk.LabelFrame(self, text="Summary")
        self.status_frame = tk.LabelFrame(self.summary_frame, text="Status")
        self.status_mlabel = tk.Label(self.status_frame, font=("Helvetica", 20, "bold"))
        self.status_tlabel = tk.Label(self.status_frame)
        self.status_onb = ttk.Button(self.status_frame, text="Switch On", command=lambda: self.update_tracker(1))
        self.status_offb = ttk.Button(self.status_frame, text="Switch Off", command=lambda: self.update_tracker(0))
        self.update_tracker(-1)
        self.outages_frame = tk.LabelFrame(self.summary_frame, text="Outages", padx=5, pady=5)
        self.outages_timeperiod_frame = tk.Frame(self.outages_frame, relief='sunken', bd=2)
        self.outages_timeperiod_var = tk.IntVar()
        self.outages_timeperiod_today_rb = tk.Radiobutton(self.outages_timeperiod_frame, text="Today",
                                                          variable=self.outages_timeperiod_var, value=1,
                                                          command=self.update_outages_list)
        self.outages_timeperiod_week_rb = tk.Radiobutton(self.outages_timeperiod_frame, text="This Week",
                                                         variable=self.outages_timeperiod_var, value=2,
                                                         command=self.update_outages_list)
        self.outages_timeperiod_month_rb = tk.Radiobutton(self.outages_timeperiod_frame, text="This Month",
                                                          variable=self.outages_timeperiod_var, value=3,
                                                          command=self.update_outages_list)
        self.outages_timeperiod_alltime_rb = tk.Radiobutton(self.outages_timeperiod_frame, text="All Time",
                                                            variable=self.outages_timeperiod_var, value=4,
                                                            command=self.update_outages_list)
        self.outages_timeperiod_var.set(1)      # sets default timep to 'today'
        self.outages_scrollbox = xw.ScrollBox(self.outages_frame, width=47)
        self.outages_info = tk.Frame(self.outages_frame, bd=2, relief='sunken')

        self.outages_outage_count_l = tk.Label(self.outages_info, text="Number of Outages: ", font=FIELD_FONT)
        self.outages_outage_count_v = tk.StringVar()
        self.outages_outage_count_f = tk.Label(self.outages_info, textvariable=self.outages_outage_count_v,
                                               font=FIELD_CONTENT_FONT)
        self.outages_oscillation_count_l = tk.Label(self.outages_info, text="Number of Oscillations: ", font=FIELD_FONT)
        self.outages_oscillation_count_v = tk.StringVar()
        self.outages_oscillation_count_f = tk.Label(self.outages_info, textvariable=self.outages_oscillation_count_v,
                                                    font=FIELD_CONTENT_FONT)
        self.outages_test_time_l = tk.Label(self.outages_info, text="Test Time: ", font=FIELD_FONT)
        self.outages_test_time_v = tk.StringVar()
        self.outages_test_time_f = tk.Label(self.outages_info, textvariable=self.outages_test_time_v,
                                            font=FIELD_CONTENT_FONT)
        self.outages_offline_time_l = tk.Label(self.outages_info, text="Offline Time: ", font=FIELD_FONT)
        self.outages_offline_time_v = tk.StringVar()
        self.outages_offline_time_f = tk.Label(self.outages_info, textvariable=self.outages_offline_time_v,
                                               font=FIELD_CONTENT_FONT)
        self.outages_oscillation_time_l = tk.Label(self.outages_info, text="Oscillation Time: ", font=FIELD_FONT)
        self.outages_oscillation_time_v = tk.StringVar()
        self.outages_oscillation_time_f = tk.Label(self.outages_info, textvariable=self.outages_oscillation_time_v,
                                                   font=FIELD_CONTENT_FONT)
        self.outages_loss_percentage_l = tk.Label(self.outages_info, text="Loss Percentage: ", font=FIELD_FONT)
        self.outages_loss_percentage_v = tk.StringVar()
        self.outages_loss_percentage_f = tk.Label(self.outages_info, textvariable=self.outages_loss_percentage_v,
                                                  font=FIELD_CONTENT_FONT)
        self.outages_oscillation_percentage_l = tk.Label(self.outages_info, text="Oscillation Percentage: ",
                                                         font=FIELD_FONT)
        self.outages_oscillation_percentage_v = tk.StringVar()
        self.outages_oscillation_percentage_f = tk.Label(self.outages_info,
                                                         textvariable=self.outages_oscillation_percentage_v,
                                                         font=FIELD_CONTENT_FONT)

        self.outages_update_button = ttk.Button(self.outages_frame, text="Update List",
                                                command=self.update_outages_list)
        self.heatmap_frame = tk.LabelFrame(self, text="HeatMap")
        self.graph_frame = tk.Frame(self.heatmap_frame)
        self.figure = Figure(figsize=(6, 4), dpi=100)
        self.plt = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, self.graph_frame)
        self.canvas.draw()
        self.toolbar = NavigationToolbar2Tk(self.canvas, self.graph_frame)
        self.toolbar.update()
        self.ax = self.figure.gca()
        self.heatmap_update_button = ttk.Button(self.heatmap_frame, text="Update Heatmap")
        # Configuring the Figure:
        self.figure.subplots_adjust(left=0.1)
        self.plt.set_title("Heatmap View")
        self.ax.legend(handles=[Line2D([0], [0], marker='o', color='lime', label='Online'),
                                Line2D([0], [0], marker='o', color='r', label='Offline'),
                                Line2D([0], [0], marker='o', color='blue', label='Unknown')])
        # self.ax.yaxis.set_major_locator(plt.MaxNLocator(20))
        # self.ax.yaxis.set_minor_locator(mdates.MinuteLocator(byminute=))
        # self.ax.yaxis.set_major_formatter(mdates.DateFormatter('%H:%M'))
        self.ax.grid(True)

        self.title.grid(row=0, column=0, columnspan=100, sticky='nw')
        self.summary_frame.grid(row=1, column=0, sticky='nsew')
        self.status_frame.grid(row=0, column=0, sticky='nsew')
        self.status_mlabel.grid(row=0, column=0, sticky='w', columnspan=2)
        self.status_tlabel.grid(row=1, column=0, sticky='w', columnspan=2)
        self.status_onb.grid(row=2, column=0, sticky='ew')
        self.status_offb.grid(row=2, column=1, sticky='ew')
        self.outages_frame.grid(row=1, column=0, sticky='nsew')
        self.outages_timeperiod_frame.grid(row=0, column=0, sticky='ew')
        self.outages_timeperiod_today_rb.grid(row=0, column=0, sticky='w')
        self.outages_timeperiod_week_rb.grid(row=1, column=0, sticky='w')
        self.outages_timeperiod_month_rb.grid(row=2, column=0, sticky='w')
        self.outages_timeperiod_alltime_rb.grid(row=3, column=0, sticky='w')
        self.outages_scrollbox.grid(row=1, column=0, sticky='nsew')

        self.outages_info.grid(row=2, column=0, sticky='nsew')
        self.outages_test_time_l.grid(row=0, column=0, sticky='w')
        self.outages_test_time_f.grid(row=0, column=1, sticky='w')
        self.outages_outage_count_l.grid(row=1, column=0, sticky='w')
        self.outages_outage_count_f.grid(row=1, column=1, sticky='w')
        self.outages_oscillation_count_l.grid(row=2, column=0, sticky='w')
        self.outages_oscillation_count_f.grid(row=2, column=1, sticky='w')
        self.outages_offline_time_l.grid(row=3, column=0, sticky='w')
        self.outages_offline_time_f.grid(row=3, column=1, sticky='w')
        self.outages_oscillation_time_l.grid(row=4, column=0, sticky='w')
        self.outages_oscillation_time_f.grid(row=4, column=1, sticky='w')
        self.outages_loss_percentage_l.grid(row=5, column=0, sticky='w')
        self.outages_loss_percentage_f.grid(row=5, column=1, sticky='w')
        self.outages_oscillation_percentage_l.grid(row=6, column=0, sticky='w')
        self.outages_oscillation_percentage_f.grid(row=6, column=1, sticky='w')

        self.outages_update_button.grid(row=3, column=0, sticky='w')

        # Heatmap:

        self.heatmap_frame.grid(row=1, column=1, sticky='nsew')
        self.heatmap_update_button.grid(row=1, column=0, sticky='w')
        self.graph_frame.grid(row=0, column=0, sticky='nsew')
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.X)
        self.canvas._tkcanvas.pack(side=tk.BOTTOM, fill=tk.X)

    def update_tracker(self, command: int = -1):
        """
        Updates stuff from self.status_frame
        :param command: (int, default = -1) 1: switches tracker ON, 0: switches tracker OFF, -1: maintains tracker's
                        state while updating widgets.
        :return: nothing
        """

        if command is 1:
            pass
        elif command is 0:
            if platform.system() == "Windows":
                with open(os.path.join(os.environ["APPDATA"], "ICT/collector.pid"), 'r') as file:
                    pid = int(file.read().strip('\n'))
            elif platform.system() == "Linux":
                with open("data/collector.pid", 'r') as file:
                    pid = int(file.read().strip('\n'))
            if psutil.pid_exists(pid):
                os.kill(pid, 1)
                try:
                    sleep(1)
                    os.kill(pid, 1)
                except:
                    pass


        if platform.system() == "Windows":
            with open(os.path.join(os.environ["APPDATA"], "ICT/collector.pid"), 'r') as file:
                pid = int(file.read().strip('\n'))
        elif platform.system() == "Linux":
            with open("data/collector.pid", 'r') as file:
                pid = int(file.read().strip('\n'))
        if psutil.pid_exists(pid):
            if platform.system() == "Windows":
                with open(os.path.join(os.environ["APPDATA"],
                                       "ICT/data/{}.trck".format(datetime.datetime.now().strftime("%d_%m%_%Y"))), 'r')\
                        as file:
                    state = "Online" if float(file.readlines()[-1]) > -1 else "Offline"
            elif platform.system() == "Linux":
                with open("data/{}.trck".format(datetime.datetime.now().strftime("%d_%m_%Y")), 'r') as file:
                    state = "Online" if float(file.readlines()[-1]) > -1 else "Offline"

            self.status_mlabel.config(text=state, fg="green" if state == "Online" else "red")
            self.status_tlabel.config(text="Tracking is on and the computer is Online" if state == "Online" else
                                      "Tracking is on, but the computer is Offline")
            self.status_onb.config(state="disabled")
            self.status_offb.config(state="normal")
        else:
            self.status_mlabel.config(text="Unknown", fg="blue")
            self.status_tlabel.config(text="Tracking has been switched off")
            self.status_onb.config(state="normal")
            self.status_offb.config(state="disabled")


    def update_outages_list(self):
        print("HomePage.update_outages_list() called")
        self.outages_scrollbox.clear()
        organizeds = []

        if self.outages_timeperiod_var.get() != 4:
            ite = 1
            # if self.outages_timeperiod_var.get() == 1:
            #     pass
            if self.outages_timeperiod_var.get() == 2:
                ite = 7
            elif self.outages_timeperiod_var.get() == 3:
                ite = 30

            for i in range(ite):
                try:
                    organizeds.append(reader.organize((datetime.datetime.now() - datetime.timedelta(days=i)).strftime(
                        "%d/%m/%Y")))
                except FileNotFoundError:
                    # print("File Not Found")
                    break
            print(organizeds)
        else:
            i = 0
            while True:
                try:
                    # print((datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%d/%m/%Y"))
                    organizeds.append(reader.organize((datetime.datetime.now() - datetime.timedelta(days=i)).strftime(
                        "%d/%m/%Y")))
                    i += 1
                except FileNotFoundError:
                    break

        info = []
        for track in organizeds:
            analysis = reader.get_analysis(track)
            self.outages_scrollbox.special_insert(0, tuple(analysis["outage_times"]))
            info.append([analysis["outage_count"], analysis["oscillation_count"], analysis["total_test_minutes"],
                         analysis["total_minutes_lost"], analysis["oscillation_minutes"]])

        # Update info labels:
        outage_count = 0
        oscillation_count = 0
        test_mins = 0
        mins_lost = 0
        osc_mins = 0
        for i in info:
            outage_count += i[0]
            oscillation_count += i[1]
            test_mins += i[2]
            mins_lost += i[3]
            osc_mins += i[4]

        self.outages_outage_count_v.set(str(outage_count))
        self.outages_oscillation_count_v.set(str(oscillation_count))
        self.outages_test_time_v.set("{} hour(s) and {} minute(s)".format(test_mins // 60, test_mins % 60))
        self.outages_offline_time_v.set("{} hour(s) and {} minute(s)".format(mins_lost // 60, mins_lost % 60))
        self.outages_oscillation_time_v.set("{} hour(s) and {} minute(s)".format(osc_mins // 60, osc_mins % 60))
        self.outages_loss_percentage_v.set("{0:.2f}% ({1}/{2})".format(100 * (mins_lost / test_mins), mins_lost,
                                                                       test_mins))
        self.outages_oscillation_percentage_v.set("{0:.2f}% ({1}/{2})".format(100 * (osc_mins / test_mins), osc_mins,
                                                                              test_mins))

    def update_heatmap(self):
        # a = reader.organize("16/12/2019")
        # reader.fix(a)
        # for li in a:
        #     self.plt.scatter("Today", li[1], color=('lime' if li[2] > 0 else 'r' if li[2] > -2 else 'b'))
        fixed_trackings = []
        for i in range(3):
            try:
                print((datetime.datetime.now() - datetime.timedelta(days=i)).strftime("%d/%m/%Y"))
                fixed_trackings.append(reader.fix(reader.organize((datetime.datetime.now() -
                                                                   datetime.timedelta(days=i)).strftime(
                                "%d/%m/%Y"))))
                print("ft: ", fixed_trackings)
            except FileNotFoundError:
                print("HMP - File Not Found")
                break

        # i = 0
        # o = False
        cert = 0
        for tracking in reversed(fixed_trackings):      # reversed because we appended from current date
            # i += 1
            for li in tracking:
                # if cert is 0:
                #     try:
                #         for i in range(1, HEATMAP_OPTIMIZATION_FACTOR):
                #             if li[2] == tracking[tracking.index(li) + i][2]:
                #                 cert += 1
                #     except IndexError:
                #         pass
                self.plt.scatter(li[1].split(' ')[0], datetime.datetime(year=2010, month=1, day=1,
                                                                        hour=int(li[1].split(' ')[1].split(':')[0]),
                                                                        minute=int(li[1].split(' ')[1].split(':')[1])),
                                 color=('lime' if li[2] > 0 else 'r' if li[2] > -2 else 'b'))
                # else:
                #     cert -= 1
                # if li[2] is not -1 and o:
                #     o = False
                # if li[2] == -1 and not o:
                #     o = True
                #     self.ax.annotate("",
                #                 xy=(li[1].split(" ")[0], li[1].split(' ')[1]), xycoords='data',
                #                 xytext=(0.1 if i is 1 else 0.4 if i is 2 else 0.9, 0.5), textcoords='axes fraction',
                #                 arrowprops=dict(arrowstyle="->",
                #                                 connectionstyle="arc3"),
                #                 )


if __name__ == "__main__":
    a = NetTrackerApp()
    a.mainloop()


# TODO: implement email
# TODO: translate
