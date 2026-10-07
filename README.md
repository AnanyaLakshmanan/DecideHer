# DecideHer · AI Transformation Roadmap

This Streamlit app implements the complete nine-stage pipeline:

1. Intake use cases and the owned-systems list.
2. Keep identifying information separate before model processing.
3. Cluster requests by derived capability type and data object.
4. Match clusters against systems the organisation already owns.
5. Score each Engine 1 cluster with deterministic Engine 2 rules.
6. Apply the evidence gate and readiness confidence cap.
7. Preserve the interview fields required for targeted follow-up.
8. Surface root-cause and stakeholder disagreements.
9. Publish one traceable portfolio finding per cluster.

The UI has two screens and no sidebar navigation. It opens on the input form; submitting the form runs Engine 1 and then opens the Engine 2 output. Engine 2 cannot run before Engine 1 has produced a cluster.

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Complete the input form and select **Submit AI improvement idea**. The app stores the submitted form in hosted PostgreSQL, runs Engine 1 using the owned-systems data, and opens the output screen automatically.

The repository data lives in `data/sample_submissions.json` and `data/owned_systems.json`. The IT Context page is generated from `data/owned_systems.csv`; registered systems are stored in hosted PostgreSQL and feed owned-system matching and technology-readiness scoring. Engine 1 derives `capability_type` and `data_object`, then clusters on that pair rather than raw text similarity. Engine 2 applies the field definitions and formulas in `data/decision_output_fields.csv`; this is the renamed copy of the supplied `derived_fields 2.csv` reference.

The supplied executive frontend is integrated in `frontend/` and receives pipeline output through `static/dashboard/dashboard.json`. Rebuild it after changing React code:

```bash
cd frontend
npm install
npm run build
cd ..
```

The portfolio output is deterministic and does not require OpenAI. The legacy interview helper can use OpenAI structured output when `OPENAI_API_KEY` is present. `OPENAI_MODEL` is optional and defaults to `gpt-6-astra`. Never commit `api_key.env`.

Submissions are stored without anonymisation. Configure `DATABASE_URL` in `api_key.env` with a pooled PostgreSQL connection string that includes `sslmode=require`. The app creates the `issues`, `clusters`, and `owned_systems` tables automatically. The `issues` table contains the complete intake record, derived fields, and pipeline metadata.

For Supabase, create a free project, choose **Connect → Session pooler**, copy the connection string, replace the password placeholder, and save it as `DATABASE_URL`. Do not commit `api_key.env`.

The `issues` table schema is generated from the `field_name` column in `data/form_fields.csv`. Every form answer—including name, email, company, generated summary, and issue details—has a directly queryable column. Pipeline metadata and derived Engine 1 values are stored in additional columns.

The hosted database starts without demo submissions. New user submissions are stored when the intake form is submitted. The optional `sample_data.py` utility can seed the 20 representative records from `data/sample_submissions.json` when demo data is explicitly wanted.

The output screen shows the imported executive dashboard using current PostgreSQL records. Open an initiative to see its impact formula result, four readiness dimensions and sources, evidence and verdict confidence, evidence gate, finding drivers, and source references. Engine 1 reclusters all database records whenever a new valid submission is added.

## Test

```bash
pytest -q
```
