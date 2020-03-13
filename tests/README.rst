This directory contains the Pytest tests which depend on a Salesforce org
or other remote services.

Due to file naming conventions, they do not execute (by default) when you run
pytest locally.

Pytest integration tests are hidden from ordinary `pytest` because they are in
a different directory.

You can invoke these test with the CCI task:

cci task run integration_tests
