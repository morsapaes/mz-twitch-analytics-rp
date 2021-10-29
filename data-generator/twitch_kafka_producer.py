#!/usr/bin/env python
import datetime
import sys
import os
import twitch
from itertools import islice
import json
from kafka import KafkaProducer

client = twitch.TwitchHelix(client_id='<client_id>',
                            client_secret='<client_secret>',
                            scopes=[twitch.constants.OAUTH_SCOPE_ANALYTICS_READ_EXTENSIONS])
client.get_oauth()

# Producer instance
p = KafkaProducer(bootstrap_servers='redpanda:9092')


def json_serializer(obj):
    if isinstance(obj, (datetime.datetime, datetime.date)):
        return obj.isoformat()
    raise "Type %s not serializable" % type(obj)


try:
    streams = client.get_streams(page_size=100)

    while streams.next:

        for stream in islice(streams, 0, 100):
            payload = json.dumps(stream, default=json_serializer, ensure_ascii=False).encode('utf-8')

            p.send(topic='twitch-streams', key=stream['id'].encode('utf-8'), value=json.dumps(stream, default=json_serializer, ensure_ascii=False).encode('utf-8'))

    p.flush()

except Exception as e:
    print("Exception: %s" % str(e),file=sys.stderr)
    sys.exit(1)
