# Imprese Italia

**Quante imprese nascono, crescono e muoiono in Italia? Quali settori tirano l'economia reale?**

Sistema di intelligence sulla demografia d'impresa italiana: raccoglie dati dal Registro delle Imprese (Camera di Commercio delle Marche / InfoCamere) e li trasforma in indicatori su stock, flussi, variazioni e specializzazione territoriale.

- **Copertura:** Italia nazionale + 227 comuni delle Marche
- **Periodo:** Aprile 2025 – Agosto 2026 (mensile)
- **Granolarità:** Province italiane (2 cifre ATECO) + Comuni Marche (6 cifre ATECO)
- **Fonte:** [opendata.marche.camcom.it](https://opendata.marche.camcom.it) — CC-BY 4.0

## Cosa risponde

**Dove sta crescendo l'economia italiana? Quali settori muoiono? Cosa fa Fabriano rispetto ad Ancona?**

Il sistema copre il ciclo di vita completo delle imprese: nascita (iscrizioni), vita (stock), morte (cancellazioni), e cambiamento (variazione tendenziale). La granolarità comunale nelle Marche permette analisi di micro-territorio rare in fonti开放.

## Dataset

| Dataset | Cosa | Righe | Copertura |
|---------|------|-------|-----------|
| `camcom_stock_italia` | Stock imprese per provincia × ATECO 2 | 51K | Italia, mensile |
| `camcom_stock_marche` | Stock imprese per comune × ATECO 2 | 27K | Marche, mensile |
| `camcom_variazione` | Variazione % YoY per provincia × ATECO | 5K | Italia, mensile |
| `camcom_iscrizioni` | Nuove iscrizioni al Registro | 5K | Italia, mensile |
| `camcom_cancellazioni` | Cessazioni dal Registro | 5K | Italia, mensile |
| `camcom_stock_italia_6cifre` | Stock per provincia × ATECO 6 cifre | 112K | Italia, snapshot |
| `camcom_stock_marche_6cifre` | Stock per comune × ATECO 6 cifre | 34K | Marche, snapshot |

## Come accedere

### DuckDB (consigliato)
```sql
-- Top comuni Marche per numero imprese
SELECT territorio, SUM(imprese) AS totale
FROM read_parquet('out/data/mart/camcom_stock_marche/2026/mart_comune_ateco.parquet')
WHERE ateco != 'TOTAL'
GROUP BY territorio ORDER BY totale DESC LIMIT 10;

-- Bilancio demografico per settore (Italia)
WITH stock AS (
    SELECT ateco, imprese AS stock FROM read_parquet('out/data/mart/camcom_stock_italia/2026/mart_provincia_ateco.parquet')
    WHERE territorio = 'ITALIA' AND ateco != 'TOTAL'
),
flussi AS (
    SELECT i.ateco, i.nuove_imprese AS iscrizioni, c.cessazioni
    FROM read_parquet('out/data/mart/camcom_iscrizioni/2026/mart_iscrizioni_provincia.parquet') i
    JOIN read_parquet('out/data/mart/camcom_cancellazioni/2026/mart_cancellazioni_provincia.parquet') c
    ON i.ateco = c.ateco
    WHERE i.territorio = 'ITALIA' AND i.ateco != 'TOTAL'
)
SELECT s.ateco, s.stock, f.iscrizioni, f.cessazioni,
       f.iscrizioni - f.cessazioni AS netto
FROM stock s JOIN flussi f ON s.ateco = f.ateco ORDER BY netto DESC;
```

### Makefile
```bash
make check    # valida tutti i dataset.yml
make run-all  # esegui pipeline completa
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
└── .github/workflows/ci.yml
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
