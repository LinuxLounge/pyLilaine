import Queue

class Event(object):
    def __init__(self, name, timer):
        self.timer = timer
        self.name = name
        self.passed = False

    def getName():
        return self.name

    def __update(self, diff):
        if (self.timer >= diff):
            self.timer -= diff
        else:
            self.passed = True

    def __passed(self):
        return self.passed

class EventHandler(object):
    def __init__(self):
        self.__events = []
        self.__finished = Queue.Queue()
        
    def update(self, diff):
        for event in self.__events:
            event.__update(diff)
            if event.__passed():
                self.__finished.put(event)
                self.__events.remove(event)

    def next(self):
        try:
            return self.__finished.get()
        except self.__finished.Empty():
            pass
            
    def register(self, name, delay):
        self.__events.append(Event(name, delay))
