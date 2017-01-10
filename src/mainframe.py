import tkinter

from datetime import date
from threading import Thread

from src.forexdata import ForexData


class MainFrame(tkinter.Frame):
    def __init__(self, parent):
        tkinter.Frame.__init__(self, parent)

        parent.title("GainsCapital Downloader")
        self._init_ui()

    def _init_ui(self):
        self._init_markets()
        self._init_dates()
        self._init_button()

    def _init_button(self):
        tkinter.Button(self, text="Start download", command=self.start_download).pack()

    def _init_dates(self):
        dts = tkinter.Frame()
        tkinter.Label(dts, text="From date:").pack(side=tkinter.LEFT)
        self.from_entry = tkinter.StringVar(value="2014/1")
        tkinter.Entry(dts, textvariable=self.from_entry, width=8).pack(side=tkinter.LEFT)
        tkinter.Label(dts, text="To date:").pack(side=tkinter.LEFT)
        self.to_entry = tkinter.StringVar(value="2017/1")
        tkinter.Entry(dts, textvariable=self.to_entry, width=8).pack()
        dts.pack()

    def _init_markets(self):
        markets = tkinter.LabelFrame()
        self.isAudUsd = tkinter.IntVar()
        tkinter.Checkbutton(markets, text="AUD/USD", variable=self.isAudUsd).pack(side=tkinter.LEFT)
        self.isEurUsd = tkinter.IntVar()
        tkinter.Checkbutton(markets, text="EUR/USD", variable=self.isEurUsd).pack(side=tkinter.LEFT)
        self.isGbpUsd = tkinter.IntVar()
        tkinter.Checkbutton(markets, text="GBP/USD", variable=self.isGbpUsd).pack(side=tkinter.LEFT)
        self.isNzdUsd = tkinter.IntVar()
        tkinter.Checkbutton(markets, text="NZD/USD", variable=self.isNzdUsd).pack(side=tkinter.LEFT)
        self.isUsdCad = tkinter.IntVar()
        tkinter.Checkbutton(markets, text="USD/CAD", variable=self.isUsdCad).pack(side=tkinter.LEFT)
        self.isUsdJpy = tkinter.IntVar()
        tkinter.Checkbutton(markets, text="USD/JPY", variable=self.isUsdJpy).pack()
        markets.pack()

    def start_download(self):
        t = Thread(target=self.start_download_thread)
        t.setDaemon(True)
        t.start()

    def start_download_thread(self):
        symbols = []

        if self.isAudUsd.get():
            symbols.append("AUD_USD")
        if self.isEurUsd.get():
            symbols.append("EUR_USD")
        if self.isGbpUsd.get():
            symbols.append("GBP_USD")
        if self.isNzdUsd.get():
            symbols.append("NZD_USD")
        if self.isUsdCad.get():
            symbols.append("USD_CAD")
        if self.isUsdJpy.get():
            symbols.append("USD_JPY")

        from_spl = self.from_entry.get().split("/")
        from_year = int(from_spl[0])
        from_month = int(from_spl[1])

        to_spl = self.to_entry.get().split("/")
        to_year = int(to_spl[0])
        to_month = int(to_spl[1])

        date_from = date(from_year, from_month, 1)
        date_to = date(to_year, to_month, 1)

        forex_data = ForexData(date_from, date_to, symbols)
        forex_data.acquire()
