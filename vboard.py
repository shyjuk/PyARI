
import ari
import logging
import uuid
from models import Modules, Moduledata

logging.basicConfig(level=logging.ERROR)

client = ari.connect('http://localhost:8088', 'asterisk', 'asterisk')

class VBoard(object):
    def __init__(self, channel_obj, ev):
        self.channel_obj, self.ev = channel_obj, ev

    def audio(self, dp, id):
        print 'Audio Start'
        self.channel = self.channel_obj.get('channel')
        print "Monkeys! Attack %s!" % self.channel.json.get('name')

        self.playback_id = str(uuid.uuid4())
        print 'Playback Start'
        self.playback = self.channel.playWithId(playbackId=self.playback_id,
                                      media='sound:hello-world')

    def playback_finished(self, playback, ev):
        print 'In playback finished'
        print 'Hanging up....'
        self.channel.hangup()

    def hangup(self, dp, id):
        print 'After audio, in hangup'
        # check if playback has been completed
        print 'Check playback is over'
        self.playback.on_event('PlaybackFinished', self.playback_finished)

def stasis_end_cb(channel, ev):
    """Handler for StasisEnd event"""
    print "Channel %s just left our application" % channel.json.get('name')

def stasis_start_cb(channel_obj, ev):
    """Handler for StasisStart event"""

    vb = VBoard(channel_obj, ev)

    for mods in Modules.select():
        output = {}
        output['outputDataArray'] = []
        module_id = mods.id
        dialplan = mods.dialplan['nodeDataArray']
        for dp in dialplan:
            if dp['type'] == 'Audio':
                audiodp = vb.audio(dp, mods.id)
                output['outputDataArray'].append(audiodp)
            elif dp['type'] == 'Hangup':
                hangupdp = vb.hangup(dp, mods.id)
                output['outputDataArray'].append(hangupdp)
            else:
                print 'Good Day!!!!'

if __name__ == '__main__':
    client.on_channel_event('StasisStart', stasis_start_cb)
    client.on_channel_event('StasisEnd', stasis_end_cb)

    client.run(apps='vboard')
