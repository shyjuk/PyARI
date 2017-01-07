
# from event import Event

class RecordingState(object):
    state_name = "recording"

    def __init__(self, call):
        self.call = call
        self.hangup_event = None
        self.dtmf_event = None
        self.recording = None

    def enter(self):
        print "Entering recording state"
        self.hangup_event = self.call.channel.on_event('ChannelHangupRequest',
                self.on_hangup)
        self.dtmf_event = self.call.channel.on_event('ChannelDtmfReceived',
                                                     self.on_dtmf)
        self.recording = self.call.channel.record(name=self.call.vm_path,
                                                  format='wav',
                                                  beep=True,
                                                  ifExists='overwrite')
        print "Recording voicemail at {0}".format(self.call.vm_path)

    def cleanup(self):
        print "Cleaning up event handlers"
        self.dtmf_event.close()
        self.hangup_event.close()

    def on_hangup(self, channel, event):
        print "Accepted recording {0} on hangup".format(self.call.vm_path)
        self.cleanup()
        self.call.state_machine.change_state(Event.HANGUP)

    def on_dtmf(self, channel, event):
        digit = event.get('digit')
        if digit == '#':
            rec_name = self.recording.json.get('name')
            print "Accepted recording {0} on DTMF #".format(rec_name)
            self.cleanup()
            self.recording.stop()
            self.call.state_machine.change_state(Event.DTMF_OCTOTHORPE)
