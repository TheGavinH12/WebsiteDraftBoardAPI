# Draft Board API

A small FastAPI backend for your own NFL draft big board — the portfolio site's
Draft Big Board tab calls this instead of (or in addition to) the hard-coded
list. Same idea as the Scores/Standings tabs calling ESPN, just with data you
control.

## Endpoints

- `GET /api/draft-board` — the full list, ordered by rank.
- `GET /api/draft-board/meta` — `{ label, updated, count }` for the page header.
- `POST /api/draft-board` — add a prospect. Requires `X-Admin-Token` header.
- `PUT /api/draft-board/{id}` — edit a prospect. Requires `X-Admin-Token`.
- `DELETE /api/draft-board/{id}` — remove a prospect. Requires `X-Admin-Token`.

A prospect looks like:
```json
{ "id": 1, "rank": 1, "name": "Jeremiah Smith", "position": "WR", "school": "Ohio State", "note": "..." }
```

## Running it locally

```bash
cd draft-board-api
python -m venv .venv && source .venv/bin/activate   # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cp .env.example .env   # edit ADMIN_TOKEN at least
python seed.py          # creates draft_board.db and loads a starting board
uvicorn app.main:app --reload
```

Visit `http://localhost:8000/api/draft-board` — you should see the seeded list.
Interactive API docs are at `http://localhost:8000/docs`.

To edit a prospect from the command line:
```bash
curl -X PUT http://localhost:8000/api/draft-board/1 \
  -H "X-Admin-Token: your-token-from-.env" \
  -H "Content-Type: application/json" \
  -d '{"rank":1,"name":"Jeremiah Smith","position":"WR","school":"Ohio State","note":"Updated note here."}'
```

## Moving to a real database

By default this uses a local SQLite file so it runs with zero setup. For your
actual draft-prospect project (the one with PFF grades), point `DATABASE_URL`
at a real Postgres instance instead — nothing else in the code changes:

```
DATABASE_URL=postgresql://user:password@host:5432/dbname
```

Two free Postgres hosts that work well for a small API like this:
- **[Neon](https://neon.tech)** — serverless Postgres, generous free tier, scales to zero when idle.
- **[Supabase](https://supabase.com)** — Postgres + a dashboard for browsing your own tables.

Once you have the connection string, set it as an environment variable on
whatever host runs this API (see below) and re-run `python seed.py` once
against that database to create the table and load starting data. After that
you can manage rows either through the API itself or straight in the
database.

## Deploying it

This needs to run somewhere with a long-lived process — not Netlify/GitHub
Pages (those are static-only, which is why your main site is separate from
this). **[Render](https://render.com)** has a free tier that's simplest for a
small FastAPI app like this:

1. Push this folder to its own GitHub repo (or a subfolder of one).
2. On Render: **New > Web Service**, connect the repo.
3. Build command: `pip install -r requirements.txt`
4. Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
5. Add environment variables from `.env.example` (at least `ADMIN_TOKEN`, and
   `DATABASE_URL` if you've moved to Postgres, and `ALLOWED_ORIGINS` set to
   your real site's URL once you know it).
6. Deploy. Render gives you a URL like `https://your-api.onrender.com`.

(Railway and Fly.io both work the same way if you'd rather use one of those.)

## Wiring the site to it

In the portfolio project, set `VITE_DRAFT_API_URL` (in a `.env` file, not
committed) to your deployed API's base URL, e.g.:

```
VITE_DRAFT_API_URL=https://your-api.onrender.com
```

The Draft Big Board tab calls `${VITE_DRAFT_API_URL}/api/draft-board` and
`/api/draft-board/meta` if that variable is set, and falls back to the
built-in static list if it's unset or unreachable — so the site never breaks
even if this API is down or asleep (Render's free tier spins down when idle
and takes a few seconds to wake back up on the next request).
