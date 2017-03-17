#!/usr/bin/python

import json
import sys
import websocket
import threading
import Queue
import requests
from gevent.ares import channel

class ARIInterface(object):
    def __init__(self, server_addr, username, password):
        self._req_base = "http://%s:8088/ari/" % server_addr
        self._username = username
        self._password = password

    def answer_call(self, channel_id):
        req_str = self._req_base+"channels/%s/answer" % channel_id
        self._send_post_request(req_str)

    def play_sound(self, channel_id, sound_name):
        req_str = self._req_base+("channels/%s/play?media=sound:%s" % (channel_id, sound_name))
        self._send_post_request(req_str)


    def continue_in_dialplan(self, channel_id):
        #print "in continue_in_dialplan()"
        #print  self._req_base+("channels/%s/continue" % (channel_id))
        req_str = self._req_base+("channels/%s/continue" % (channel_id))
        self._send_post_request(req_str)

    def music_on_hold(self, channel_id, moh_class):
        print "in music_on_hold()"
        print self._req_base+("channels/%s/moh?mohClass=custom" % (channel_id))

        req_str = self._req_base+("channels/%s/moh?mohClass=%s" % (channel_id, moh_class))
        self._send_post_request(req_str)

    def music_unhold(self, channel_id):
        print "unhold the music"
        #stopMoh
        print self._req_base+("channels/%s/moh" % (channel_id))
        req_str = self._req_base+("channels/%s/moh" % (channel_id))
        self._send_delete_request(req_str)


    def _send_post_request(self, req_str):
        r = requests.post(req_str, auth=(self._username, self._password))
        #print(r.text())

    def _send_delete_request(self, req_str):
        r = requests.delete(req_str, auth=(self._username, self._password))
        print r.status_code
        #print(r.text())

class ARIApp(object):
    def __init__(self, server_addr):
        app_name = 'hello-world'
        username = 'asterisk'
        password = 'asterisk'
        url = "ws://%s:8088/ari/events?app=%s&api_key=%s:%s" % (server_addr, app_name, username, password)
        self.ari = ARIInterface(server_addr, username, password)
        self.ws = websocket.create_connection(url)
        self.channel_id = ''

        try:
            for event_str in iter(lambda: self.ws.recv(), None):
                event_json = json.loads(event_str)

                json.dump(event_json, sys.stdout, indent=2, sort_keys=True,
                          separators=(',', ': '))
                print("\n\nWebsocket event***************************************************\n")

                if event_json['type'] == 'StasisStart':
                    channel_id = event_json['channel']['id']
                    self.on_stasis_start(channel_id)
                    #self.ari.answer_call(event_json['channel']['id'])
                    #self.ari.play_sound(event_json['channel']['id'], 'tt-monkeys')

                elif event_json['type'] =='StasisEnd':
                    channel_id = event_json['channel']['id']
                    self.on_stasis_end(channel_id)
                #ChannelDtmfReceived

                elif event_json['type'] =='ChannelDtmfReceived' :
                    channel_id = event_json['channel']['id']
                    digit = event_json['digit']
                    self.on_channel_dtmf_received(channel_id, digit)


        except websocket.WebSocketConnectionClosedException:
            print("Websocket connection closed")
        except KeyboardInterrupt:
            print("Keyboard interrupt")
        finally:
            if self.ws:
                self.ws.close()



    def on_stasis_start(self, channel_id):
        print "ARI Session started\n";
        self.ari.answer_call(channel_id)
        #self.ari.play_sound(channel_id,'tt-monkeys')


    def on_stasis_end(self, channel_id):
        print "Stasis Session ended\n"

    def on_channel_dtmf_received(self, channel_id, digit):
        print "DTMF Received: " + digit
        # on any dtmf stop the stasis Application and goto next prirorty.
        #self.ari.continue_in_dialplan(channel_id)
        if('1' == digit):
            self.ari.music_on_hold(channel_id,'custom')

        elif('2' == digit):
            self.ari.music_unhold(channel_id)

        if('3' == digit):
            self.ari.music_on_hold(channel_id,'default')

        elif('4' == digit):
            self.ari.music_unhold(channel_id)

    def on_ChannelHangupRequest(self, channel_id):
        print "ChannelHangupRequest received"

    def on_PlaybackFinished(self, channel_id):
        print "PlaybackFinished received"

if __name__ == "__main__":
    app = ARIApp('192.168.1.106')
