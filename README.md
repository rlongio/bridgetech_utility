# A sample Python project

"""
Attached a CSV of an elevator operation.
There are two types of data - button_call and door_open.
We want to analyze the time it took to get to a floor from the time it was called.

A few rules:

1. The button_call can be positive or negative. That just means the person wanted to go up or down. We can treat it for now as the absolute value. So -3=3
2. The button_call can be pushed a few times before the open_door at that floor. We only care about the first time it was pressed until the open_door.
3. We can assume that if a call was 'open' (=meaning the button_call was sent, but the open_door at that floor didn't occur yet) for more than 10 minutes - then this is an anomaly and we do not want to count that button_call.

The output should be per-day the Average and Median wait times for the elevator
"""

"""

- get list of values
- sort by date

iterate:

if type is button_call:
results[floor]
"""

![Python Logo](https://www.python.org/static/community_logos/python-logo.png "Sample inline image")

A sample project that exists as an aid to the [Python Packaging User
Guide][packaging guide]'s [Tutorial on Packaging and Distributing
Projects][distribution tutorial].

This project does not aim to cover best practices for Python project
development as a whole. For example, it does not provide guidance or tool
recommendations for version control, documentation, or testing.

[The source for this project is available here][src].

Most of the configuration for a Python project is done in the `setup.py` file,
an example of which is included in this project. You should edit this file
accordingly to adapt this sample project to your needs.

---

This is the README file for the project.

The file should use UTF-8 encoding and can be written using
[reStructuredText][rst] or [markdown][md use] with the appropriate [key set][md use]. It will be used to generate the project webpage on PyPI and will be
displayed as the project homepage on common code-hosting services, and should be
written for that purpose.

Typical contents for this file would include an overview of the project, basic
usage examples, etc. Generally, including the project changelog in here is not a
good idea, although a simple “What's New” section for the most recent version
may be appropriate.

[packaging guide]: https://packaging.python.org
[distribution tutorial]: https://packaging.python.org/tutorials/packaging-projects/
[src]: https://github.com/pypa/sampleproject
[rst]: http://docutils.sourceforge.net/rst.html
[md]: https://tools.ietf.org/html/rfc7764#section-3.5 "CommonMark variant"
[md use]: https://packaging.python.org/specifications/core-metadata/#description-content-type-optional
