Definitely we should add edit counter and indicate what details in content have changed. If a user sees the counter has changed many times, they can see that content is still alive and author care about it. Users can also investigate exactly what details were changed, and they don't have to remember what the original content looked like. Presenting these details also saves time for users and build trust for platform.



## Performance & Database Optimizations

To ensure the application scales effectively for 10,000+ active users and prevents common database bottlenecks, several architectural and query-level optimizations were implemented:

### 1. N+1 Query Prevention (`select_related` & `prefetch_related`)
* **`select_related("user", "content")`**: Used in `FollowViewSet` to fetch foreign key relationships using SQL `JOIN`s in a single query.
* **`prefetch_related("followers", "edit_history")`**: Used in `ContentViewSet` to batch-fetch many-to-many and reverse foreign key relationships in separate optimized queries.
* **Impact**: Eliminates the N+1 problem, reducing what would be hundreds of database queries per request down to just 1–2 queries.

### 2. Database-Level Computations (`annotate` & `F()` expressions)
* Instead of fetching raw models into Python memory and iterating over them to check for updates, we offload this work directly to the database engine using `annotate()` combined with `Case`, `When`, and `F()`.
* **Impact**: Computes flags like `has_new_changes` in microseconds on the database server, bypassing Python memory overhead and serialization penalties.

### 3. Concurrency Control & Atomic Increments
* Used `instance.edited_count = F("edited_count") + 1` for update operations.
* **Impact**: Executes atomic SQL increments directly in the database (`UPDATE content SET edited_count = edited_count + 1`). This completely prevents race conditions and lost updates caused by rapid consecutive clicks or parallel requests.

### 4. Granular Database Writes (`update_fields`)
* Implemented `instance.save(update_fields=[...])` during `retrieve` and update operations (e.g., updating only `last_viewed_at` or `edited_count`).
* **Impact**: Prevents overwriting the entire row in the database. Reduces SQL payload size, decreases write-lock times, and improves overall DB write throughput.

### 5. Database Indexing (`db_index=True`)
* Added database indexes to heavily queried timestamp columns (`updated_at` on `Content` and `last_viewed_at` on `Follow`).
* **Impact**: Transforms costly Full Table Scans into logarithmic Index Scans during timestamp comparisons (`content__updated_at__gt=F("last_viewed_at")`), keeping response times fast as table sizes grow into millions of rows.

### 6. API Pagination
* Integrated DRF pagination (`PageNumberPagination` / `paginate_queryset`) on content endpoints.
* **Impact**: Limits payload sizes, prevents memory exhaustion on the application server, and guarantees consistent latency even under heavy data load.