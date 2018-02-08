=======
History
=======

0.7.8 (2018-02-08)
------------------
* Support clean up runs after specified days
* testcube-client --cleanup-runs days 60

0.7.6 (2017-10-31)
------------------
* Support server version v1.3
* Save environment variables to server when start a run, use for result reset

0.7.0 (2017-10-25)
------------------
* Support server version v1.2
* Able to handle pending task, for example:
* testcube-client --handle-task
* Able to rerun a result by reset id, for example:
* testcube-client --reset-result 12345 -x "**/*.xml"

0.6.0 (2017-09-07)
------------------
* Able to upload result files using argument --result-files
* testcube-client --result-files "**/*.png"

0.5.0 (2017-07-07)
------------------
* Update due to testcube model changed, not compatible with prev versions

0.3.3 (2017-06-29)
------------------
* Improve run url in output.
* Bug fix - run duration data incorrect.
* Abort run if failed to analyze its xml.
* Always summarize run duration from test cases.
* Bug fix - unicode exception message in python 2.
* Bug fix - multiple cache hits error.

0.2.2 (2017-06-13)
------------------
* Support --force command when register a server.
* Sum the testsuite time from testcases if there is no time attribute in result xml.
* Fix document moved header issue when server deployed in IIS server.
* Add cache to improve performance.
* Fix import error.

0.1.3 (2017-06-12)
------------------

* Support register to TestCub server.
* Support --run command.
* Support --start-run command.
* Support --finish-run command.

0.1.0 (2017-06-08)
------------------

* First release on PyPI.
