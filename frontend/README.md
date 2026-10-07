# DecideHer executive dashboard

This is the supplied React frontend integrated with the Python pipeline. It reads the portfolio contract from `../static/dashboard/dashboard.json` when served by Streamlit.

## Run Locally

**Prerequisite:** Node.js


1. Run `npm install`.
2. Run `npm run build` to write the production dashboard into `../static/dashboard`.
3. Return to the repository root and run `streamlit run app.py`.

No frontend API key is required. Engine 2 produces the output contract in Python.
