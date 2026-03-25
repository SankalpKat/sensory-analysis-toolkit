# 🧪 Sensory Analysis Toolkit
**Live app:** [sensory-analysis-toolkit.streamlit.app](https://sensory-analysis-toolkit.streamlit.app)
Open-source double-blind randomized sensory trial designer for food scientists.

Plan, blind, and run consumer sensory trials without expensive software. Generates trial designs, blinding codes, panelist ballots, and digital survey links — all from a single web app.

---

## Features

- **Three trial designs** — Williams Latin Square, Balanced Incomplete Block (BIB), Monadic Sequential
- **Algorithmic design suggestion** — recommends the right design based on your inputs
- **Blinding by default** — unique 3-digit codes per product, locked before trial starts
- **PDF ballot export** — print-ready ballots per panelist or all-in-one
- **Digital survey links** — unique URL per panelist, responses stored in database
- **Live response tracking** — see who has submitted in real time
- **Power calculator** — minimum panel size for a given effect size and confidence level
- **Results export** — download all responses as a formatted Excel file

---

## Quickstart
```bash
git clone https://github.com/SankalpKat/sensory-analysis-toolkit.git
cd sensory-analysis-toolkit
pip install -r requirements.txt
streamlit run app.py
```

---

## Setup — Digital Survey (optional)

The digital survey feature requires a free Supabase account.

1. Create a project at [supabase.com](https://supabase.com)
2. Run the following SQL in the Supabase SQL Editor:
```sql
CREATE TABLE trials (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    trial_name TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT now(),
    config JSONB NOT NULL
);

CREATE TABLE panelists (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    trial_id UUID REFERENCES trials(id),
    panelist_number INTEGER NOT NULL,
    access_token TEXT UNIQUE NOT NULL,
    serving_order JSONB NOT NULL,
    submitted BOOLEAN DEFAULT FALSE
);

CREATE TABLE responses (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    panelist_id UUID REFERENCES panelists(id),
    trial_id UUID REFERENCES trials(id),
    sample_position INTEGER NOT NULL,
    blinding_code INTEGER NOT NULL,
    ratings JSONB NOT NULL,
    submitted_at TIMESTAMP DEFAULT now()
);
```

3. Create a `.env` file in the project root:
```
SUPABASE_URL=your_project_url
SUPABASE_KEY=your_anon_key
```

---

## Trial Designs

| Design | Use when | Products per panelist |
|---|---|---|
| Williams Latin Square | 2-6 products, trained panels | All products |
| Balanced Incomplete Block | 7+ products, fatigue risk | A subset (k) |
| Monadic Sequential | Consumer panels, large groups | All products |

---

## Roadmap

- [ ] Streamlit Cloud deployment guide
- [ ] QR code generation per panelist link
- [ ] Multi-session trial support with washout scheduling
- [ ] Statistical analysis module — ANOVA, d-prime, preference mapping
- [ ] Full self-hosted mode — no Supabase account required

---

## Stack

- [Streamlit](https://streamlit.io)
- [Supabase](https://supabase.com)
- [pandas](https://pandas.pydata.org) / [NumPy](https://numpy.org)
- [SciPy](https://scipy.org)
- [fpdf2](https://py-fpdf2.readthedocs.io)
- [openpyxl](https://openpyxl.readthedocs.io)

---

## License

MIT