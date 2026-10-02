# Imprese Italia

**Quante imprese nascono, crescono e muoiono in Italia? Quali settori tirano l'economia reale?**

Sistema di intelligence sulla demografia d'impresa italiana: raccoglie dati dal Registro delle Imprese (Camera di Commercio delle Marche / InfoCamere) e li trasforma in indicatori su stock, flussi, variazioni e specializzazione territoriale.

- **Copertura:** Italia nazionale + 227 comuni delle Marche
- **Periodo:** Aprile 2025 – Agosto 2026 (mensile)
- **Granolarità:** Province italiane (2 cifre ATECO) + Comuni Marche (6 cifre ATECO)
- **Fonte:** [opendata.marche.camcom.it](https://opendata.marche.camcom.it) — CC-BY 4.0
- **Dashboard:** [dcl-imprese.streamlit.app](https://dcl-imprese.streamlit.app/)

## Dashboard

App Streamlit pubblica con Panoramica, Settori, Territorio, Marche e Query SQL.
Legge i mart su GCS (`gs://dataciviclab-mart|clean/imprese-italia/`) via
[lab-connectors](https://github.com/dataciviclab/lab-connectors).

```bash
cd dashboard
pip install -r requirements.txt
streamlit run app.py
```

Sviluppo locale: se `out/data/` è presente, i loader usano i parquet locali;
altrimenti cadono su GCS.

## Cosa risponde

**Dove sta crescendo l'economia italiana? Quali settori muoiono? Cosa fa Fabriano rispetto ad Ancona?**

Il sistema copre il ciclo di vita completo delle imprese: nascita (iscrizioni), vita (stock), morte (cancellazioni), e cambiamento (variazione tendenziale). La granolarità comunale nelle Marche permette analisi di micro-territorio rare in fonti开放.

## Dataset

| Dataset | Cosa | Righe | Copertura |
|---------|------|-------|-----------|
| `camcom_stock_italia` | Stock imprese per provincia × ATECO 2 + serie Italia/territori | 51K | Italia, mensile |
| `camcom_stock_marche` | Stock imprese per comune × ATECO 2 + serie comuni | 92K | Marche, mensile |
| `camcom_variazione` | Variazione % YoY per provincia × ATECO + serie Italia | 15K | Italia, mensile |
| `camcom_iscrizioni` | Nuove iscrizioni al Registro + serie Italia | 51K | Italia, mensile |
| `camcom_cancellazioni` | Cessazioni dal Registro + serie Italia | 51K | Italia, mensile |
| `camcom_stock_italia_6cifre` | Stock per provincia × ATECO 6 cifre + gerarchia piena | 112K | Italia, snapshot |
| `camcom_stock_marche_6cifre` | Stock per comune × ATECO 6 cifre + gerarchia piena | 34K | Marche, snapshot |
| `demografia_imprese` (compose) | Bilancio mensile, composizione, specializzazione Marche, codici anomali | 49K | Italia + Marche |

### Mart analitici (nuovi)

| Mart | Dataset | Cosa |
|------|---------|------|
| `mart_serie_italia_ateco` | stock / iscrizioni / cancellazioni / variazione | Serie mensile Italia × ATECO (share % dove applicabile) |
| `mart_serie_territorio` | stock_italia | Serie mensile per territorio con `territorio_tipo` (ITALIA/REGIONE/PROVINCIA) |
| `mart_serie_comune` | stock_marche | Serie mensile comuni Marche (TOTAL) |
| `mart_gerarchia` | stock_*_6cifre | Gerarchia ATECO completa (divisione/classe/sottocategoria) |
| `mart_bilancio_mensile` | demografia_imprese | stock + iscrizioni + cessazioni + netto per ATECO × mese |
| `mart_composizione_ateco` | demografia_imprese | Share % stock per ATECO × territorio × mese |
| `mart_specializzazione` | demografia_imprese | RCA Marche vs Italia per ATECO (ultimo mese) |
| `mart_codici_anomali` | demografia_imprese | Flag codici rari X/V/U/P con variazione YoY |

Codelist etichette ATECO: `compose/demografia-imprese/codelists/ateco_2.csv` (support `file`).

## Come accedere

### Dashboard (più rapido)

[dcl-imprese.streamlit.app](https://dcl-imprese.streamlit.app/) — KPI, trend, settori, territorio, Marche.

### DuckDB / GCS

```sql
-- Top comuni Marche (mart)
SELECT comune, SUM(imprese) AS totale
FROM read_parquet('gs://dataciviclab-mart/imprese-italia/camcom_stock_marche_6cifre/2026/mart_6cifre_comune.parquet')
GROUP BY comune ORDER BY totale DESC LIMIT 10;

-- Bilancio demografico Italia per ATECO (compose)
SELECT ateco, stock, iscrizioni, cessazioni, netto
FROM read_parquet('gs://dataciviclab-mart/imprese-italia/demografia_imprese/2026/mart_bilancio_mensile.parquet')
WHERE data = (SELECT MAX(data) FROM read_parquet('gs://dataciviclab-mart/imprese-italia/demografia_imprese/2026/mart_bilancio_mensile.parquet'))
ORDER BY netto DESC;
```

In locale i path sono `out/data/mart/...` dopo `make run-all`.

### Makefile
```bash
make check    # valida dataset.yml + compose
make run-all  # pipeline completa (datasets + compose)
make clean    # pulisci output
```

## Esempi di domande

1. **Quali settori crescono in Italia?** → `camcom_variazione` ordina per YoY %
2. **Com'è fatta l'economia di Pesaro?** → `camcom_stock_marche_6cifre` filtra per comune
3. **Quante imprese nascono vs muoiono?** → crocetta iscrizioni + cancellazioni
4. **Le Marche sono diverse dall'Italia?** → indice di specializzazione (stock Marche / stock Italia)
5. **Quali sottocategorie dominano a Fermo?** → 6-cifre filtrato per provincia

## Struttura

```
imprese-italia/
├── compose/
│   └── demografia-imprese/   # bilancio, composizione, RCA, codici anomali
├── dashboard/                # Streamlit → dcl-imprese.streamlit.app
├── datasets/
│   ├── camcom_stock_italia/
│   ├── camcom_stock_marche/
│   ├── camcom_variazione/
│   ├── camcom_iscrizioni/
│   ├── camcom_cancellazioni/
│   ├── camcom_stock_italia_6cifre/
│   └── camcom_stock_marche_6cifre/
├── Makefile
├── pyproject.toml
├── README.md
└── .github/workflows/
```

## Fonte e licenza

- **Fonte:** [Camera di Commercio delle Marche — Open Data Explorer](https://opendata.marche.camcom.it)
- **Dati:** Registro delle Imprese (InfoCamere) — dati aggregati statistici
- **Licenza dati:** CC-BY 4.0 — citare "opendata.marche.camcom.it, CCIAA Marche su dati InfoCamere"
- **Licenza codice:** MIT

## Partecipa

Hai domande sull'economia italiana? Vuoi analizzare un territorio specifico? [Aprite una Discussion](https://github.com/dataciviclab/imprese-italia/discussions) o segnalate un problema con un'issue.

---

*Sistema creato con [DataCivicLab Toolkit](https://github.com/dataciviclab/toolkit)*
