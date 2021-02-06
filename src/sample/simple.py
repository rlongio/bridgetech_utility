import csv
import operator
import os
import statistics
import datetime
import typing
import bisect

"""
Attached a CSV of an elevator operation.
There are two types of data - button_call and door_open.
We want to analyze the time it took to get to a floor from the time it was called.

A few rules:
1) The button_call can be positive or negative. That just means the person wanted to go up or down. We can treat it for now as the absolute value. So -3=3
2) The button_call can be pushed a few times before the open_door at that floor. We only care about the first time it was pressed until the open_door.
3) We can assume that if a call was 'open' (=meaning the button_call was sent, but the open_door at that floor didn't occur yet) for more than 10 minutes - then this is an anomaly and we do not want to count that button_call.


The output should be per-day the Average and Median wait times for the elevator
"""


class ElevatorLogEntries:
    def __init__(self, list: typing.List["ElevatorLogEntry"]):
        self._list = sorted(list, key=lambda x: x.date)

    def __str__(self):
        return f"length: {len(self._list)} entries: {self._list}"

    def __repr__(self):
        return f"<{self.__class__.__name__}: length: {len(self._list)}>"

    def append(self, entry: "ElevatorLogEntry"):
        self._list.insert(
            bisect.bisect_left(self._list, self._list.append(entry)), entry
        )

    def dates(self):
        return {x.date.date() for x in self._list}

    def datetimes(self):
        return {x for x in self._list}

    def floors(self):
        return {x.floor for x in self._list}

    def filter_date(self, _date: datetime.date):
        return ElevatorLogEntries([x for x in self._list if x.date.date() == _date])

    def filter_floor(self, floor: int):
        return ElevatorLogEntries(
            [x for x in self._list if abs(int(x.floor)) == int(floor)]
        )

    def split_by_date(self):
        results: dict[datetime.date, ElevatorLogEntries] = {}
        for _date in self.dates():
            results[_date] = self.filter_date(_date)
        return results


class ElevatorCall:
    def __init__(self, entry: "ElevatorLogEntry"):
        self.floor: int = entry.floor
        self.button_call: datetime.datetime = entry.date
        self.open_door: typing.Optional[datetime.datetime] = None
        self.entries: typing.List[ElevatorLogEntry] = [entry]
        self.is_complete: bool = False

    def __repr__(self):
        return f"<{self.__class__.__name__}: {vars(self)}"

    # def is_anamoly(self) -> bool:
    #     """is_anamoly returns true if length of time
    #     between button_call and door_open is longer
    #     than 10 minutes.

    #     Returns:
    #         bool: True if button_to_open is longer than 10 minutes, False otherwise
    #     """
    #     return (self.button_to_open() / 60) > 10

    # def button_to_open(self) -> int:
    #     """button_to_open returns the length in seconds between the time
    #     the button was called to the time the door was opened.

    #     Returns:
    #         int: [description]
    #     """
    #     if not self.is_complete:
    #         return 0
    #     assert self.button_call != None
    #     assert self.open_door != None
    #     return int((self.button_call - self.open_door).total_seconds())

    # def direction(self):
    #     """direction return True for up and False for down

    #     Returns:
    #         bool:
    #     """
    #     if self.to < 1:
    #         return False
    #     return True

    def add_entry(self, entry: "ElevatorLogEntry"):
        """add_entry adds an entry to the elevator call

        The method will dynamically send the entry to the correct
        set function based on type.

        Args:
            entry (ElevatorLogEntry): log entry
        """
        self.entries.append(entry)
        type_map = {
            "button_call": self._add_button_call,
            "door_open": self._set_open_door,
        }
        type_map[entry.type](entry)

    def _add_button_call(self, entry: "ElevatorLogEntry"):
        """add_button_call adds the entry to the call stack and sets
        the button call to the entry.date if it is less than the current
        self.button_call

        Args:
            entry (ElevatorLogEntry): log entry
        """
        self.button_call = (
            entry.date
            if self.button_call.timestamp() > entry.date.timestamp()
            else self.button_call
        )

    def _set_open_door(self, entry: "ElevatorLogEntry"):
        """set_open_door sets the time the door was opened
        and marks the call completed

        Args:
            entry (ElevatorLogEntry): log entry
        """
        self.open_door = entry.date
        self.is_complete = True


class ElevatorLogEntry:
    def __init__(self, id, device_id, data, type, date):
        self.id = id
        self.device_id = device_id
        self.floor = data
        self.type = type
        self._date = date
        self.date = datetime.datetime.strptime(self._date, "%Y-%m-%d %H:%M:%S")

    def __repr__(self):
        return f"<{self.__class__.__name__}: {vars(self)}"


if __name__ == "__main__":

    input_path = "data/test.csv"
    # input_path = input("Enter source file path...")
    # if not os.path.exists(input_path) or not os.path.isfile(input_path):
    #     print(f"file not found or invalid: {input_path}")
    results: typing.List[ElevatorCall] = []
    sorted_results = []
    with open(input_path) as csvfile:
        reader = csv.DictReader(csvfile)
        sorted_results = sorted(reader, key=operator.itemgetter("date"), reverse=True)
        entries = ElevatorLogEntries([ElevatorLogEntry(**x) for x in sorted_results])
        print(entries.floors())
        print(entries.filter_floor(12))
        print(entries.filter_date(datetime.datetime(2020, 1, 13, 13, 13)))
        for k, v in entries.split_by_date().items():
            print("*" * 10)
            print(k, v)
            print("*" * 10)
        exit()
    # for idx, row in enumerate(sorted_results):
    #     entry = ElevatorLogEntry(**row)
    #     if len(results) < 1 or results[len(results) - 1].is_complete == True:
    #         # if we instantiate with door_open, we know it was a test
    #         if entry.type == "door_open":
    #             continue
    #         else:
    #             results.append(ElevatorCall(entry))
    #     else:
    #         result = results[len(results) - 1].add_entry(entry)
    # x = [
    #     result.button_to_open() / 60
    #     for result in results
    #     if result.is_anamoly() is False
    # ]
    # print(results)
    # print(x)
    # print(f"Median: {round(statistics.median(x), 4)}")
    # print(f"Average: {round(statistics.mean(x), 4)}")
