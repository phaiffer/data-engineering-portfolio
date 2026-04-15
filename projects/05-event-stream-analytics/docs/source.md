# Source

## Selected Source

This project uses the official Wikimedia EventStreams `recentchange` stream:

- stream endpoint: `https://stream.wikimedia.org/v2/stream/recentchange`
- EventStreams documentation: `https://wikitech.wikimedia.org/wiki/EventStreams`
- RecentChange schema: `https://schema.wikimedia.org/repositories/primary/jsonschema/mediawiki/recentchange/latest.yaml`

## Why This Source Fits

This source is a good portfolio fit because it is:

- public and widely recognized;
- event-oriented by design instead of a static file dump;
- naturally suited to producer and consumer boundaries;
- rich enough for raw landing, standardization, and summary metrics;
- meaningfully different from the batch-oriented case studies already in the repository.

## Important Stream Behavior

The source is delivered over HTTP using Server-Sent Events.

Important operational notes from the official documentation:

- the public service exposes continuous streams of structured events;
- `recentchange` emits MediaWiki recent change events;
- canary events are included and should be discarded for normal analytics use;
- the public HTTP layer enforces a connection timeout, so reconnect behavior matters;
- historical consumption is possible only while retained history still exists.

## Bounded Local Execution

This project does not pretend to run forever.

Instead, local commands support bounded execution such as:

- capture `N` events with `--max-events`;
- run for `X` seconds with `--max-seconds`;
- broker replay: seek earliest retained broker offsets with `--replay` on the Bronze consumer;
- offline replay: rebuild Silver and Gold from landed Bronze files with `run_replay.py`.

This keeps the project reproducible, inspectable, and realistic for local portfolio use.

## Important Event Fields

The RecentChange schema includes many fields. This project focuses on the fields that are useful for a first streaming analytics pass:

- `meta.dt`: source event timestamp in UTC;
- `meta.id`: source metadata event id;
- `type`: event type such as `edit`, `new`, or `log`;
- `bot`: whether the event is marked as bot-generated;
- `wiki`: wiki identifier such as `enwiki`;
- `namespace`: namespace id;
- `title`: affected page title;
- `user`: actor name;
- `comment`: change comment when present;
- `server_name` and `server_url`: wiki context;
- `revision` and `length`: revision and content-size context when present.

## Caveats

- the public stream can disconnect and reconnect;
- not every field is populated on every event;
- client-side filtering is expected;
- the public stream includes synthetic canary messages that are not analytical signal;
- broker replay is retention-bound, which is why Bronze raw landing is the more durable rebuild point in this project.
