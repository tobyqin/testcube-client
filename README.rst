===============
testcube-client
===============


.. image:: https://img.shields.io/pypi/v/testcube-client.svg
        :target: https://pypi.python.org/pypi/testcube-client

.. image:: https://img.shields.io/travis/tobyqin/testcube-client.svg
        :target: https://travis-ci.org/tobyqin/testcube-client

.. image:: https://pyup.io/repos/github/tobyqin/testcube-client/shield.svg
     :target: https://pyup.io/repos/github/tobyqin/testcube-client/
     :alt: Updates


A Python client for testcube.


* Free software: MIT license
* TestCube Project: https://github.com/tobyqin/testcube
* TestCube Client Project: https://github.com/tobyqin/testcube-client


Get Started
-----------

You should have python 2.7 or 3.x installed on your machine. Then follow steps here.

Installation
~~~~~~~~~~~~
Install testcube-client via pip is the most easy way.

::

  pip install testcube-client -U

Register to Server
~~~~~~~~~~~~~~~~~~

You should have a TestCube_ server deployed, then run ``--register`` command.::

  testcube-client register http://testcube-server:8000

Submit Run Results
~~~~~~~~~~~~~~~~~~

Once you had register to the server, you have 2 ways to upload test results,
one is call ``--start-run`` at the beginning and call ``--finish--run`` when it finished.::

  # call --start-run before run started
  testcube-client --start-run -name "nightly run for testcube"  --team Core --product TestCube

  # call --finish-run once run completed
   testcube-client --finish-run --xunit-files **/results/*.xml

In this way, TestCube will record the **exact** ``start_time`` and ``end_time`` for the run.

Another choice is ``--run`` command to upload test results at one time.::

  # put this command at the end of a run
  testcube-client --run -n "smoke tests for testcube" -t XPower -p TestCube -v v1.0 -x **/smoke*.xml

With this choice, TestCube will use current time as ``end_time`` of the run, and guess ``start_time``
according to run duration.

Command-line Options
~~~~~~~~~~~~~~~~~~~~

The optional arguments::

  -h, --help            show this help message and exit
  -r REGISTER, --register REGISTER
                        Register to the TestCube server, e.g.
                        http://server:8000
  -run, --run           Upload run info at one time, require team,product,name
                        and xunit files.
  -start, --start-run   Start a run, require team, product and a name.
  -finish, --finish-run
                        Finish a run, require xunit files.

  -x XUNIT_FILES, --xunit-files XUNIT_FILES
                        Specify the xunit xml results, e.g "**/result*.xml"
  -n NAME, --name NAME  Specify the run name.
  -t TEAM, --team TEAM  Specify the team name.
  -p PRODUCT, --product PRODUCT
                        Specify the product name.
  -v PRODUCT_VERSION, --product-version PRODUCT_VERSION
                        Specify the product version. [Optional]
  -f, --force           Force the command, when force register, will clear all caches.


.. _TestCube: https://github.com/tobyqin/testcube
