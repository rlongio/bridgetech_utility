import csv
import operator
import os
import statistics
import datetime
import typing
import bisect
import collections

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

"""
* get list of values
* sort by date

iterate:

if type is button_call:
    results[floor]
"""


ElevatorOperationRecord = collections.namedtuple(
    "ElevatorOpeartionRecord", ["start", "other", "end"]
)


class ElevatorOperation:
    def __init__(self, record: ElevatorOperationRecord):
        self._record = record

    def __repr__(self):
        return f"<{self.__class__.__name__}: {vars(self)}>"

    def is_anamoly(self) -> bool:
        if self._record.start is None or self._record.end is None:
            return True
        if self.button_to_open() > 60 * 10:
            return True
        if self.button_to_open() < 0:
            return True
        return False

    def button_to_open(self) -> int:
        """button_to_open returns the length in seconds between the time
        the button was called to the time the door was opened.

        Returns:
            int: [description]
        """
        if self._record.start is None or self._record.end is None:
            return -1
        return int((self._record.end.date - self._record.start.date).total_seconds())

    def direction(self):
        """direction return True for up and False for down

        Returns:
            bool:
        """
        return bool(self._record.start.floor)


class ElevatorOperations:
    def __init__(self, operations: typing.List["ElevatorOperation"]):
        self._operations = operations

    def __repr__(self):
        return f"<{self.__class__.__name__}: {vars(self)}>"

    def __iter__(self):
        return iter(self._operations)

    def average(self):
        try:
            return statistics.mean(
                x.button_to_open() for x in self._operations if not x.is_anamoly()
            )
        except Exception as e:
            return -1

    def median(self):
        try:
            return statistics.median(
                x.button_to_open() for x in self._operations if not x.is_anamoly()
            )
        except Exception as e:
            return -1

    def print_report(self):
        for item in self._operations:
            print(item._record)
            print(item.button_to_open())

    @staticmethod
    def from_log_entries(entries: "ElevatorLogEntries") -> "ElevatorOperations":
        dates: list[ElevatorLogEntries] = [
            entry for entry in entries.split_by_date().values()
        ]

        floors: list[ElevatorLogEntries] = [
            x for _date in dates for x in _date.split_by_floor().values()
        ]

        results: typing.List["ElevatorOperation"] = []
        start = None
        other = []
        for entry in [entry for x in floors for entry in x]:
            if entry.type == "button_call" and start is None:
                start = entry
            elif entry.type == "button_call" and start is not None:
                other.append(entry)
            else:
                record = ElevatorOperationRecord(start, other, entry)
                operation = ElevatorOperation(record)
                results.append(operation)
                start, other = None, []
        return ElevatorOperations(results)


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


class ElevatorLogEntries:
    def __init__(self, list: typing.List["ElevatorLogEntry"]):
        self._list = sorted(list, key=lambda x: x.date)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._list}>"

    def __iter__(self):
        return self._list.__iter__()

    def append(self, entry: "ElevatorLogEntry"):
        self._list.insert(
            bisect.bisect_left(self._list, self._list.append(entry)), entry
        )

    def dates(self) -> set[datetime.date]:
        return {x.date.date() for x in self._list}

    def datetimes(self) -> set[datetime.datetime]:
        return {x.date for x in self._list}

    def floors(self) -> set[int]:
        return {x.floor for x in self._list}

    def filter_date(self, _date: datetime.date) -> "ElevatorLogEntries":
        return ElevatorLogEntries([x for x in self._list if x.date.date() == _date])

    def filter_floor(self, floor: int) -> "ElevatorLogEntries":
        return ElevatorLogEntries(
            [x for x in self._list if abs(int(x.floor)) == int(floor)]
        )

    def split_by_date(self) -> dict[datetime.date, "ElevatorLogEntries"]:
        results: dict[datetime.date, ElevatorLogEntries] = {}
        for _date in self.dates():
            results[_date] = self.filter_date(_date)
        return results

    def split_by_floor(self) -> dict[int, "ElevatorLogEntries"]:
        results: dict[int, ElevatorLogEntries] = {}
        for floor in self.floors():
            results[floor] = self.filter_floor(floor)
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


if __name__ == "__main__":

    input_path = "data/query_result.csv"
    # input_path = input("Enter source file path...")
    # if not os.path.exists(input_path) or not os.path.isfile(input_path):
    #     print(f"file not found or invalid: {input_path}")
    results: typing.List[ElevatorCall] = []
    sorted_results = []
    with open(input_path) as csvfile:
        reader = csv.DictReader(csvfile)
        sorted_results = sorted(reader, key=operator.itemgetter("date"), reverse=True)
        entries = ElevatorLogEntries(
            [ElevatorLogEntry(**x) for x in sorted_results]
        ).split_by_date()
        for k, v in entries.items():
            # test = ElevatorOperations.from_log_entries(v)
            # [print(x, "\n") for x in test]
            print(
                f"{k}: average {round(ElevatorOperations.from_log_entries(v).average(), 2)} seconds   median: {round(ElevatorOperations.from_log_entries(v).median(), 2)} seconds"
            )
