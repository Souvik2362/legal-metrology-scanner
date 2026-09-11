Yes. A separate **`RUNNING.md`** is a good idea. Keep the main `README.md` focused on the project, and put the practical startup instructions in `RUNNING.md`.

Use this:

````markdown
# Running Metrology Scan

This guide explains how to run the Metrology Scan project locally.

## Prerequisites

Install:

- Python 3.12
- Node.js and npm
- Git

Python 3.12 is recommended for the current PaddleOCR/PaddlePaddle setup.

---

# 1. Clone the Repository

```bash
git clone https://github.com/Souvik2362/legal-metrology-scanner.git
cd legal-metrology-scanner
````

---

# 2. Start the Backend

Open a terminal in the project root.

```bat
cd backend
```

Create a Python virtual environment:

```bat
py -3.12 -m venv .venv
```

Activate it:

```bat
.venv\Scripts\activate
```

Install the backend dependencies:

```bat
py -3.12 -m pip install -r requirements.txt
```

Start the FastAPI server:

```bat
py -3.12 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

The backend should now be running at:

```text
http://localhost:8000
```

### Check Backend Status

Open:

```text
http://localhost:8000/api/v1/health
```

A successful response confirms that the backend is running.

---

# 3. Start the Frontend

Keep the backend terminal running.

Open a **second terminal** in the project root:

```bat
cd frontend
```

Install frontend dependencies:

```bat
npm install
```

Start the Next.js development server:

```bat
npm run dev
```

The frontend should now be available at:

```text
http://localhost:3000
```

Open this address in your browser.

---

# 4. Run a Product Scan

Once both servers are running:

1. Open `http://localhost:3000`.
2. Upload a product-label image.
3. Start the scan.
4. The frontend sends the image to the FastAPI backend.
5. The backend performs:

   * Image preprocessing
   * OCR
   * Information extraction
   * Compliance rule evaluation
6. The results are returned to the frontend.
7. Review the extracted declarations and compliance assessments.

---

# 5. Project Services

The application uses two local development servers:

| Service  | URL                     | Purpose                                    |
| -------- | ----------------------- | ------------------------------------------ |
| Frontend | `http://localhost:3000` | User interface                             |
| Backend  | `http://localhost:8000` | OCR, extraction, and compliance processing |

The frontend communicates with the backend through:

```text
POST /api/v1/scan
```

---

# 6. Testing the Backend

From the `backend` directory, with the virtual environment activated:

```bat
pytest
```

This runs the available backend tests.

---

# 7. Using the Test Images

Sample product-label images are available in:

```text
Test_Images/
```

You can use these images to test the scanning workflow.

---

# 8. Stopping the Servers

To stop either development server, press:

```text
Ctrl + C
```

Stop both the frontend and backend terminals when finished.

---

# Troubleshooting

## Backend does not start

Make sure Python 3.12 is installed:

```bat
py -3.12 --version
```

Then install the dependencies again:

```bat
py -3.12 -m pip install -r requirements.txt
```

---

## Frontend does not start

Make sure Node.js and npm are installed:

```bat
node --version
npm --version
```

Then run:

```bat
npm install
npm run dev
```

---

## Frontend cannot connect to the backend

Make sure the backend terminal is still running.

Check:

```text
http://localhost:8000/api/v1/health
```

If the health endpoint is unavailable, restart the backend:

```bat
cd backend
py -3.12 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

---

## First Scan Takes Longer

The first OCR scan may take longer because the OCR models may need to be initialized or downloaded.

Subsequent scans can be faster once the models are available locally.

---

# Quick Start

For subsequent runs, after the dependencies have already been installed:

### Terminal 1

```bat
cd backend
.venv\Scripts\activate
py -3.12 -m uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### Terminal 2

```bat
cd frontend
npm run dev
```

Then open:

```text
http://localhost:3000
```

````