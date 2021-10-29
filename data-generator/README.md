# Twitch Data Generator

To ingest Twitch data into Kafka, we’ll use use existing Python wrappers for the Twitch Helix API ([`python-twitch-client`](https://github.com/tsifrer/python-twitch-client)) and Kafka ([`kafka-python`](https://github.com/dpkp/kafka-python)) to write a minimal producer.

## Twitch Authentication Flow

To work with data from Twitch, you first need to [register an app](https://dev.twitch.tv/docs/authentication#registration) and get a hold of your app access tokens. Remember to replace `<client_id>` and `<client_secret>` in the [producer](twitch_kafka_producer.py)!

### Kafka Producer (Python)

In this demo, we use the `streams` endpoint to produce events about active streams into [Redpanda](https://vectorized.io/redpanda) (which is Kafka-compatible). As with all real-world data, there's a few catches to be aware of before getting to the actual processing:

1. The endpoint returns events sorted by number of current viewers, so there might be duplicate or missing events as viewers join and leave. As new events flow in for the same `id`, we're only ever interested in keeping the most recent values; so we'll need [`UPSERT`](https://materialize.com/docs/sql/create-source/json-kafka/#upsert-envelope-details) to retract old values and keep things fresh.

2. Events have a `started_at` timestamp, but there's no way of knowing when a stream is finished. Because _the maximum broadcast length is 48 hours_; we can lean on that to expire events in state using a [temporal filter](https://materialize.com/docs/guides/temporal-filters/#main).

3. Each stream may have up to five tags, so we'll end up with a JSON array literal in `tag_ids` for each record.

Once you've get the setup up and running, you can check that the `twitch-streams` topic has been created:

```bash
docker-compose exec redpanda rpk topic list
```

And that there's data landing in Redpanda:

```bash
docker-compose exec redpanda rpk topic consume twitch-streams
```