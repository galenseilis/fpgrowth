# README
---
## Installation and Compilation Instructions

Provided that you have Python 3.7+ installed on your system, you should not require taking any steps to install software for running `fpgrowth.py` because they are all implemented with [standard library](https://docs.python.org/3/library/) modules. Since Python is an [interpreted language](https://en.wikipedia.org/wiki/Interpreted_language), and for your convenience I have intentionally **not** made use of any [Cython](https://cython.org/) or other extensions, you should be able to run the scripts immediately without any setup. If you do not have a sufficient version of Python installed, you can find downloads for it for any of the major operating systems on the main [website](https://www.python.org/downloads/).

## Execution

The script intended to be used from a command with `python3` available in your shell's namespace. All three of these scripts have a `-h` or `--help` option where you can see the available options. Also note that `-m`, representing the minimum (relative) support threshold, has a default value of 0.5, and that the default output file specified by `-o` is `"MiningResults.txt"`.

### apriori.py
```
usage: fpgrowth.py [-h] -i IN_FILE [-o OUT_FILE] [-m MIN_SUPP]

A CLI that performs the FP-Growth pattern learning algorithm. This program
expects an input text file with a particular format. The first line of the
input file should be the number of transactions in the transaction database.
All subsequent lines are expected to have a tab-delimited format where the
first column is the transaction ID, the second column is the number of items
in the transaction, and the third column is a space-delimited set of items.
Failure to format the input file correctly may result in errors or unexpected
behaviour.

optional arguments:
  -h, --help            show this help message and exit
  -o OUT_FILE, --out_file OUT_FILE
                        Output results file. (default='MiningResults.txt')
  -m MIN_SUPP, --min_supp MIN_SUPP
                        Minimum support threshold as a float between 0 and 1.
                        (default=0.5)

required arguments:
  -i IN_FILE, --in_file IN_FILE
                        Input data file.
```

> **_Example:_**  `python3 fpgrowth.py -i data.txt`

> **_Example:_**  `python3 fpgrowth.py -i data.txt -m 0.5 -o frequent_patterns_data.txt`

## Profiling

You may wish to further understand my code by profiling it to assess which pieces of the code are the performance bottlenecks. This can be accomplished with the [cProfile](https://docs.python.org/3.9/library/profile.html) from the command line, and no further installation is required since this library is built-in. The following shows the basic usage.

```
$ python3 -m cProfile -h
Usage: cProfile.py [-o output_file_path] [-s sort] [-m module | scriptfile] [arg] ...

Options:
  -h, --help            show this help message and exit
  -o OUTFILE, --outfile=OUTFILE
                        Save stats to <outfile>
  -s SORT, --sort=SORT  Sort order when printing to stdout, based on
                        pstats.Stats class
  -m                    Profile a library module
```

> **_Example:_** `python3 -m cProfile -o data.prof fpgrowth.py -i data.txt`

Furthermore, you can easily visualize the output data with an extended library known as [snakeviz](https://jiffyclub.github.io/snakeviz/), which can be installed with `pip install snakeviz`. This library can act as a command line tool, and I've included the usage below.

```
$ snakeviz -h
usage: snakeviz [-h] [-v] [-H ADDR] [-p PORT] [-b BROWSER_PATH] [-s] filename

Start SnakeViz to view a Python profile.

positional arguments:
  filename              Python profile to view

optional arguments:
  -h, --help            show this help message and exit
  -v, --version         show program's version number and exit
  -H ADDR, --hostname ADDR
                        hostname to bind to (default: 127.0.0.1)
  -p PORT, --port PORT  port to bind to; if this port is already in use a free
                        port will be selected automatically (default: 8080)
  -b BROWSER_PATH, --browser BROWSER_PATH
                        name of webbrowser to launch as described in the
                        documentation of Python's webbrowser module:
                        https://docs.python.org/3/library/webbrowser.html
  -s, --server          start SnakeViz in server-only mode--no attempt will be
                        made to open a browser
```

Once you have a `*.prof` file, you can easily visualize the results within a browser.

> **_Example:_** `snakeviz data.prof`

---
© 2020 Galen Seilis

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
