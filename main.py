import base64
import json
import requests

def handler(event, context):
    reqBody = json.loads(event['body'])
    url = reqBody['url']

    return {
        "statusCode": 200,
        "headers": {
            "Content-Type": "application/gpx+xml"
        },
        "body": to_gpx(url)
    }

def to_gpx(url):
    maps = routes_info(html(url))
    
    metadata = maps[0]
    origin = metadata[0][0][1][1]
    destination = metadata[1][0][1][1]
    
    routes = maps[1]
    gpx = f"""<gpx>
    <trk>
        <name>{origin} to {destination}</name>
        <type>Walking</type>
        <trkseg>
    """
    for route in routes:
        title = route[0][1]
        distance = route[0][2][1]
        duration = route[0][3][1]
    
        tracks = route[1][0][1][0][1]
        for track in tracks:
            latitude = track[0][7][2][2]
            longitude = track[0][7][2][3]
    
            gpx += f'\t\t<trkpt lat="{latitude}" lon="{longitude}"></trkpt>\n'

        latitude = route[1][0][4][2][1][0][2]
        longitude = route[1][0][4][2][1][0][3]
        gpx += f'\t\t<trkpt lat="{latitude}" lon="{longitude}"></trkpt>\n'

        # TODO: Can be developed further so that users can choose their
        # preferred route.
        break 
              
    
    gpx += f"""\t</trkseg>
    </trk>
</gpx>"""
    
    gpx_bytes = gpx.encode()
    gpx_base64_bytes = base64.b64encode(gpx_bytes)
    gpx_base64 = gpx_base64_bytes.decode()

    return gpx_base64

def html(url):
    r = requests.get(url)
    return r.text

def routes_info(maps):
    maps = maps.split('window.APP_INITIALIZATION_STATE=')
    maps = maps[1].split(';window.APP_FLAGS')
    maps = json.loads(maps[0])
    maps = maps[3][4].split('\n')
    maps = json.loads(maps[1])
    maps = maps[0]

    return maps
