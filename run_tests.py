#!/usr/bin/python
import unittest

import tests.unittest_message, tests.unittest_pluginsystem

# compile suite
suite = unittest.TestSuite()
suite.addTest(tests.unittest_message.suite())
suite.addTest(tests.unittest_pluginsystem.suite())

# run
unittest.TextTestRunner(verbosity=2).run(suite)
