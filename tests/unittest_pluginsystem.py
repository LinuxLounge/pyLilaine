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
        msg = Message(":GnoXter!gnoxter@local-954F9AB.clients.your-server.de PRIVMSG #chan :Momentan blocken sie das Pluginsystem  bzw. update()")
        self.plugins.process(msg)
        self.assertEqual(msg, self.testPlugin.getLastMessage())
      
    def testHooksNotice(self):
        msg = Message(":GnoXter!gnoxter@local-954F9AB.clients.your-server.de NOTICE #chan :Momentan blocken sie das Pluginsystem  bzw. update()")
        self.plugins.process(msg)
        self.assertEqual(msg, self.testPlugin.getLastMessage())
        
    def testHooksRaw(self):
        msg = Message(":localhost.local 366 Lilaine #wifi :End of /NAMES list.")
        self.plugins.process(msg)
        self.assertEqual(msg, self.testPlugin.getLastMessage())
        
    def testHooksCTCP(self):
        msg = Message(":hexa-!hexa@local-FE1E1050.dip.t-dialin.net PRIVMSG Lilaine :VERSION")
        self.plugins.process(msg)
        self.assertEqual(msg, self.testPlugin.getLastMessage())
        
    def testHooksJoin(self):
        msg = Message(":Lilaine!lilaine@A7C823CA.E483845.77FD6974.IP JOIN :#channel")
        self.plugins.process(msg)
        response = self.testPlugin.getLastMessage()
        expect = [msg.getUser(), msg.getTarget()]
        for i in range(0, len(expect)):
            self.assertEqual(response[i], expect[i])
            
    def testHooksPart(self):
        msg = Message(":hexa-!hexa@local-FE1E1050.dip.t-dialin.net PART #channel :test")
        self.plugins.process(msg)
        response = self.testPlugin.getLastMessage()
        expect = [msg.getUser(), msg.getTarget(), msg.getMessage()]
        for i in range(0, len(expect)):
            self.assertEqual(response[i], expect[i])
            
    def testHooksQuit(self):
        msg = Message(":hexa-!hexa@local-FE1E1050.dip.t-dialin.net QUIT :test")
        self.plugins.process(msg)
        response = self.testPlugin.getLastMessage()
        expect = [msg.getUser(), msg.getMessage()]
        for i in range(0, len(expect)):
            self.assertEqual(response[i], expect[i])        
            
    def testHooksTopic(self):
        msg = Message(":hexa-!martin@lounge-FE1E1050.dip.t-dialin.net TOPIC #channel :sample message")
        self.plugins.process(msg)
        response = self.testPlugin.getLastMessage()
        expect = [msg.getUser(), msg.getTarget(), msg.getMessage()]
        for i in range(0, len(expect)):
            self.assertEqual(response[i], expect[i])        
            
    def testHooksNick(self):
        msg = Message(":hexa-!hexa@local-FE1E1050.dip.t-dialin.net NICK :hexaa")
        self.plugins.process(msg)
        response = self.testPlugin.getLastMessage()
        expect = [msg.getUser(), msg.getMessage()]
        for i in range(0, len(expect)):
            self.assertEqual(response[i], expect[i])
            
    def testHooksMode(self):
        msg = Message(":hexa-!hexa@local-FE1E1050.dip.t-dialin.net MODE #channel +b test!*@*")
        self.plugins.process(msg)
        response = self.testPlugin.getLastMessage()
        expect = [msg.getUser(), msg.getTarget(), msg.getMode()]
        for i in range(0, len(expect)):
            self.assertEqual(response[i], expect[i])  
            
    def testHooksUserMode(self):
        msg = Message(":Lilaine MODE Lilaine :+iwxz")
        self.plugins.process(msg)
        response = self.testPlugin.getLastMessage()
        expect = [msg.getNick(), msg.getTarget(), msg.getMode()]
        for i in range(0, len(expect)):
            self.assertEqual(response[i], expect[i])  
            
    def testHooksKick(self):
        msg = Message(":hexa-!hexa@local-FE1E1050.dip.t-dialin.net KICK #chan carliii :kickmessage")
        self.plugins.process(msg)
        response = self.testPlugin.getLastMessage()
        expect = [msg.getUser(), msg.getTarget(), msg.getVictim(), msg.getMessage()]
        for i in range(0, len(expect)):
            self.assertEqual(response[i], expect[i])  
            
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testPluginSystem))
    return suite
