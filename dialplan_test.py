
from models import Modules, Moduledata

def audio(dp, id):
    print 'Audio playback here!'
    if dp['options']['filename']:
        dp['data'] ={'playedfile' : dp['options']['filename']}
    else:
        dp['data'] ={'playedfile' : 'no file'}
    return dp

def hangup(dp, id):
    print 'Hangup here!'
    dp['data'] = 'Call Hang up'
    return dp

for mods in Modules.select():
    output = {}
    output['outputDataArray'] = []
    module_id = mods.id
    dialplan = mods.dialplan['nodeDataArray']
    for dp in dialplan:
        if dp['type'] == 'Audio':
            audiodp = audio(dp, mods.id)
            output['outputDataArray'].append(audiodp)
        elif dp['type'] == 'Hangup':
            hangupdp = hangup(dp, mods.id)
            output['outputDataArray'].append(hangupdp)
        else:
            print 'Good Day!!!!'
print output
Moduledata.create(module = module_id, data = output)
