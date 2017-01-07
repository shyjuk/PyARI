
import ari
import logging
import sys
import os
import time
import uuid

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger(__name__)

client = ari.connect('http://localhost:8088', 'asterisk', 'asterisk')

class VoiceMailCall(object):
    def __init__(self, ari_client, channel):
        self.client = ari_client
        self.channel = channel
        self.vm_path = os.path.join('voicemail', str(time.time()))

        print 'Channel: ', self.channel

        self.setup_state_machine()

    def setup_state_machine(self):
        print 'Inside state machine'
        self.dtmf_event = self.channel.on_event('ChannelDtmfReceived',
                                             self.on_dtmf)
        self.recording = self.channel.record(name=self.vm_path,
                                          format='wav',
                                          beep=True,
                                          ifExists='overwrite')

    def after_record(self):
        print 'this is after recording has stopped'
        self.channel.hangup()

    def on_dtmf(self, channel, event):
        digit = event.get('digit')
        if digit == '#':
            rec_name = self.recording.json.get('name')
            print "Accepted recording {0} on DTMF #" .format(rec_name)
            self.recording.stop
            print "recording stopped"

            self.after_record()

def stasis_start_cb(channel_obj, event):
    channel = channel_obj['channel']
    channel_name = channel.json.get('name')
    print "Recording started for channel {0}" .format(channel_name)
    channel.answer()
    VoiceMailCall(client, channel)

client.on_channel_event('StasisStart', stasis_start_cb)
client.run(apps='vm-record')
