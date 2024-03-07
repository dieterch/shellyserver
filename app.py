from quart import Quart, render_template, redirect, url_for
from pprint import pprint as pp
import json
import wakeonlan as wol

mac = "10:bf:48:8d:5c:34"
app = Quart(__name__)

keys = ['timestamp', 'mac', 'ip', 'hostname', 'id']
zdata = {
    'shellyplug-s-040D25' : {
        'name' : 'Blumenlicht',
        'gen':1 
    },
    'shellyplug-s-6A6374' : {
        'name' : 'BeoCreate',
        'gen':1 
    },
    'shelly1pmminig3-ecda3bc405dc' : {
        'name' : 'Wohnzimmer Deckenlicht',
        'gen':3 
    },
    'shelly1-5B2B93' : {
        'name' : 'Gang Deckenlicht',
        'gen':1 
    },
    'shellyplus1-08b61fd93e1c' : {
        'name' : 'Küche Schalter oben',
        'gen':2 
    },
    'shellyplus1-08b61fd7f0ac' : {
        'name' : 'Schlafzimmer Dieter Türschalter',
        'gen':2 
    },
    'shellyplus2pm-5443b23e53b8' : {
        'name' : 'Küche & Esstisch',
        'gen':2 
    },
  
}



@app.route('/wakeonlan')
async def wakeonlan():
    wol.send_magic_packet(mac)
    return redirect(url_for('index'))
    #return { "status": "ok" }

@app.route('/wolserver')
async def wolserver():
    wol.send_magic_packet(mac)
    return { "status": "ok" }

@app.route('/')
async def index():
    data = []
    try:
        text_file = open("/var/lib/misc/dnsmasq.leases", "r")
        lines = text_file.readlines()
        for line in lines:
            rec = dict(zip(keys, line.strip().split()))
            if rec['hostname'] in zdata:
                rec['name'] = zdata[rec['hostname']]['name']
            data.append(rec)
            print(line.strip())
        # print(len(lines))
        text_file.close()
        pp (data)
    except FileNotFoundError:
        print("File not found")
    return await render_template("index.html", data=data)  # Required to be in templates/

app.run(host='0.0.0.0', port=5550, debug=True)
