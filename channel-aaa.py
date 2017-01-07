
import ari
import logging
import threading
import time

logging.basicConfig(level=logging.ERROR)

client = ari.connect('http://localhost:8088', 'asterisk', 'asterisk')

class DTMFInput(object):
    def __init__(self, channel, ev):
        self.inps = ''
        self.ev = ev
        self.channel = channel
        self.channel.on_event('ChannelDtmfReceived', self.on_dtmf_received)

    def on_dtmf_received(self, channel, ev):
        digit = int(ev.get('digit'))

        self.inps += str(digit)

        hashTermination = True

        if len(self.inps) == 2 and hashTermination:
            print self.inps
        elif len(self.inps) == 2 and not hashTermination:
            channel.hangup()
        else:
            print self.inps

def stasis_start_cb(channel_obj, ev):
    """Handler for StasisStart event"""

    channel = channel_obj.get('channel')
    print "Channel %s has entered the application" % channel.json.get('name')

    channel.answer()

    t = threading.Thread(target = DTMFInput(channel, ev))

    t.wait(timeout=5)

    # t.stop()

    print 'after dtmf'


def stasis_end_cb(channel, ev):
    """Handler for StasisEnd event"""

    print "%s has left the application" % channel.json.get('name')

client.on_channel_event('StasisStart', stasis_start_cb)
client.on_channel_event('StasisEnd', stasis_end_cb)

client.run(apps='channel-aa')
