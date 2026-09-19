# C4 — Career Intelligence

A premium Streamlit MVP for the Skill-Gap-to-Job Matching Agent.

## Product flow

Profile / Resume → Gemini 2.5 Flash extraction → local job matching → skill-gap analysis → course path.

Only the unstructured profile extraction uses Gemini. Matching and course recommendation are deterministic/local, so the demo is faster and uses fewer API requests.

## Setup

```powershell
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Copy `.env.example` to `.env` and put your Gemini key in it:

```env
GEMINI_API_KEY=your_key_here
```

Run:

```powershell
streamlit run app.py
```

## Demo mode

If Gemini quota is exhausted, click **Launch demo mode**. The UI and complete product flow still work without an API request.

## Notes

- Model is intentionally `gemini-2.5-flash`.
- Do not commit `.env`.
- Job and course data are local sample data for the hackathon MVP.
