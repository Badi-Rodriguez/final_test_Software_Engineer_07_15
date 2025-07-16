# Ride Management System (UTEC)

## Setup

1. Create a virtual environment:
   ```bash
   python -m venv venv
   src venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
2. Install dependencies:
   ```bash
   pip install fastapi uvicorn pydantic
   ```
3. Run the app:
   ```bash
   uvicorn main:app --reload
   ``` 