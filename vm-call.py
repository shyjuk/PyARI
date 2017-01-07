
# At the top of the file

import ari
import logging
import time
import os
import sys

from recording_state import RecordingState
from ending_state import EndingState
from hangup_state import HungUpState

logging.basicConfig(level=logging.ERROR)
LOGGER = logging.getLogger(__name__)

client = ari.connect('http://localhost:8088', 'asterisk', 'asterisk')


class VoiceMailCall(object):
    def __init__(self, ari_client, channel):
        self.client = ari_client
        self.channel = channel
        self.vm_path = os.path.join('voicemail', str(time.time()))
        self.setup_state_machine()

    def setup_state_machine(self):
        hungup_state = HungUpState(self)
        recording_state = RecordingState(self)
        ending_state = EndingState(self)

        self.state_machine = StateMachine()
        self.state_machine.add_transition(recording_state, Event.DTMF_OCTOTHORPE,
                                          ending_state)
        self.state_machine.add_transition(recording_state, Event.HANGUP,
                                          hungup_state)
        self.state_machine.start(recording_state

        # self.channel.record(
        #     name=self.vm_path,
        #     format='wav',
        #     beep=True,
        #     ifExists='overwrite'
        )
        # This is where we will initialize states, create a state machine, add
        # state transitions to the state machine, and start the state machine.


def stasis_start_cb(channel_obj, event):
    channel = channel_obj['channel']
    channel_name = channel.json.get('name')
    # mailbox = event.get('args')[0]

    print("Channel {0} recording voicemail for".format(
        channel_name))

    channel.answer()
    VoiceMailCall(client, channel)


client.on_channel_event('StasisStart', stasis_start_cb)
client.run(apps='vm-record')
