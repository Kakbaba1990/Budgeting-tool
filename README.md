# Budgeting Tool

Een uitgebreide, lokale budgeting tool waarmee je inkomsten, uitgaven, budgetten en spaardoelen beheert via de command line.
De data wordt opgeslagen in een JSON-bestand, zodat je alles makkelijk kunt bijhouden en exporteren.

## Features

- **Inkomsten & uitgaven registreren** met categorie, datum en notitie.
- **Budgetten per categorie** instellen en vergelijken met je uitgaven.
- **Maandelijkse samenvatting** met totalen, balans en categorie-overzicht.
- **Spaardoelen beheren** met target, huidige stand en deadline.
- **CSV-export** van transacties.

## Installatie

Gebruik de standaard Python-installatie (3.10+ aanbevolen). Er zijn geen externe dependencies.

```bash
python -m venv .venv
source .venv/bin/activate
```

## Basisgebruik

Initialiseer een nieuw databestand:

```bash
python -m budgeting_tool init --data budget.json --currency EUR
```

Inkomsten toevoegen:

```bash
python -m budgeting_tool add-income --data budget.json --amount 2500 --category Salaris --date 2024-03-01 --note "Maandloon"
```

Uitgaven toevoegen:

```bash
python -m budgeting_tool add-expense --data budget.json --amount 75.50 --category Boodschappen --date 2024-03-02 --note "Weekboodschappen"
```

Budget per categorie instellen:

```bash
python -m budgeting_tool set-budget --data budget.json --category Boodschappen --amount 300
```

Maandoverzicht:

```bash
python -m budgeting_tool summary --data budget.json --month 2024-03
```

Spaardoel toevoegen:

```bash
python -m budgeting_tool goals add --data budget.json --name "Noodfonds" --target 2000 --saved 500 --deadline 2024-12-31
```

Transacties exporteren naar CSV:

```bash
python -m budgeting_tool export-csv --data budget.json --output transacties.csv
```

## Tips

- Gebruik `list` om alle transacties te bekijken.
- Voeg `--month` toe aan `list` of `summary` om te filteren op maand (YYYY-MM).
- Bewaar het JSON-bestand in een cloud-map als je het op meerdere apparaten wilt gebruiken.

## Commandolijst (kort)

- `init`
- `add-income`
- `add-expense`
- `set-budget`
- `list`
- `summary`
- `goals add`
- `goals list`
- `export-csv`

## Licentie

MIT
