# ACEest Fitness & Gym — CI/CD Pipeline

> **DevOps Assignment | BITS Pilani — Introduction to DevOps (CSIZG514)**  
> Automated CI/CD pipeline for the ACEest Fitness & Gym management application.

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Repository Structure](#repository-structure)  
3. [Local Setup & Execution](#local-setup--execution)  
4. [Running Tests Manually](#running-tests-manually)  
5. [Docker Usage](#docker-usage)  
6. [GitHub Actions — Pipeline Overview](#github-actions--pipeline-overview)  
7. [Jenkins — BUILD Stage Overview](#jenkins--build-stage-overview)  
8. [API Reference](#api-reference)

---

## Project Overview

ACEest is a Flask-based REST API for managing gym clients, fitness programs, and progress tracking. This repository demonstrates a production-grade DevOps workflow including version control, containerization, unit testing, and automated CI/CD pipelines.

**Technology Stack**

| Layer | Technology |
|-------|-----------|
| Application | Python 3.12 + Flask 3.0 |
| Testing | Pytest + pytest-cov |
| Containerization | Docker (multi-stage build) |
| CI/CD | GitHub Actions |
| BUILD Server | Jenkins (Declarative Pipeline) |
| Version Control | Git / GitHub |

---

## Repository Structure

```
aceest-cicd/
├── app.py                        # Flask application (main source)
├── requirements.txt              # Python dependencies
├── Dockerfile                    # Multi-stage Docker build
├── Jenkinsfile                   # Jenkins declarative pipeline
├── .gitignore
├── .github/
│   └── workflows/
│       └── main.yml              # GitHub Actions CI/CD pipeline
├── tests/
│   └── test_app.py               # Pytest test suite (35+ tests)
└── README.md
```

---

## Local Setup & Execution

### Prerequisites

- Python 3.12+
- pip
- Docker (optional, for container testing)

### 1. Clone the repository

```bash
git clone https://github.com/<your-username>/aceest-cicd.git
cd aceest-cicd
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Linux / macOS
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the Flask application

```bash
python app.py
```

The API will be available at `http://localhost:5000`.

---

## Running Tests Manually

```bash
# Run all tests with verbose output
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=term-missing

# Run a specific test class
pytest tests/test_app.py::TestAddClient -v
```

Expected output: **35 tests passing**.

---

## Docker Usage

### Build the image

```bash
docker build -t aceest-fitness:latest .
```

### Run the container

```bash
docker run -d -p 5000:5000 --name aceest aceest-fitness:latest
```

### Run tests inside the container

```bash
docker run --rm \
  -v $(pwd)/tests:/app/tests \
  -v $(pwd)/requirements.txt:/app/requirements.txt \
  --entrypoint "" aceest-fitness:latest \
  sh -c "pip install pytest pytest-cov -q && pytest tests/ -v"
```

### Stop & remove

```bash
docker stop aceest && docker rm aceest
```

---

## GitHub Actions — Pipeline Overview

**File:** `.github/workflows/main.yml`  
**Trigger:** Every `push` or `pull_request` to `main` / `develop`

The pipeline has **three sequential jobs**:

```
Push/PR → [Job 1: Build & Lint] → [Job 2: Automated Testing] → [Job 3: Docker Build]
```

### Job 1 — Build & Lint

- Checks out the repository
- Installs Python 3.12 and all dependencies (with pip caching)
- Runs `flake8` for syntax errors (hard fail on E9/F63/F7/F82)
- Verifies the application imports cleanly

### Job 2 — Automated Testing (Pytest)

- Depends on Job 1 passing (enforced via `needs:`)
- Runs the full Pytest suite with coverage reporting
- Uploads a `.coverage` artifact for inspection

### Job 3 — Docker Image Assembly

- Depends on Job 2 passing
- Builds the Docker image using Buildx (with layer caching via GHA cache)
- Mounts tests into the container and reruns Pytest inside Docker
- Performs a live smoke test (`curl` the running container)

---

## Jenkins — BUILD Stage Overview

**File:** `Jenkinsfile`  
**Type:** Declarative Pipeline

Jenkins serves as a secondary quality gate — ensuring the code builds and tests pass in a controlled CI server environment, independent of GitHub Actions.

### Jenkins Setup Steps

1. Install Jenkins on your server / VM (or use a local Docker container):
   ```bash
   docker run -d -p 8080:8080 -v jenkins_home:/var/jenkins_home jenkins/jenkins:lts
   ```
2. Install required plugins: **Git**, **Pipeline**, **JUnit**, **Docker Pipeline**.
3. Create a **New Item → Pipeline** project.
4. Under *Pipeline Definition*, select **Pipeline script from SCM**.
5. Set SCM to **Git** and provide your repository URL.
6. Set *Script Path* to `Jenkinsfile`.
7. Save and click **Build Now**.

### Pipeline Stages

| Stage | Description |
|-------|-------------|
| Checkout | Pulls latest code from GitHub |
| Environment Setup | Creates venv, installs all dependencies |
| Lint | Runs flake8 — fails on syntax errors |
| Unit Tests | Runs Pytest; publishes JUnit XML report |
| Docker Build | Builds tagged Docker image |
| Container Smoke Test | Starts container, verifies HTTP response |
| Archive | Saves test/coverage XML as artifacts |

---

## API Reference

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Health check / app info |
| GET | `/programs` | List all fitness programs |
| GET | `/clients` | List all registered clients |
| POST | `/clients` | Register a new client |
| GET | `/clients/<name>` | Get a single client |
| DELETE | `/clients/<name>` | Remove a client |
| POST | `/clients/<name>/progress` | Log weekly adherence |
| GET | `/calories?weight=&program=` | Quick calorie estimate |

### Example — Add a client

```bash
curl -X POST http://localhost:5000/clients \
  -H "Content-Type: application/json" \
  -d '{"name": "Arjun", "program": "Muscle Gain", "weight_kg": 75, "age": 28}'
```

```json
{
  "message": "Client added",
  "client": {
    "name": "Arjun",
    "age": 28,
    "weight_kg": 75,
    "program": "Muscle Gain",
    "calories": 2625,
    "workout": "Push/Pull/Legs",
    "membership_status": "Active"
  }
}
```
