// ============================================================
// ACEest Fitness & Gym - Jenkinsfile
// Task 4 & 7: CI Pipeline with Build, Test, SonarQube, Docker
// ============================================================

pipeline {
    agent any

    environment {
        APP_NAME        = "aceest-fitness"
        APP_VERSION     = "3.2.4"
        DOCKER_HUB_USER = credentials('dockerhub-username')
        DOCKER_IMAGE    = "${DOCKER_HUB_USER}/${APP_NAME}"
        SONAR_HOST      = "http://localhost:9000"
        SONAR_TOKEN     = credentials('sonarqube-token')
        KUBECONFIG      = credentials('kubeconfig')
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '10'))
        timeout(time: 30, unit: 'MINUTES')
        timestamps()
    }

    triggers {
        // Poll GitHub every 2 minutes for changes
        pollSCM('H/2 * * * *')
    }

    stages {

        // -------------------------------------------------------
        // Stage 1: Checkout Source Code
        // -------------------------------------------------------
        stage('Checkout') {
            steps {
                echo "==> Checking out source code from GitHub..."
                checkout scm
                sh 'git log --oneline -5'
            }
        }

        // -------------------------------------------------------
        // Stage 2: Setup Python Environment
        // -------------------------------------------------------
        stage('Setup Environment') {
            steps {
                echo "==> Setting up Python virtual environment..."
                sh '''
                    python3 -m venv venv
                    . venv/bin/activate
                    pip install --upgrade pip
                    pip install -r requirements.txt
                    pip install pytest pytest-cov flake8
                '''
            }
        }

        // -------------------------------------------------------
        // Stage 3: Code Linting
        // -------------------------------------------------------
        stage('Lint') {
            steps {
                echo "==> Running flake8 linting..."
                sh '''
                    . venv/bin/activate
                    flake8 app.py --max-line-length=120 --ignore=E501,W503 || true
                '''
            }
        }

        // -------------------------------------------------------
        // Stage 4: Unit Tests with Pytest
        // -------------------------------------------------------
        stage('Unit Tests') {
            steps {
                echo "==> Running Pytest unit tests..."
                sh '''
                    . venv/bin/activate
                    pytest tests/test_app.py \
                        --tb=short \
                        --junitxml=reports/junit.xml \
                        --cov=app \
                        --cov-report=xml:reports/coverage.xml \
                        --cov-report=html:reports/htmlcov \
                        -v
                '''
            }
            post {
                always {
                    junit 'reports/junit.xml'
                    publishHTML(target: [
                        reportName : 'Coverage Report',
                        reportDir  : 'reports/htmlcov',
                        reportFiles: 'index.html'
                    ])
                }
            }
        }

        // -------------------------------------------------------
        // Stage 5: SonarQube Analysis
        // -------------------------------------------------------
        stage('SonarQube Analysis') {
            steps {
                echo "==> Running SonarQube static code analysis..."
                withSonarQubeEnv('SonarQube') {
                    sh """
                        sonar-scanner \
                          -Dsonar.projectKey=${APP_NAME} \
                          -Dsonar.projectName="ACEest Fitness & Gym" \
                          -Dsonar.projectVersion=${APP_VERSION} \
                          -Dsonar.sources=. \
                          -Dsonar.python.coverage.reportPaths=reports/coverage.xml \
                          -Dsonar.python.xunit.reportPath=reports/junit.xml \
                          -Dsonar.host.url=${SONAR_HOST} \
                          -Dsonar.token=${SONAR_TOKEN}
                    """
                }
            }
        }

        // -------------------------------------------------------
        // Stage 6: Quality Gate
        // -------------------------------------------------------
        stage('Quality Gate') {
            steps {
                echo "==> Checking SonarQube Quality Gate..."
                timeout(time: 5, unit: 'MINUTES') {
                    waitForQualityGate abortPipeline: true
                }
            }
        }

        // -------------------------------------------------------
        // Stage 7: Build Docker Image
        // -------------------------------------------------------
        stage('Build Docker Image') {
            steps {
                echo "==> Building Docker image..."
                sh """
                    docker build \
                        -t ${DOCKER_IMAGE}:${APP_VERSION} \
                        -t ${DOCKER_IMAGE}:latest \
                        --build-arg APP_VERSION=${APP_VERSION} \
                        .
                """
                sh "docker images | grep ${APP_NAME}"
            }
        }

        // -------------------------------------------------------
        // Stage 8: Push to Docker Hub
        // -------------------------------------------------------
        stage('Push to Docker Hub') {
            steps {
                echo "==> Pushing Docker image to Docker Hub..."
                withCredentials([usernamePassword(
                    credentialsId: 'dockerhub-credentials',
                    usernameVariable: 'DOCKER_USER',
                    passwordVariable: 'DOCKER_PASS'
                )]) {
                    sh """
                        echo ${DOCKER_PASS} | docker login -u ${DOCKER_USER} --password-stdin
                        docker push ${DOCKER_IMAGE}:${APP_VERSION}
                        docker push ${DOCKER_IMAGE}:latest
                        docker logout
                    """
                }
            }
        }

        // -------------------------------------------------------
        // Stage 9: Deploy to Kubernetes
        // -------------------------------------------------------
        stage('Deploy to Kubernetes') {
            parallel {

                stage('Rolling Update') {
                    steps {
                        echo "==> Applying Rolling Update deployment..."
                        sh """
                            kubectl apply -f k8s/rolling-deployment.yaml
                            kubectl rollout status deployment/aceest-rolling -n aceest
                        """
                    }
                }

                stage('Blue-Green Deploy') {
                    steps {
                        echo "==> Applying Blue-Green deployment..."
                        sh """
                            kubectl apply -f k8s/blue-green-deployment.yaml
                            kubectl apply -f k8s/blue-green-service.yaml
                        """
                    }
                }

                stage('Canary Deploy') {
                    steps {
                        echo "==> Applying Canary deployment..."
                        sh """
                            kubectl apply -f k8s/canary-deployment.yaml
                        """
                    }
                }

            }
        }

        // -------------------------------------------------------
        // Stage 10: Smoke Test (Post-Deploy)
        // -------------------------------------------------------
        stage('Smoke Test') {
            steps {
                echo "==> Running post-deployment smoke test..."
                sh '''
                    sleep 10
                    kubectl get pods -n aceest
                    . venv/bin/activate
                    pytest tests/test_app.py::TestHealthAndVersion -v
                '''
            }
        }

    }

    // -------------------------------------------------------
    // Post Actions
    // -------------------------------------------------------
    post {
        success {
            echo "✅ Pipeline SUCCESS — ACEest v${APP_VERSION} deployed!"
        }
        failure {
            echo "❌ Pipeline FAILED — Rolling back to previous version..."
            sh '''
                kubectl rollout undo deployment/aceest-rolling -n aceest || true
            '''
        }
        always {
            echo "==> Cleaning up workspace..."
            sh 'docker image prune -f || true'
            cleanWs()
        }
    }
}
