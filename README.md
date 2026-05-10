# CorVo Website

CorVo (Corpora for Volcanoes) brings together historical volcanology, linguistics, and computational linguistics to support research on volcanic activity and its cultural impact. The project uses historical written sources to help researchers and stakeholders study past eruptive scenarios, improve volcanic risk forecasting, assess impacts, and plan for resilience.

The website provides access to the CorVo corpus, a searchable collection of historical documents about past activity of Vesuvius. The current interface lets users explore approximately 200 digitised documents, the spatial data they contain, and curated metadata; searches can surface information such as precursors, eruptive phenomena, deposit distribution, damages, social impact, and institutional responses.

Live website: [https://www.corvo-project.eu/](https://www.corvo-project.eu/)

Funded by: PNRR - Mission 4 - Component 2 - Investment 3.1 - MEET Project (Monitoring Earth's Evolution and Tectonics) - WP 11 ISPES - Action 11c.

## Project Structure

- `frontend/`: Vue 3 and Vite application.
- `backend/`: FastAPI application and OCR/document search index code.

## Backend

From the repository root:

```bash
python3 -m venv env
source env/bin/activate
pip install -r backend/requirements.txt
cp backend/.env-example backend/.env
```

Edit `backend/.env` if needed, then start the API:

```bash
cd backend
uvicorn api.main:app --reload
```

By default, the API will be available at `http://localhost:8000/`.

## Frontend

In another terminal, from the repository root:

```bash
cd frontend
npm install
cp .env-example .env
npm run dev
```

Vite will print the local development URL, usually `http://localhost:5173/`.

## Environment Variables

Backend variables are documented in `backend/.env-example`.

- `DATABASE_URL`: SQLAlchemy database URL used by the FastAPI backend. The example value points to the bundled SQLite database when the backend is started from the `backend/` directory.

Frontend variables are documented in `frontend/.env-example`.

- `VITE_API_BASE_URL`: Base URL for the FastAPI backend. Keep the trailing slash because the frontend appends route paths directly.
- `VITE_BASE_URL`: Base URL for frontend routes used by map popup links. Keep the trailing slash.

## Citation

If you use this system in your work, please cite our paper, [Extracting Volcanological Knowledge from Historical Texts: A Language-Technology Pipeline for Diachronic Geovisualization](LT4HALA_2026_CorVo.pdf), presented at [LT4HALA](https://circse.github.io/LT4HALA/2026/Program).

```bibtex
@inproceedings{marini2026extracting,
  title = {Extracting Volcanological Knowledge from Historical Texts: A Language-Technology Pipeline for Diachronic Geovisualization},
  author = {Marini, Costanza and Casagrande, Gianluca and Palmero Aprosio, Alessio and Principe, Claudia},
  booktitle = {Proceedings of the Fourth Workshop on Language Technologies for Historical and Ancient Languages (LT4HALA 2026)},
  year = {2026}
}
```
