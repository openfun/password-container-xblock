Password-container Xblock
=========================

This Xblock controls time availability and password access to other Xblocks it
contains. It especially allows to take a proctored exam by communicating a
password to a student when the examination starts. It also closes access to its
content when available time is up. When examination elements are left on several
pages, one can instanciate several Password-container Xblocks belonging to the
same group which will unlock all at the same time.

[![CircleCI](https://circleci.com/gh/openfun/password-container-xblock/tree/master.svg?style=svg)](https://circleci.com/gh/openfun/password-container-xblock/tree/master)

## Installation

Install this package with `pip` using FUN package index _via_:

```bash
$ pip install --extra-index-url https://pypi.fury.io/fun-mooc password_container-xblock
```

Alternatively, if you intend to work on this project, clone this repository
first, and then make an editable installation _via_:

```bash
$ pip install -e ".[dev]"
```

## Configuration

Add `password_container` to edx-platform `INSTALLED_APPS`, and create database
tables _via_:

```bash
$ paver update_db -s devstack
```

Add finally, `password_container` to the list of advanced modules in the
"advanced settings" of a course.
