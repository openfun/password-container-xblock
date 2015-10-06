Password-container Xblock
=========================

This xblock controls time availability and password access to other Xblocks it contains. It especially allow to take a proctored exam by communicate a password to student when examination starts. It also close access to its content when available time is up.
When examination elements are left on several pages, one can instanciate several Password-container Xblock belonging to the same group which will unlock all at the same time.



Installation
------------

Install Python package

    python setup.py install

Add `password_container` to edx-platform `INSTALLED_APPS`

Create database tables

    paver update_db -s devstack

Add `password_container` to the list of advanced modules in the advanced settings of a course.

