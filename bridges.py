
import requests
import websocket
import json
import uuid

server_addr = 'localhost'
app_name = 'hello-world'
username = 'asterisk'
password = 'asterisk'

url = "ws://%s:8088/ari/events?app=%s&api_key=%s:%s" % (server_addr, app_name, username, password)
req_base = "http://%s:8088/ari/" % server_addr

ws = websocket.create_connection(url)


def enter(channel_id):
    print '\nChannel Id: ', channel_id

    print '\n-----Creating a bridge------\n'
    req_str = req_base + "bridges?type={0}" .format('mixing')
    a = requests.post(req_str, auth=(username, password))
    print a.text

    bridge_json = json.loads(a.text)
    bridge_id = bridge_json['id']

    print '\n----Adding caller channel to bridge----\n'
    req_str = req_base + "bridges/{0}/addChannel?channel={1}" .format(bridge_id, channel_id)
    a = requests.post(req_str, auth=(username, password))

    req_str = req_base + "channels?endpoint={0}&app={1}&appArgs={2}" .format('SIP/3003', 'hello-world', 'dialed')
    a = requests.post(req_str, auth=(username, password))
    print a.text
    bridge_channel_json = json.loads(a.text)
    next_channel_id = bridge_channel_json['id']

    print '\n---Adding endpoint user to bridge----'
    req_str = req_base + "bridges/{0}/addChannel?channel={1}" .format(bridge_id, next_channel_id)
    a = requests.post(req_str, auth=(username, password))
    print a.status_code

    print '\n-----Listing available bridges------\n'
    req_str = req_base + "bridges"
    a = requests.get(req_str, auth=(username, password))
    print a.text


    print '\n----Deleting bridge---\n'
    req_str = req_base + "bridges/{0}" .format(bridge_id)
    a = requests.delete(req_str, auth=(username, password))
    print a.status_code

try:
    for event_str in iter(lambda: ws.recv(), None):
        event_json = json.loads(event_str)
        event_type = event_json['type']

        print event_type

        if event_json['type'] == 'StasisStart':
            print 'Stasis Start'
            channel_id = event_json['channel']['id']
            enter(channel_id)
        elif event_json['type'] == 'StasisEnd':
            print 'Stasis End'
except websocket.WebSocketConnectionClosedException:
    print 'Websocket Connection Closed'
except KeyboardInterrupt:
    print 'Keyboard Interrupt'
finally:
    if ws:
        ws.close()
