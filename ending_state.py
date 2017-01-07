
class EndingState(object):
    state_name = "ending"

    def __init__(self, call):
        self.call = call

    def enter(self):
        channel_name = self.call.channel.json.get('name')
        print "Ending voice mail call from {0}".format(channel_name)
        self.call.channel.hangup()
