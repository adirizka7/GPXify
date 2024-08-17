from urllib.parse import parse_qs

import base64
import json
import requests

def handler(event, context):
    event_body = event['body']
    req_body = parse_qs(event_body)
    url = req_body['url'][0]

    # TODO: Propagate the error properly. Either to clients (might be too verbose?)
    # or to cloudwatch.
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/gpx+xml',
            'Access-Control-Allow-Origin': '*'
        },
        'body': to_gpx(url)
    }

def to_gpx(url):
    maps = routes_info(html(url))
    
    metadata = maps[0]
    title = gpx_title(metadata)

    gpx = f"""<gpx>
    <trk>
        <name>{title}</name>
        <type>Walking</type>
        <trkseg>
    """

    routes = maps[1]
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
    
    return gpx

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

def gpx_title(metadata):
    try:
        origin = metadata[0][0][1][1]
    except TypeError:
        origin = ""

    try:
        destination = metadata[1][0][1][1]
    except TypeError:
        destination = ""

    if origin == "" and destination == "":
        return "From GPXify to You"

    if origin == "":
        return "to " + destination

    if destination == "":
        return "from " + origin

    if origin != "" and destination != "":
        return f"{origin} to {destination}"

if __name__ == '__main__':
    link = input('GMaps Link: ')
    print(to_gpx(link))
