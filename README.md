# xfuzz

- [Introduction](#introduction)
- [Repository layout](#repository-layout)
- [Testing](#testing)

_**NOTE:**_ this is a programming assignment originally designed for CS 3710
*Intro to Cybersecurity* at the University of Virginia. This assignment covers
*web fuzzers*, and asks you to build your own fuzzer from the skeleton
provided here.

See [ASSIGNMENT.md](ASSIGNMENT.md) for the assignment instructions.

See [INSTALL.md](INSTALL.md) for installation instructions.

## Introduction

*Web fuzzers* are useful tools for exploring and auditing the security of web
applications. They can do any number of things, including

- Finding the pages and directories that are available on a webserver;
- brute-force a login page to try and login as a user;
- enumerate the [virtual hosts](https://en.wikipedia.org/wiki/Virtual_hosting)
  that are available on a webserver;
- and more!

There are many great web fuzzers already out there, like
[ffuf](https://github.com/ffuf/ffuf) and
[wfuzz](https://wfuzz.readthedocs.io/en/latest/). For this assignment, we will
be using the  [aiohttp](https://docs.aiohttp.org/en/stable/index.html) library
to build the fastest web fuzzer we can in the spirit of these other projects.

## Repository layout

The `xfuzz/` directory contains some skeleton code you can use to start building
out your fuzzer. This skeleton code contains the following files:

- `xfuzz/cmd.py`: code for parsing command-line arguments to `xfuzz`.
- `xfuzz/fuzz.py`: contains the `fuzz` function, which takes the command-line
  arguments given to `xfuzz` after they've been parsed and pre-processed by the
  code in `cmd.py`.

(There are also a few other files in this directory that you can ignore for the
sake of this assignment.)

Once you've [installed xfuzz](#installation) and its dependencies, you should
run `python3 -m xfuzz --help` to see how it should be used; you can use this to
start guiding your development.

I *recommend* that you start implementing xfuzz from the `fuzz()` function in
`xfuzz/fuzz.py`; this is the function that gets called after we read in
arguments from the command line. It is also the function that will get used by
the PyTest test harness to ensure the correctness of your solution.

## Testing

There are two ways that you can test xfuzz: interactively, and with `pytest`. In
either case, you will want to install the dependencies in
`dev.requirements.txt`, which you can do with

```
$ pip install -r dev.requirements.txt
```

The `pytest` method is automated and a bit easier to use, but for ensuring that
your tool works correctly you should test it against the interactive server as
described below.

### Interactive testing

You can run a test server for `xfuzz` locally with the following command:

```
$ uvicorn test.interactive:server --host 0.0.0.0 --port 5000
```

This will run an HTTP server on http://localhost:5000. You can then run (in a
different terminal)

```
$ python3 -m xfuzz -u http://localhost:5000
```

along with any other options you want to run xfuzz against this local server.
For instance, once you've implemented the `fuzz()` function, you should be able
to run

```
$ python3 -m xfuzz -u http://localhost:5000/FUZZ -w test/wordlists/common.txt
```

to see all of the pages in the top-level directory of the webserver.

#### Documentation

To see all of the routes that are available on the testing server, you can go to
http://localhost:5000/docs after starting up the server (note that these routes
change a little every time you start the server). This webpage will show you all
of the routes that are available on the server, as well as a little information
about the `xfuzz` commands that you should try to run against them.

#### Wordlists

To obtain a wordlist you can use for testing, you can either download a wordlist
from the [SecLists repository](https://github.com/danielmiessler/SecLists/) (you
will probably want to use a wordlist in the `Web-Content/` directory), or you
can use the `common.txt` wordlist in `test/wordlists/common.txt`.

#### Other interactive tests

In addition to running the local server, you can try running xfuzz against
[http://ffuf.me](http://ffuf.me/).

### PyTest

For grading purposes, we will use PyTest and some manual testing to ensure that
`xfuzz` works correctly. You can run a series of automated tests for `xfuzz` by
simply running

```
$ pytest
```

from your terminal. These tests are non-comprehensive, and in particular they
don't check the terminal output of your tool; please make sure that you've
sufficiently implemented all of the features required for this assignment before
submitting it.
