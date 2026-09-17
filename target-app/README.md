# target-app

A small order management API used as the review target throughout the workshop.

## This application is intentionally vulnerable

It contains real, exploitable security defects that were put there on purpose. That is its job.

**Never expose it beyond localhost.** Do not deploy it, do not put it on a shared network, do not run it on a work machine that is reachable from anywhere else, and do not copy code out of it into anything real. It binds to `127.0.0.1` and you should leave it that way.

The answer key is in `PLANTED.md`. If you are an attendee working the labs, do not read it yet.

## Running it

From the repository root, activate the virtual environment first.

```bash
source .venv/bin/activate
cd target-app
python app.py
```

```powershell
.\.venv\Scripts\Activate.ps1
cd target-app
python app.py
```

It listens on `http://127.0.0.1:5000` and creates `app.db` next to the source on first run, seeded with two users and five orders.

To start over, delete `app.db` and run it again.

## Logging in

Both seeded users have the password `password123`.

| Username | Owns orders |
|---|---|
| alice | 1, 2, 3 |
| bob | 4, 5 |

```bash
curl -c cookies.txt -X POST http://127.0.0.1:5000/api/login \
  -H "Content-Type: application/json" \
  -d '{"username": "alice", "password": "password123"}'

curl -b cookies.txt http://127.0.0.1:5000/api/orders
```

```powershell
$session = New-Object Microsoft.PowerShell.Commands.WebRequestSession
Invoke-RestMethod -Uri http://127.0.0.1:5000/api/login -Method Post `
  -ContentType "application/json" `
  -Body '{"username": "alice", "password": "password123"}' -WebSession $session

Invoke-RestMethod -Uri http://127.0.0.1:5000/api/orders -WebSession $session
```

## Endpoints

| Method | Path | What it does |
|---|---|---|
| POST | `/api/login` | Start a session |
| POST | `/api/logout` | End a session |
| GET | `/api/orders` | List the caller's own orders |
| GET | `/api/orders/<id>` | Fetch one order by id |
| GET | `/api/search?q=` | Search orders by item name |
| GET | `/api/export?format=` | Generate a report |
| GET | `/api/downloads` | List downloadable files |
| GET | `/api/download?name=` | Download a file by name |

## Layout

| File | Concern |
|---|---|
| `app.py` | Routes and application setup |
| `auth.py` | Sessions and access control decorators |
| `models.py` | Queries against users and orders |
| `storage.py` | File downloads and report generation |
| `db.py` | Connection handling, schema, and first-run seeding |
| `uploads/` | Files served by the download endpoint |
| `internal_notes.txt` | Sits outside `uploads/`, used to prove one of the bugs |

## Tests

The suite has two halves. `test_app_runs.py` proves the API works as intended, so the exploits are demonstrating real defects rather than a broken application. `test_planted_bugs.py` has one exploit per planted bug, each named for the bug it proves.

```bash
cd target-app
python -m pytest tests/ -v
```

```powershell
cd target-app
python -m pytest tests\ -v
```

Every test uses the Flask test client against a throwaway database, so nothing binds a port and nothing touches `app.db`.

If a test in `test_planted_bugs.py` fails, the bug it covers has been fixed and `PLANTED.md` needs updating.
