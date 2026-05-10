# Student Search with Apache Solr (Lab 13)

This is a small lab project where student records are indexed in **Apache Solr** and shown in a simple frontend dashboard.

The UI supports:
- full search
- filtering by department, year, and CGPA range
- sorting
- highlighting

I used a tiny **Flask proxy** (`app.py`) so the frontend can call Solr cleanly without browser CORS/network issues.

## Project files

- `students.csv` — dataset
- `index.html` — frontend UI
- `app.py` — Flask app + Solr proxy
- `solr-9.6.0/` — local Solr distribution

## Quick start

### 1. Start Solr

```bash
cd "/mnt/c/Users/abdib/Pictures/LECTURES/LABS/DL LABS/LAB 13 PDC/solr-9.6.0"
bin/solr start -p 8983 -h 127.0.0.1
```

### 2. Create core and index data (first time only)

```bash
bin/solr create -c students
bin/solr post -c students ../students.csv
curl "http://127.0.0.1:8983/solr/students/update?commit=true"
```

### 3. Create and activate Python virtual environment

```bash
cd "/mnt/c/Users/abdib/Pictures/LECTURES/LABS/DL LABS/LAB 13 PDC"
python3 -m venv .venv
source .venv/bin/activate
pip install flask requests
```

### 4. Run the Flask app

```bash
export SOLR_BASE="http://127.0.0.1:8983/solr"
python app.py
```

### 5. Open in browser

- `http://localhost:5000`

If localhost forwarding does not work on your machine, use your WSL IP:
- `http://<your-wsl-ip>:5000`

## Useful test query

```bash
curl "http://127.0.0.1:8983/solr/students/select?q=*:*&rows=5&wt=json"
```

## Notes

- Solr startup warnings about file/process limits are common in local lab setups.
- `favicon.ico` 404 in Flask logs is harmless.
- If you close terminal sessions, restart both Solr and Flask.
