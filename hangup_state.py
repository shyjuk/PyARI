
class HungUpState(object):
    state_name = "hungup"

    def __init__(self, call):
        self.call = call

    def enter(self):
        channel_name = self.call.channel.json.get('name')
        print "Channel {0} hung up".format(channel_name)
