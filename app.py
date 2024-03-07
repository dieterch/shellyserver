from quart import Quart, render_template, redirect, url_for
from pprint import pprint as pp
import json
import wakeonlan as wol

mac = "10:bf:48:8d:5c:34"
app = Quart(__name__)

keys = ['timestamp', 'mac', 'ip', 'hostname', 'id']

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
            data.append(rec)
            print(line.strip())
        # print(len(lines))
        text_file.close()
        pp (data)
    except FileNotFoundError:
        print("File not found")
    return await render_template("index.html", data=data)  # Required to be in templates/

app.run(host='0.0.0.0', port=5550, debug=True)
