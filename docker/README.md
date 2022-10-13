# Grading setup for xfuzz

This directory contains tools for grading xfuzz.

## Setup

To run the tools provided here, you will need to start by installing
[Docker](https://en.wikipedia.org/wiki/Docker_%28software%29).  You can do so
either by following the instructions provided
[here](https://docs.docker.com/engine/install/), or by running

```
$ curl -s https://get.docker.com/ -o- | sudo bash
```

Note that the proxy server must run with `CAP_NET_ADMIN`, so you will have to
either install Docker rootfully (the default), or run Docker as root.

To reduce the number of times you will have to run `sudo`, you may want to run

```
$ sudo usermod -aG docker $(whoami)
```

to add yourself to the `docker` group. Log yourself out of the VM and then log
back in, and you will be able to run Docker commands as a non-root user.

After setting up Docker, you should build the container images used for testing
with

```
$ docker compose build
```

### AppArmor sandboxing

If you are on an AppArmor-supported Linux distribution such as Debian or Ubuntu,
there there are AppArmor profiles available for you to help keep the students'
code sandboxed. You can enable them with

```
$ sudo apparmor_parser -r ./xfuzz.profile
```

The use of the custom AppArmor profile is disabled by default. If you wish to
enable it, you can run

```
$ export XFUZZ_USE_APPARMOR=1
```

To disable it again, you can run `export XFUZZ_USE_APPARMOR=0`.

## Running unit tests

To execute the tests, run

```
$ ./run-tests.sh /path/to/student/code
```

where `/path/to/student/code` is the directory containing the student's source
code for xfuzz (i.e. the directory containing `fuzz.py` and any other Python
files the student may have written).

This script will first run the unit tests with `pytest`. After those tests have
completed, it will run the speed tests against the server you set up with Docker
Compose.

The AppArmor profiles have been tested ahead of time but are still experimental.
If they are causing issues (e.g. if you are getting lots of unexpected
"permission denied" errors) and do not wish to use them, you should run `export
XFUZZ_USE_APPARMOR=0` to disable them.

## Cleaning up

After you have finished running all of your tests, you can run

```
$ docker compose down
```

To take down the testing servers. If you'd like to clear up some space on your
computer, you can then run

```
$ docker system prune
$ docker volume prune
$ docker rmi xfuzz/xfuzz:latest xfuzz/proxy:latest
```

This will remove any stopped containers and unused data volumes, as well as the
container images you built during setup.
