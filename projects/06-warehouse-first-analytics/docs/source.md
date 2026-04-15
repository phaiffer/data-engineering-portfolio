# Source Documentation

## Dataset

**BigQuery project:** `bigquery-public-data`
**Dataset:** `stackoverflow`
**Access:** Public, no billing required to query (charges apply to your GCP project for bytes scanned)

The Stack Overflow public dataset is maintained by Google and contains a near-complete
history of the Stack Overflow Q&A platform from its founding in 2008 through periodic
refreshes. It is one of the largest and most widely recognized public datasets available
natively in BigQuery, making it a natural fit for a warehouse-first analytics project.

---

## Tables Selected

### `posts_questions`

One row per Stack Overflow question.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key |
| `title` | STRING | Question title |
| `tags` | STRING | Pipe-delimited with angle brackets: `<python><pandas>` |
| `score` | INTEGER | Net vote score (can be negative) |
| `view_count` | INTEGER | Cumulative page views |
| `answer_count` | INTEGER | Number of posted answers |
| `comment_count` | INTEGER | Number of comments |
| `favorite_count` | INTEGER | Number of bookmarks |
| `accepted_answer_id` | INTEGER | ID of accepted answer; NULL if none |
| `owner_user_id` | INTEGER | Author's user ID; NULL for anonymous |
| `creation_date` | TIMESTAMP | UTC creation timestamp |
| `last_activity_date` | TIMESTAMP | UTC timestamp of last activity |

**Estimated size (unfiltered):** ~60–70 GB. The full table spans 2008–present.
A 4-year window (2021–2024) reduces scan to ~15–20 GB.

### `posts_answers`

One row per Stack Overflow answer. Same schema as questions; split by post type.

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key for the answer |
| `parent_id` | INTEGER | References the parent question's `id` |
| `score` | INTEGER | Net vote score |
| `comment_count` | INTEGER | Number of comments |
| `owner_user_id` | INTEGER | Author's user ID |
| `creation_date` | TIMESTAMP | UTC creation timestamp |
| `last_activity_date` | TIMESTAMP | UTC last activity |

**Estimated size (unfiltered):** ~70–80 GB.

### `users`

One row per registered user. Much smaller than posts tables (~21 M rows, ~2 GB).

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key (positive = real user; ≤ 0 = system/anonymous stub) |
| `display_name` | STRING | Public display name |
| `reputation` | INTEGER | Cumulative reputation score |
| `up_votes` | INTEGER | Total upvotes cast |
| `down_votes` | INTEGER | Total downvotes cast |
| `views` | INTEGER | Profile view count |
| `location` | STRING | Free-text location (nullable) |
| `creation_date` | TIMESTAMP | Account creation date |
| `last_access_date` | TIMESTAMP | Last login timestamp |

### `tags`

One row per distinct tag. Very small (~65 k rows).

| Column | Type | Notes |
|---|---|---|
| `id` | INTEGER | Primary key |
| `tag_name` | STRING | Tag slug (e.g., "python", "sql") |
| `count` | INTEGER | Number of questions currently carrying this tag |
| `excerpt_post_id` | INTEGER | Tag excerpt wiki post |
| `wiki_post_id` | INTEGER | Tag full wiki post |

---

## Tables Not Used (v1)

| Table | Reason excluded |
|---|---|
| `comments` | Large (~6 GB), adds comment-level grain not needed for v1 marts |
| `post_history` | Revision history; high volume, out of scope for v1 |
| `badges` | Gamification data; doesn't add analytical value to question/answer marts |
| `votes` | Vote-level detail not needed; aggregate vote counts are on posts |

---

## Source Caveats

1. **Not partitioned.** The tables in `bigquery-public-data.stackoverflow` are not
   partitioned. Cost control relies entirely on `WHERE creation_date >= ...` filters
   in staging models.

2. **Body column excluded.** The `body` column (HTML question/answer text) is available
   in the public dataset but deliberately excluded. It is very large (~100 GB if included
   across both posts tables) and not needed for structured analytical marts.

3. **Refresh frequency.** The public dataset is refreshed periodically by Google but is
   not real-time. Data may lag the live Stack Overflow data by days to weeks.

4. **Anonymous users.** User IDs ≤ 0 represent system or anonymous stubs and are
   excluded in `stg_stackoverflow__users`.

5. **Answer count vs. window-scoped count.** The `answer_count` column on questions
   reflects the live count at refresh time. `answer_count_in_window` in intermediate
   models reflects only answers present in the staging year window — these will differ
   for older questions.

6. **Tag string format.** Tags are stored as `<tag1><tag2>` — angle brackets must be
   stripped and delimiters normalized before splitting. This is handled in
   `stg_stackoverflow__questions`.

---

## Why This Source

- Native BigQuery access — no download, ingestion pipeline, or local storage required
- Large enough to justify warehouse-first modeling patterns
- Well-understood domain with clean relational structure
- Strongly distinct from previous portfolio projects (Kaggle CSV, local Parquet, event streams)
- Questions, answers, users, and tags form a natural staging → intermediate → marts hierarchy
- Demonstrates cost-awareness as a real concern, not just a talking point
