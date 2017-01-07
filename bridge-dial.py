
import logging
import requests
import ari

logging.basicConfig(level=logging.ERROR)

client = ari.connect('http://localhost:8088', 'asterisk', 'asterisk')


def safe_hangup(channel):
    """Safely hang up the specified channel"""
    try:
        print 'hangup here'
        channel.hangup()
        print "Hung up {}".format(channel.json.get('name'))
    except requests.HTTPError as e:
        if e.response.status_code != requests.codes.not_found:
            raise e


def safe_bridge_destroy(bridge, br):
    """Safely destroy the specified bridge"""
    try:
        print 'bridge destroyed'
        br.stop()
        bridge.destroy()
    except requests.HTTPError as e:
        if e.response.status_code != requests.codes.not_found:
            raise e


def stasis_start_cb(channel_obj, ev):
    """Handler for StasisStart"""

    channel = channel_obj.get('channel')
    channel_name = channel.json.get('name')
    args = ev.get('args')

    if not args:
        print "Error: {} didn't provide any arguments!".format(channel_name)
        return

    if args and args[0] != 'inbound':
        # Only handle inbound channels here
        return

    if len(args) != 2:
        print "Error: {} didn't tell us who to dial".format(channel_name)
        channel.hangup()
        return

    print "{} entered our application".format(channel_name)
    channel.ring()

    try:
        print "Dialing {}".format(args[1])
        outgoing = client.channels.originate(endpoint=args[1],
                                             app='bridge-dial',
                                             appArgs='dialed')
    except requests.HTTPError:
        print "Whoops, pretty sure %s wasn't valid" % args[1]
        channel.hangup()
        return

    channel.on_event('StasisEnd', lambda *args: safe_hangup(outgoing))
    outgoing.on_event('StasisEnd', lambda *args: safe_hangup(channel))

    def outgoing_start_cb(channel_obj, ev):
        """StasisStart handler for our dialed channel"""

        print "{} answered; bridging with {}".format(outgoing.json.get('name'),
                                                     channel.json.get('name'))
        channel.answer()

        bridge = client.bridges.create(type='mixing')
        bridge.addChannel(channel=[channel.id, outgoing.id])
        br = bridge.record(name='a', format='wav', ifExists='overwrite')

        # Clean up the bridge when done
        channel.on_event('StasisEnd', lambda *args:
                         safe_bridge_destroy(bridge, br))
        outgoing.on_event('StasisEnd', lambda *args:
                          safe_bridge_destroy(bridge, br))

    outgoing.on_event('StasisStart', outgoing_start_cb)


client.on_channel_event('StasisStart', stasis_start_cb)

client.run(apps='bridge-dial')
