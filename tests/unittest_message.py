import unittest

# Class Under Test
from lib.Message import Message

class testMessage(unittest.TestCase):
    """
    Test the correct parsing of message
    arriving on the IRC Socket into the
    appropriate slices
    """
    
    def testPrivmsg(self):
        msg = Message(":nick!~user@some.host-name.tld PRIVMSG #channel :this is a demo message")
        
        # identity
        user = msg.getUser()
        self.assertEqual(user[0], "nick")
        self.assertEqual(user[1], "~user")
        self.assertEqual(user[2], "some.host-name.tld")
        
        # type
        self.assertEqual(msg.getType(), "PRIVMSG")
        
        # target
        self.assertEqual(msg.getTarget(), "#channel")
        
        # message
        self.assertEqual(msg.getMessage(), "this is a demo message")
        
        # Corner Cases
        # 1: Message contains whitespaces only
        msg = Message(":nick!~user@some.host-name.tld PRIVMSG targetuser : ")
        self.assertEqual(msg.getMessage(), " ")
        
        # 2: Target can be a nickname
        self.assertEqual(msg.getTarget(), "targetuser")
        
    def testNotice(self):
        msg = Message(":nick!~user@some.host-name.tld NOTICE #channel :this is a demo message")
        
        # identity
        user = msg.getUser()
        self.assertEqual(user[0], "nick")
        self.assertEqual(user[1], "~user")
        self.assertEqual(user[2], "some.host-name.tld")
        
        # type
        self.assertEqual(msg.getType(), "NOTICE")
        
        # target
        self.assertEqual(msg.getTarget(), "#channel")
        
        # message
        self.assertEqual(msg.getMessage(), "this is a demo message")
        
        # Corner Cases
        # 1: Message contains whitespaces only
        msg = Message(":nick!~user@some.host-name.tld PRIVMSG targetuser : ")
        self.assertEqual(msg.getMessage(), " ")
        
        # 2: Target can be a nickname
        self.assertEqual(msg.getTarget(), "targetuser")    
        
    def testRawNumeric(self):
        msg = Message(":localhost.local 422 pyLilaine :MOTD File is missing")
        
        # numeric needs to be of type int
        self.assertIsInstance(msg.getType(), int)
        self.assertEqual(msg.getType(), 422)
        
        # server
        self.assertEqual(msg.getServerName(), "localhost.local")
        
        # target
        self.assertEqual(msg.getTarget(), "pyLilaine")
        
        # message
        self.assertEqual(msg.getMessage(), ":localhost.local 422 pyLilaine :MOTD File is missing") # FIXME
        
        # Corner Cases
        # 1: Secondary Target
        msg = Message(":localhost.local 366 pyLilaine #channel :End of /NAMES list.")
        self.assertEqual(msg.getMessage(), ":localhost.local 366 pyLilaine #channel :End of /NAMES list.") # FIXME
        
        # 2: Message is not separated by a leading colon
        msg = Message(":localhost.local 333 pyLilaine #channel topicAuthor 1360811136")
        self.assertEqual(msg.getMessage(), ":localhost.local 333 pyLilaine #channel topicAuthor 1360811136") # FIXME
        
    def testJoin(self):
        msg = Message(":nick!user@some-host.tld JOIN :#channel")
        
        # type
        self.assertEqual(msg.getType(), "JOIN")
        
        # target
        self.assertEqual(msg.getTarget(), "#channel")
        
        
    def testPart(self):
        msg = Message(":nick!user@some-host.tld PART #channel :some message")
        
        # type
        self.assertEqual(msg.getType(), "PART")
        
        # target
        self.assertEqual(msg.getTarget(), "#channel")
        
        # message
        self.assertEqual(msg.getMessage(), "some message")

    def testQuit(self):
        msg = Message(":Lilaine!lilaine@A7C823CA.E483845.77FD6974.IP QUIT :Quit: Messages can contain additional colons")
        
        # user
        user = msg.getUser()
        self.assertEqual(user[0], "Lilaine")
        self.assertEqual(user[1], "lilaine")
        self.assertEqual(user[2], "A7C823CA.E483845.77FD6974.IP")
        
        # type
        self.assertEqual(msg.getType(), "QUIT")
        
        # message
        self.assertEqual(msg.getMessage(), "Quit: Messages can contain additional colons")
        
    def testChannelMode(self):
        msg = Message(":hexa-!hexa@local-7DE74C9E.dip.t-dialin.net MODE #channel +n")
         
        # user
        user = msg.getUser()
        self.assertEqual(user[0], "hexa-")
        self.assertEqual(user[1], "hexa")
        self.assertEqual(user[2], "local-7DE74C9E.dip.t-dialin.net")
        
        # type
        self.assertEqual(msg.getType(), "MODE")
        
        # target
        self.assertEqual(msg.getTarget(), "#channel")
        
        # mode
        self.assertEqual(msg.getMode(), "+n")
        
    def testUserMode(self):
        msg = Message(":Lilaine MODE Lilaine :+iwxz")
        
        # type
        self.assertEqual(msg.getType(), "USERMODE")
        
        # nick / target
        self.assertEqual(msg.getNick(), "Lilaine")
        self.assertEqual(msg.getNick(), msg.getTarget())
        
        # mode
        self.assertEqual(msg.getMode(), "+iwxz")
        
                    
    def testKick(self):
        msg = Message(":hexa-!hexa@local-7DE74C9E.dip.t-dialin.net KICK #channel Lilaine :some kick message")
        
        # type
        self.assertEqual(msg.getType(), "KICK")
        
        # target, victim
        self.assertEqual(msg.getTarget(), "#channel")
        self.assertEqual(msg.getVictim(), "Lilaine")
        
        # reason
        self.assertEqual(msg.getMessage(), "some kick message")
   
        
def suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(testMessage))
    return suite
