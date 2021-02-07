"""
Utility for caluclating the average and median of elevator operations.

Author: Ryan Long
Email: ryan@rlong.io
"""

import csv
import operator
import statistics
import datetime
import typing
import bisect
import collections


# elevator operation record
ElevatorOperationRecord = collections.namedtuple(
    "ElevatorOpeartionRecord", ["start", "other", "end"]
)


class ElevatorOperation:
    """Represents an elevator operation"""

    def __init__(self, record: ElevatorOperationRecord):
        self._record = record

    def __repr__(self):
        return f"<{self.__class__.__name__}: {vars(self)}>"

    def is_anamoly(self) -> bool:
        """is_anamoly returns true if anamoly is detected in the operation

        Returns:
            bool:
        """
        if self._record.start is None or self._record.end is None:
            return True
        if self.operation_time() > 60 * 10:
            return True
        if self.operation_time() < 0:
            return True
        return False

    def operation_time(self) -> int:
        """operation_time returns the length in seconds between the time the
        button was called to the time the door was opened.

        Returns:
            int: length of time in seconds
        """
        if self._record.start is None or self._record.end is None:
            return -1
        return int((self._record.end.date - self._record.start.date).total_seconds())


class ElevatorOperations:
    def __init__(self, operations: typing.List["ElevatorOperation"]):
        self._operations = operations

    def __repr__(self):
        return f"<{self.__class__.__name__}: {vars(self)}>"

    def __iter__(self):
        return iter(self._operations)

    def average(self) -> float:
        """average returns the average time to complete all contained
        operations.

        Returns:
            float: average
        """
        try:
            return statistics.mean(
                x.operation_time() for x in self._operations if not x.is_anamoly()
            )
        except Exception:
            return -1

    def median(self) -> float:
        """median returns the media time to complete all contained operations.

        Returns:
            float: median
        """
        try:
            return statistics.median(
                x.operation_time() for x in self._operations if not x.is_anamoly()
            )
        except Exception:
            return -1

    @staticmethod
    def from_log_entries(entries: "ElevatorLogEntries") -> "ElevatorOperations":
        """from_log_entries is a convenience method for creating an
        Elevator Operations object from ElevatorLogEntries.

        Returns:
            ElevatorLogEntries: entries
        """
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
    """ElevatorLogEntry models a log entry"""

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
    """ElevatorLogEntries is a container for ElevatorLogEntry"""

    def __init__(self, list: typing.List["ElevatorLogEntry"]):
        self._list = sorted(list, key=lambda x: x.date)

    def __repr__(self):
        return f"<{self.__class__.__name__}: {self._list}>"

    def __iter__(self):
        return self._list.__iter__()

    def insert(self, entry: "ElevatorLogEntry"):
        """insert adds the entry to the container ordered

        Args:
            entry (ElevatorLogEntry): elevator log entry
        """
        self._list.insert(
            bisect.bisect_left(self._list, self._list.append(entry)), entry
        )

    def dates(self) -> typing.Set[datetime.date]:
        """dates returns a set of dates for each log entry in the container

        Returns:
            set[datetime.date]: set of datetime.date's
        """
        return {x.date.date() for x in self._list}

    def datetimes(self) -> typing.Set[datetime.datetime]:
        """datetimes returns a set of datetimes for each log entry in the container

        Returns:
            set[datetime.datetime]: set of datetime.datetime's
        """
        return {x.date for x in self._list}

    def floors(self) -> typing.Set[int]:
        """floors returns a set of floors for each log entry in the container

        Returns:
            set[int]: set of ints
        """
        return {x.floor for x in self._list}

    def filter_date(self, _date: datetime.date) -> "ElevatorLogEntries":
        """filter_date returns a new instance of ElevatorLogEntries that
        match the _date parameter.

        Returns:
            ElevatorLogEntries: entries
        """
        return ElevatorLogEntries([x for x in self._list if x.date.date() == _date])

    def filter_floor(self, floor: int) -> "ElevatorLogEntries":
        """filter_floor returns a new instance of ElevatorLogEntries that
        match the floor parameters.

        Returns:
            ElevatorLogEntries: entries
        """
        return ElevatorLogEntries(
            [x for x in self._list if abs(int(x.floor)) == int(floor)]
        )

    def split_by_date(self) -> typing.Dict[datetime.date, "ElevatorLogEntries"]:
        """split_by_date returns a dictionary with keys as unique dates
        and value as ElevatorLogEntries corresponding to the date key.

        Returns:
            ElevatorLogEntries: entries
        """
        results: typing.Dict[datetime.date, ElevatorLogEntries] = {}
        for _date in self.dates():
            results[_date] = self.filter_date(_date)
        return results

    def split_by_floor(self) -> typing.Dict[int, "ElevatorLogEntries"]:
        """split_by_floor returns a dictionary with keys as unique floors
        and value as ElevatorLogEntries corresponding to the floor key.

        Returns:
            ElevatorLogEntries: entries
        """
        results: typing.Dict[int, ElevatorLogEntries] = {}
        for floor in self.floors():
            results[floor] = self.filter_floor(floor)
        return results


if __name__ == "__main__":

    import os

    def get_user_input_file_path() -> str:
        """get_user_input_file_path prompts user for input file path and returns the path

        Raises:
            FileNotFoundError: if file is not found

        Returns:
            str: validated path of file
        """
        input_path = input("Enter source file path:  ")
        if not os.path.exists(input_path) or not os.path.isfile(input_path):
            print(f"File not found: {input_path}")
            exit(1)
        return input_path

    def load_entries_from_csv(input_path: str) -> typing.List[typing.Any]:
        """load_entries_from_csv loads elevator log entries from a csv file.

        Args:
            input_path (str): path as string

        Returns:
            List: entries
        """
        with open(input_path) as csvfile:
            reader = csv.DictReader(csvfile)
            return sorted(reader, key=operator.itemgetter("date"), reverse=True)

    input_path = get_user_input_file_path()

    entries = ElevatorLogEntries(
        [ElevatorLogEntry(**x) for x in load_entries_from_csv(input_path)]
    ).split_by_date()
    for k, v in entries.items():
        print(
            f"{k}: average {round(ElevatorOperations.from_log_entries(v).average(), 2)} seconds   median: {round(ElevatorOperations.from_log_entries(v).median(), 2)} seconds"
        )
