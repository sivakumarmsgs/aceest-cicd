# ACEest Fitness & Gym — DevOps CI/CD Pipeline

**Assignment 2 | Introduction to DevOps | CSIZG514/SEZG514**
**Name:** SIVAKUMAR.S | **ID:** 2024ht66534

---

## 📋 Project Overview

A complete DevOps CI/CD pipeline for the ACEest Fitness & Gym management system — a Flask REST API application that manages gym clients, fitness programs, workout logging, and progress tracking.

## 🛠️ Tech Stack

| Tool | Purpose |
|------|---------|
| Python / Flask | REST API application |
| Git / GitHub | Version control |
| Pytest | Unit testing (37 test cases) |
| Jenkins | CI/CD pipeline automation |
| SonarQube | Code quality analysis |
| Docker | Containerization |
| Kubernetes (AKS) | Deployment orchestration |
| Azure AKS | Cloud Kubernetes platform |

---

## 📁 Repository Structure

```
aceest-cicd/
├── app.py                          # Flask REST API (v3.2.4)
├── requirements.txt                # Python dependencies
├── Dockerfile                      # Multi-stage Docker build
├── Jenkinsfile                     # 7-stage CI/CD pipeline
├── sonar-project.properties        # SonarQube configuration
├── .gitignore                      # Git exclusions
├── tests/
│   └── test_app.py                 # 37 Pytest unit tests
└── k8s/
    ├── rolling-deployment.yaml     # Strategy 1: Rolling Update
    ├── blue-green-deployment.yaml  # Strategy 2: Blue-Green
    ├── blue-green-service.yaml     # Strategy 2: Blue-Green Service
    ├── canary-deployment.yaml      # Strategy 3: Canary Release
    ├── ab-testing-deployment.yaml  # Strategy 4: A/B Testing
    └── shadow-deployment.yaml      # Strategy 5: Shadow Deployment
```

---

## 🚀 Quick Start

### 1. Clone the repository
```bash
git clone https://github.com/sivakumarmsgs/aceest-cicd.git
cd aceest-cicd
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the application
```bash
python app.py
# App runs at http://localhost:5000
```

### 4. Run tests
```bash
pytest tests/test_app.py -v
# 37 tests — all passing
```

---

## 🐳 Docker

### Build image
```bash
docker build -t aceest-fitness:3.2.4 .
```

### Run container
```bash
docker run -d -p 5000:5000 --name aceest aceest-fitness:3.2.4
```

### Test health
```bash
curl http://localhost:5000/health
# {"status": "healthy", "version": "3.2.4"}
```

### Docker Hub
```
docker pull sivakumarmsgs/aceest-fitness:3.2.4
docker pull sivakumarmsgs/aceest-fitness:3.1.2
docker pull sivakumarmsgs/aceest-fitness:latest
```

---

## 🔌 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | / | App info and version |
| GET | /health | Health check |
| GET | /version | Version number |
| GET | /clients | List all clients |
| POST | /clients | Add new client |
| GET | /clients/<name> | Get client by name |
| DELETE | /clients/<name> | Delete client |
| POST | /workouts | Log a workout |
| GET | /workouts | List all workouts |
| POST | /metrics | Save body metrics |
| GET | /programs | List fitness programs |
| POST | /login | Authenticate user |

---

## 🧪 Testing

37 unit tests across 7 test classes:

| Test Class | Tests | Coverage |
|-----------|-------|---------|
| TestHealthAndVersion | 4 | /, /health, /version |
| TestClientManagement | 11 | Full CRUD + validation |
| TestWorkoutLogging | 6 | POST/GET + edge cases |
| TestMetricsTracking | 3 | POST metrics |
| TestProgramRecommendations | 5 | GET programs |
| TestAuthentication | 4 | Login valid/invalid |
| TestDataValidation | 4 | Data types + defaults |

```bash
# Run with coverage
pytest tests/test_app.py -v --cov=app --cov-report=term-missing
```

---

## ⚙️ Jenkins Pipeline

7-stage declarative pipeline:

```
Checkout → Setup → Lint → Unit Tests → SonarQube → Docker Build/Push → K8s Deploy
```

---

## ☸️ Kubernetes Deployment Strategies

| Strategy | File | Description |
|----------|------|-------------|
| Rolling Update | k8s/rolling-deployment.yaml | Zero-downtime incremental update |
| Blue-Green | k8s/blue-green-*.yaml | Instant traffic switch between two environments |
| Canary | k8s/canary-deployment.yaml | 10% traffic to new version |
| A/B Testing | k8s/ab-testing-deployment.yaml | Header-based routing |
| Shadow | k8s/shadow-deployment.yaml | Mirror traffic to shadow environment |

### Deploy to AKS
```bash
# Create namespace
kubectl create namespace aceest

# Apply all strategies
kubectl apply -f k8s/rolling-deployment.yaml
kubectl apply -f k8s/blue-green-deployment.yaml
kubectl apply -f k8s/blue-green-service.yaml
kubectl apply -f k8s/canary-deployment.yaml
kubectl apply -f k8s/ab-testing-deployment.yaml
kubectl apply -f k8s/shadow-deployment.yaml

# Verify
kubectl get deployments -n aceest
kubectl get pods -n aceest
kubectl get svc -n aceest
```

---

## 📊 Version History

| Version | Key Changes |
|---------|------------|
| v1.0 | Initial Flask app skeleton |
| v1.1 | Added client management |
| v1.1.2 | Calorie calculator |
| v2.0.1 | Workout logging |
| v2.1.2 | Metrics tracking |
| v2.2.1 | Program recommendations |
| v2.2.4 | Authentication |
| v3.0.1 | Docker support |
| v3.1.2 | Kubernetes manifests |
| v3.2.4 | Full CI/CD pipeline |

---

## 👤 Author

**SIVAKUMAR.S** | ID: 2024ht66534
GitHub: [@sivakumarmsgs](https://github.com/sivakumarmsgs)
Docker Hub: [sivakumarmsgs](https://hub.docker.com/u/sivakumarmsgs)
