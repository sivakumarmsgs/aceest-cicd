// Jenkinsfile — ACEest Fitness & Gym
// Declarative Pipeline for the BUILD quality gate

pipeline {

    agent any

    environment {
        APP_NAME    = 'aceest-fitness'
        IMAGE_TAG   = "${APP_NAME}:${env.BUILD_NUMBER}"
        PYTHON_CMD  = 'python3'
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 20, unit: 'MINUTES')
        timestamps()
    }

    stages {

        // ── Stage 1: Checkout ───────────────────────────────────────────────
        stage('Checkout') {
            steps {
                echo "Checking out code from GitHub..."
                checkout scm
                sh 'git log --oneline -5'
            }
        }

        // ── Stage 2: Environment Setup ──────────────────────────────────────
        stage('Environment Setup') {
            steps {
                echo "Setting up Python virtual environment..."
                sh """
                    ${PYTHON_CMD} -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install flake8
                """
            }
        }

        // ── Stage 3: Lint ───────────────────────────────────────────────────
        stage('Lint') {
            steps {
                echo "Running flake8 syntax check..."
                sh """
                    . venv/bin/activate
                    flake8 app.py --count --select=E9,F63,F7,F82 --show-source --statistics
                """
            }
        }

        // ── Stage 4: Unit Tests ─────────────────────────────────────────────
        stage('Unit Tests') {
            steps {
                echo "Running Pytest suite..."
                sh """
                    . venv/bin/activate
                    pytest tests/ -v --tb=short \
                           --junitxml=reports/pytest-results.xml \
                           --cov=app --cov-report=xml:reports/coverage.xml
                """
            }
            post {
                always {
                    junit 'reports/pytest-results.xml'
                }
            }
        }

        // ── Stage 5: Docker Build ───────────────────────────────────────────
        stage('Docker Build') {
            steps {
                echo "Building Docker image: ${IMAGE_TAG}"
                sh "docker build -t ${IMAGE_TAG} ."
                sh "docker images | grep ${APP_NAME}"
            }
        }

        // ── Stage 6: Container Smoke Test ───────────────────────────────────
        stage('Container Smoke Test') {
            steps {
                echo "Running smoke test on container..."
                sh """
                    docker run -d --name aceest_ci_${BUILD_NUMBER} -p 5001:5000 ${IMAGE_TAG}
                    sleep 5
                    curl -f http://localhost:5001/ || (docker logs aceest_ci_${BUILD_NUMBER} && exit 1)
                """
            }
            post {
                always {
                    sh """
                        docker stop aceest_ci_${BUILD_NUMBER} || true
                        docker rm   aceest_ci_${BUILD_NUMBER} || true
                    """
                }
            }
        }

        // ── Stage 7: Archive Artifacts ──────────────────────────────────────
        stage('Archive') {
            steps {
                echo "Archiving build artifacts..."
                archiveArtifacts artifacts: 'reports/*.xml', allowEmptyArchive: true
            }
        }
    }

    post {
        success {
            echo "BUILD PASSED — ACEest ${IMAGE_TAG} is ready."
        }
        failure {
            echo "BUILD FAILED — Check logs above for details."
        }
        always {
            sh "docker rmi ${IMAGE_TAG} || true"
            cleanWs()
        }
    }
}
