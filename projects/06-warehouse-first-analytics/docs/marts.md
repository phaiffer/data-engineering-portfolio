# Marts Reference

All marts are materialized as BigQuery tables in the `stackoverflow_analytics` dataset
(or the dataset configured in `profiles.yml`).

---

## mart_monthly_question_activity

**Grain:** One row per calendar month within the staging window.
**Primary use:** Track question volume, engagement, and resolution trends over time.

| Column | Type | Description |
|---|---|---|
| `month_start` | DATE | First day of the calendar month |
| `year` | INTEGER | Calendar year |
| `month` | INTEGER | Calendar month (1–12) |
| `total_questions` | INTEGER | Questions created in this month |
| `unanswered_questions` | INTEGER | Questions with zero answers |
| `questions_with_accepted_answer` | INTEGER | Questions with an accepted answer |
| `unanswered_rate_pct` | FLOAT | % of questions unanswered |
| `accepted_answer_rate_pct` | FLOAT | % of questions with accepted answer |
| `avg_question_score` | FLOAT | Average net vote score |
| `avg_view_count` | FLOAT | Average view count |
| `avg_answer_count` | FLOAT | Average number of answers |
| `avg_hours_to_first_answer` | FLOAT | Average hours to receive a first answer |
| `median_hours_to_first_answer` | FLOAT | Median hours to first answer |
| `avg_hours_to_accepted_answer` | FLOAT | Average hours to receive an accepted answer |

**Example questions answered:**
- How has question volume on Stack Overflow changed since 2021?
- Has the unanswered rate increased or decreased over time?
- Is the community responding faster or slower year-over-year?

---

## mart_tag_activity

**Grain:** One row per tag (minimum 10 questions in the window).
**Primary use:** Identify the most active technology ecosystems and compare their community health metrics.

| Column | Type | Description |
|---|---|---|
| `tag_name` | STRING | Tag slug (e.g., "python", "typescript") |
| `questions_in_window` | INTEGER | Questions with this tag in the staging window |
| `questions_with_accepted_answer` | INTEGER | Questions resolved with an accepted answer |
| `unanswered_questions` | INTEGER | Questions with no answers |
| `avg_question_score` | FLOAT | Average question score for this tag |
| `avg_view_count` | FLOAT | Average view count for this tag |
| `avg_answer_count` | FLOAT | Average number of answers per question |
| `accepted_answer_rate_pct` | FLOAT | % of questions with accepted answer |
| `unanswered_rate_pct` | FLOAT | % of questions unanswered |
| `total_historical_question_count` | INTEGER | All-time question count from source tags table |

**Example questions answered:**
- Which tags have the highest and lowest accepted-answer rates?
- How does Python compare to JavaScript in terms of question volume and resolution?
- Which emerging technologies show high unanswered rates?

---

## mart_answer_latency

**Grain:** One row per calendar month (questions with at least one answer only).
**Primary use:** Analyse response-time distributions and track how quickly the community responds.

| Column | Type | Description |
|---|---|---|
| `month_start` | DATE | First day of the calendar month |
| `year` | INTEGER | Calendar year |
| `month` | INTEGER | Calendar month |
| `questions_with_answers` | INTEGER | Answered questions in this month |
| `questions_with_accepted_answer` | INTEGER | Questions with an accepted answer |
| `avg_hours_to_first_answer` | FLOAT | Average hours to first answer |
| `p25_hours_to_first_answer` | FLOAT | 25th percentile hours to first answer |
| `median_hours_to_first_answer` | FLOAT | Median hours to first answer |
| `p75_hours_to_first_answer` | FLOAT | 75th percentile hours to first answer |
| `p90_hours_to_first_answer` | FLOAT | 90th percentile hours to first answer |
| `avg_hours_to_accepted_answer` | FLOAT | Average hours to accepted answer |
| `median_hours_to_accepted_answer` | FLOAT | Median hours to accepted answer |

**Example questions answered:**
- Has typical response time improved since AI coding tools emerged in 2022?
- What fraction of questions receive a first answer within 1 hour?
- How does median latency compare to p90 latency? (long-tail vs. typical)

---

## mart_question_outcomes

**Grain:** One row per question in the staging window.
**Primary use:** Ad-hoc question-level exploration, segmentation, and future downstream use.

| Column | Type | Description |
|---|---|---|
| `question_id` | INTEGER | Unique question post ID |
| `question_title` | STRING | Question title |
| `tags_clean` | STRING | Pipe-delimited tag string |
| `question_score` | INTEGER | Net vote score |
| `view_count` | INTEGER | Cumulative view count |
| `answer_count` | INTEGER | Number of answers at source refresh time |
| `comment_count` | INTEGER | Number of comments |
| `favorite_count` | INTEGER | Number of bookmarks |
| `has_accepted_answer` | BOOLEAN | Whether an accepted answer exists |
| `is_unanswered` | BOOLEAN | Whether answer_count is zero |
| `hours_to_first_answer` | FLOAT | Hours to first answer (null if none) |
| `hours_to_accepted_answer` | FLOAT | Hours to accepted answer (null if none) |
| `outcome_category` | STRING | resolved / answered_no_accept / unanswered / unknown |
| `score_tier` | STRING | viral / popular / good / decent / neutral / downvoted |
| `question_author_user_id` | INTEGER | Author's user ID |
| `question_created_at` | TIMESTAMP | UTC creation time |
| `question_created_date` | DATE | Creation date |
| `created_year` | INTEGER | Creation year |
| `created_month` | INTEGER | Creation month |
| `created_month_start` | DATE | First day of creation month |

---

## mart_user_reputation_segments

**Grain:** One row per reputation tier (5 rows total).
**Primary use:** Understand how user experience level relates to question quality and resolution.

| Column | Type | Description |
|---|---|---|
| `reputation_tier` | STRING | new / contributor / established / advanced / expert |
| `tier_rank` | INTEGER | Display order (1=new, 5=expert) |
| `user_count` | INTEGER | Users in tier who asked questions in the window |
| `total_questions` | INTEGER | Total questions from users in this tier |
| `questions_with_accepted_answer` | INTEGER | Questions resolved with an accepted answer |
| `unanswered_questions` | INTEGER | Unanswered questions from this tier |
| `avg_questions_per_user` | FLOAT | Average questions per user in this tier |
| `avg_question_score` | FLOAT | Average question score |
| `avg_question_views` | FLOAT | Average view count |
| `avg_accepted_answer_rate_pct` | FLOAT | Average accepted-answer rate |
| `min_reputation_in_tier` | INTEGER | Minimum reputation score in tier |
| `max_reputation_in_tier` | INTEGER | Maximum reputation score in tier |
| `avg_reputation_in_tier` | FLOAT | Average reputation score in tier |

**Reputation tier thresholds:**

| Tier | Reputation range |
|---|---|
| new | < 100 |
| contributor | 100 – 999 |
| established | 1,000 – 9,999 |
| advanced | 10,000 – 99,999 |
| expert | ≥ 100,000 |
