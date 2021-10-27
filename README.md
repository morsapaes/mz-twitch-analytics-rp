# What's streaming on Twitch?

This is a clone of [this repo](https://github.com/morsapaes/mz-twitch-analytics), using Redpanda as a drop-in replacement for Kafka. Here, we only list the commands and statements that differ between the two setups; excluding these, you can rely on the instructions in the original repo.

<p align="center">
<img width="650" alt="demo_overview" src="https://user-images.githubusercontent.com/23521087/139074379-61f3e46f-aee7-4afe-9cad-56fbf4a1c208.png">
</p>

## Redpanda

To check that the topic has been created:

```bash
docker-compose exec redpanda rpk topic list #or curl -s "localhost:8082/topics" | jq .
```

and that there's data landing:

```bash
docker-compose exec redpanda rpk topic consume twitch-streams
```

## Materialize

Redpanda is supported as a source in Materialize through the Kafka source, so we just need to point it to the `redpanda` broker instead:

```sql
CREATE SOURCE kafka_twitch
FROM KAFKA BROKER 'redpanda:9092' TOPIC 'twitch-streams'
  KEY FORMAT BYTES
  VALUE FORMAT BYTES
ENVELOPE UPSERT;
```