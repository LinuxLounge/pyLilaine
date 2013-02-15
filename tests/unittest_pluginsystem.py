import unittest, time

# Class Under Test
from lib.PluginSystem import PluginSystem
from lib.Plugin import Plugin
from lib.Message import Message

from plugins.test import TestPlugin

class testPluginSystem(unittest.TestCase):
    """
    Test the Interface it provides, whether
    events are correctly called etc.
    """
    
    def setUp(self):
        self.plugins = PluginSystem()
        self.testPlugin = TestPlugin(self.plugins.qout)
        self.testPlugin.setUnitTestInstance(self)
        self.plugins.loadPluginTesting(self.testPlugin)
   
    def testSetup(self):
        self.assertIsInstance(self.plugins, PluginSystem)
        self.assertIsInstance(self.testPlugin, Plugin)
        
    def testHooksPrivmsg(self):
        self.msg = Message(":GnoXter!gnoxter@local-954F9AB.clients.your-server.de PRIVMSG #chan :Momentan blocken sie das Pluginsystem  bzw. update()")
        self.plugins.process(self.msg)
        self.assertEqual(self.msg, self.testPlugin.getLastMessage())
      
    def testHooksNotice(self):
        self.msg = Message(":GnoXter!gnoxter@local-954F9AB.clients.your-server.de NOTICE #chan :Momentan blocken sie das Pluginsystem  bzw. update()")
        self.plugins.process(self.msg)
        self.assertEqual(self.msg, self.testPlugin.getLastMessage())
        
    def testHooksRaw(self):
        self.msg = Message(":localhost.local 366 Lilaine #wifi :End of /NAMES list.")
        self.plugins.process(self.msg)
        self.assertEqual(self.msg, self.testPlugin.getLastMessage())
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testPluginSystem))
    return suite
