# Contribuire a Imprese Italia

Come partecipare al progetto.

## Modi per contribuire

1. **Segnalare un problema** — aprendo un'issue
2. **Proporre un'analisi** — con una Discussion
3. **Aggiungere dati** — con una Pull Request
4. **Migliorare il codice** — con una Pull Request

## Setup locale

```bash
# Clona
git clone <repo-url>
cd imprese-italia

# Esegui la pipeline
make run-all

# Verifica i dati
duckdb out/data/mart/camcom_stock_italia/2026/mart_provincia_ateco.parquet
```

## Struttura dei dataset

Ogni dataset segue il pattern `raw → clean → mart`:

- **`dataset.yml`** — contratto della pipeline
- **`camcom_download.py`** — script di download
- **`sql/clean.sql`** — pulizia (legge solo da `raw_input`)
- **`sql/mart_*.sql`** — aggregazioni (leggono solo da `clean_input`)

## Regole

- Ogni `clean.sql` legge **solo** da `raw_input`
- Ogni `mart*.sql` legge **solo** da `clean_input` o da `{support.*}`
- Validazione obbligatoria: `min_rows`, `not_null`, `primary_key`
- Nessun file dati committato in root
- Output in `.gitignore`

## Codice di condotta

- Rispetto per tutti i contributor
- Focus sui dati e sulla qualità
- Trasparenza sulle fonti e sui limiti
