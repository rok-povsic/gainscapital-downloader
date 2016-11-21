from datetime import date

from forexdata import ForexData


class Main:
    def start(self):
        date_from = date(2014, 1, 1)
        date_to = date(2016, 11, 1)

        symbols = [
            "AUD_USD",
            "EUR_USD",
            "GBP_USD",
            "NZD_USD",
            "USD_CAD",
            "USD_JPY",
        ]

        forex_data = ForexData(date_from, date_to, symbols)
        forex_data.acquire()


if __name__ == '__main__':
    Main().start()
