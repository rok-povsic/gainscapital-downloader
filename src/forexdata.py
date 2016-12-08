import requests
import zipfile
import io
import os
import csv
import math

from datetime import datetime
from dateutil.relativedelta import relativedelta


class ForexData:
    _data_dir = "../data"
    _temp_dir = "../temp"

    def __init__(self, date_from, date_to, symbols):
        self._date_from = date_from
        self._date_to = date_to
        self._symbols = symbols

    def acquire(self):
        """
        Downloads data, transforms it and writes it to disk.
        """
        if not os.path.exists(self._data_dir):
            os.mkdir(self._data_dir)
        if not os.path.exists(self._temp_dir):
            os.mkdir(self._temp_dir)

        current_date = self._date_from
        while current_date <= self._date_to:
            for symbol in self._symbols:
                symbol_dir = os.path.join(self._data_dir, symbol)
                if not os.path.exists(symbol_dir):
                    os.mkdir(symbol_dir)
                for week in (1, 2, 3, 4, 5):
                    try:
                        zip = self._acquire_zip(current_date, week, symbol)
                    except Exception as ex:
                        print("\tUnable to get zip: {}".format(ex))
                        continue
                    temp_path = self._extracted_zip(zip)
                    self._transform(temp_path, symbol_dir)
            current_date += relativedelta(months=1)
        os.rmdir(self._temp_dir)

    def _acquire_zip(self, dt, week, symbol):
        """
        Downloads zip file to a memory and returns it.
        """
        print("Downloading {}, week {}, symbol {}".format(dt, week, symbol))
        url = "http://ratedata.gaincapital.com/{:d}/{:02d} {}/{}_Week{:d}.zip".format(
            dt.year, dt.month, dt.strftime("%B"), symbol, week
        )
        request = requests.get(url)
        zip = zipfile.ZipFile(io.BytesIO(request.content))
        return zip

    def _extracted_zip(self, zip):
        """
        Exctracts zip to a temporary file and returns the path.
        """
        zip_filenames = zip.namelist()
        if len(zip_filenames) != 1:
            raise Exception("There should be exactly 1 file in the downloaded zip file.")
        zip.extract(zip_filenames[0], self._temp_dir)
        temp_path = os.path.join(self._temp_dir, zip_filenames[0])
        return temp_path

    def _transform(self, temp_path, symbol_dir):
        """
        Transforms downloaded file into multiple files, each for one day.
        """
        for dt, daily_lines in self._daily_lines(temp_path):
            final_path = self._final_csv_path(dt, symbol_dir)
            with open(final_path, "w") as file_write:
                for line in daily_lines:
                    file_write.write("{}\n".format(line))
            print("Wrote {}".format(final_path))
        os.remove(temp_path)

    def _final_csv_path(self, dt, symbol_dir):
        """
        Returns the path final CSV file should be saved at
        """
        return os.path.join(symbol_dir, "{}.csv".format(dt.strftime("%Y-%m-%d")))

    def _daily_lines(self, temp_path):
        """
        Returns a list of tuples where item 1 is date and item 2 are lines from CSV for date.
        """
        all_day_lines = []
        day_lines = []
        with open(temp_path) as file_read:
            csv_file = csv.reader(file_read, delimiter=",")
            header = next(csv_file)

            first = True
            last_date = None
            for line in csv_file:
                dtime, bid_str, ask_str = self._parsed_line(header, line)
                if first:
                    last_date = dtime.date()
                    first = False
                if last_date < dtime.date():
                    all_day_lines.append((last_date, day_lines))
                    day_lines = []
                    last_date = dtime.date()

                day_lines.append("{};{};{}".format(dtime.strftime("%Y-%m-%d %H:%M:%S.%f"), bid_str, ask_str))

        all_day_lines.append((dtime, day_lines))
        return all_day_lines

    def _parsed_line(self, header, line):
        """
        Returns datetime, bid and ask from a line. Knows how to handle two datetime formats.
        """
        dt_str = line[header.index("RateDateTime")]
        bid_str = line[header.index("RateBid")]
        ask_str = line[header.index("RateAsk")]
        if '.' in dt_str:
            dt_str_in_microsecond_precision = dt_str[:-3]
            dt = datetime.strptime(dt_str_in_microsecond_precision, "%Y-%m-%d %H:%M:%S.%f")
        else:
            dt = datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
        return dt, bid_str, ask_str

    def _files_already_downloaded(self, current_date, week, symbol):
        pass

    def _week_of_month(self, dt):
        """
        Returns the week of the month for the specified date.
        From: http://stackoverflow.com/a/16804556/365837
        """
        first_day = dt.replace(day=1)
        dom = dt.day
        adjusted_dom = dom + first_day.weekday()
        return int(math.ceil(adjusted_dom / 7.0))
