<!-- comment
   SPDX-FileCopyrightText: 2020-2023 Sebastian Wagner, Filip Pokorný
   SPDX-License-Identifier: AGPL-3.0-or-later
-->


# Using Elasticsearch as a database for IntelMQ

If you wish to run IntelMQ with Elasticsearch or full ELK stack (Elasticsearch, Logstash, Kibana) it is entirely
possible. This guide assumes the reader is familiar with basic configuration of ELK and does not aim to cover using ELK
in general. It is based on the version 6.8.0 (ELK is a fast moving train therefore things might change). Assuming you
have IntelMQ (and Redis)
installation in place, lets dive in.

## Configuration without Logstash

This case involves two steps:

1. Configure IntelMQ to output data directly into Elasticsearch.

2. Configure Elasticsearch for ingesting the inserted data.

!!! bug
    This section of the documentation is currently incomplete and will be updated later.

## Configuration with Logstash

This case involves three steps:

1. Configuring IntelMQ to output data to Redis.

2. Configure Logstash to collect data from Redis and insert them into Elasticsearch.

3. Configure Elasticsearch for ingesting the inserted data.

Each step is described in detail in the following sections.

### Configuring IntelMQ

In order to pass IntelMQ events to Logstash we will utilize already installed Redis. Add a new Redis Output Bot to your
pipeline. As the minimum fill in the following parameters: `bot-id`, `redis_server_ip` (can be hostname)
, `redis_server_port`, `redis_password` (if required, else set to empty!), `redis_queue` (name for the queue). It is
recommended to use a different `redis_db` parameter than used by the IntelMQ (specified as `source_pipeline_db`
, `destination_pipeline_db` and `statistics_database`).

Example values:

```yaml
bot-id: redis-output
redis_server_ip: 10.10.10.10
redis_server_port: 6379
redis_db: 4
redis_queue: logstash-queue
```

!!! warning
    You will not be able to monitor this redis queue via IntelMQ Manager.

### Configuring Logstash

Logstash defines pipelines as well. In the pipeline configuration of Logstash you need to specify where it should look
for IntelMQ events, what to do with them and where to pass them.

#### Input

This part describes how to receive data from Redis queue. See the example configuration and comments below:

```
input {
  redis {
    host => "10.10.10.10"
    port => 6379
    db => 4
    data_type => "list"
    key => "logstash-queue"
  }
}
```

- `host` - same as redis_server_ip from the Redis Output Bot
- `port` - the redis_server_port from the Redis Output Bot
- `db` - the redis_db parameter from the Redis Output Bot
- `data_type` - set to `list`
- `key` - same as redis_queue from the Redis Output Bot

!!! tip
    You can use environment variables for the Logstash configuration, for example `host => "${REDIS_HOST:10.10.10.10}"`. The value will be taken from the environment variable `$REDIS_HOST`. If the environment variable is not set then the default value of `10.10.10.10` will be used instead.

#### Filter (optional)

Before passing the data to the database you can apply certain changes. This is done with filters. See an example:

```
filter {
  mutate {
    lowercase => ["source.geolocation.city", "classification.identifier"]
    remove_field => ["__type", "@version"]
  }
  date {
    match => ["time.observation", "ISO8601"]
  }
}
```

!!! tip
    It is recommended to use the `date` filter: generally we have two timestamp fields - `time.source` (provided by the feed source this can be understood as when the event happened; however it is not always present) and `time.observation` (when IntelMQ collected this event). Logstash also adds another field `@timestamp` with time of processing by Logstash. While it can be useful for debugging, I recommend to set the `@timestamp` to the same value as `time.observation`.

!!! warning
    It is not recommended to apply any modifications to the data (within the `mutate` key) outside of the IntelMQ. All necessary modifications should be done only by appropriate IntelMQ bots. This example only demonstrates the possibility.

#### Output

The pipeline also needs output, where we define our database
(Elasticsearch). The simplest way of doing so is defining an output like this:

```
output {
  elasticsearch {
    hosts => ["http://10.10.10.11:9200", "http://10.10.10.12:9200"]
    index => "intelmq-%{+YYYY.MM}"
  }
}
```

- `hosts` - Elasticsearch host (or more) with the correct port (9200 by default)
- `index` - name of the index where to insert data

!!! tip
    Authors experience, hardware equipment and the amount of events collected led to having a separate index for each month. This might not necessarily suit your needs, but it is a suggested option.

!!! warning
    By default the ELK stack uses insecure HTTP. It is possible to setup Security for secure connections and basic user management. This is possible with the Basic (free) licence since versions 6.8.0 and 7.1.0.

### Configuring Elasticsearch

Configuring Elasticsearch is entirely up to you and should be consulted with
the [official documentation](https://www.elastic.co/guide/en/elasticsearch/reference/index.html). What you will most
likely need is something
called [index template](https://www.elastic.co/guide/en/elasticsearch/reference/current/indices-templates.html)
mappings. IntelMQ provides a tool for generating such mappings. See
[ElasticMapper Tool](https://github.com/certtools/intelmq/tree/develop/contrib/elasticsearch/README.md).

!!! danger
    Default installation of Elasticsearch database allows anyone with cURL and connection capability to have administrative access to the database. Make sure you secure your toys!
