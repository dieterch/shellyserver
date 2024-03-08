from quart import Quart, render_template, redirect, url_for
from pprint import pprint as pp
import json
import wakeonlan as wol
import os
import requests

mac = "10:bf:48:8d:5c:34"
app = Quart(__name__)

def getRQ(url):
    try:
        r = requests.get(url, timeout=100.000)
        r.raise_for_status()
        return r.json()
    except requests.exceptions.HTTPError as err:
        print(repr(err))

def getShelly(ip):
    res = getRQ('http://'+ip+'/shelly')
    return res

def power(gen, ip):
    if gen == 1:
        res = getRQ(f'http://{ip}/status')
        return res.get('meters')[0].get('power',0.0)
    elif ((gen == 2) or (gen == 3)):
        id = 0; pw_sum = 0.0
        for i in range(0,2):
            try:
                res = getRQ(f'http://{ip}/rpc/Switch.GetStatus?id={i}')
                pw_sum += res.get('apower',0.0)
            except Exception as e:
                print(f"Error: {e}")
        return pw_sum
    else:
        return 0.0

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

def addData(rec):
    if rec['hostname'] in zdata:
        rec['name'] = zdata[rec['hostname']]['name']
        rec['power'] = power(zdata[rec['hostname']]['gen'],rec['ip'])
    return rec    

@app.route('/')
async def index():
    print()
    data = []
    try:
        text_file = open("/var/lib/misc/dnsmasq.leases", "r")
        lines = text_file.readlines()
        for line in lines:
            rec = dict(zip(keys, line.strip().split()))
            data.append(addData(rec))
        text_file.close()
        power_sum = 0
        for r in data:
            if 'power' in r:
                power_sum += r['power']    
        pp (data)
    except FileNotFoundError:
        print("File not found")
    return await render_template("index.html", data=data, powersum=f"{power_sum:5.1f}")  # Required to be in templates/

if __name__ == '__main__':
    print('''
\033[H\033[J
****************************************************
* ShellyServer V0.01 (c)2024 Dieter Chvatal        *
****************************************************
''')
    if os.getenv('IN_DOCKER') == 'true':
        app.run(host='0.0.0.0', port=5550, debug=True)
    else:
        app.run(host='0.0.0.0', port=5500, debug=True)
