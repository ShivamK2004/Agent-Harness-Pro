.PHONY: install test app web api benchmark
install:
	python -m pip install -r requirements.txt

test:
	python -m pytest -q

# Legacy Streamlit fallback
app:
	streamlit run app/streamlit_app.py

# Primary Next.js frontend (run FastAPI separately with `make api`)
web:
	cd frontend && npm install && npm run dev

api:
	uvicorn harness.api.main:app --reload --host 127.0.0.1 --port 8000

benchmark:
	python -m harness.cli benchmark
