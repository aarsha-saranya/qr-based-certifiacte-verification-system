
pipeline {
    agent any

    options {
        skipDefaultCheckout(true)
    }

    environment {
        PYTHON = 'C:\\Users\\shaik\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
        DOCKER_EXE = 'C:\\Users\\shaik\\AppData\\Local\\Programs\\DockerDesktop\\resources\\bin\\docker.exe'
        DOCKER_IMAGE = 'qr-certificate-app'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out source code from GitHub'
                checkout scm
            }
        }

        stage('Check Python') {
            steps {
                bat '"%PYTHON%" --version'
            }
        }

        stage('Python Syntax Check') {
            steps {
                bat '"%PYTHON%" -m py_compile app.py certificate_pdf.py certificate_routes.py database.py models.py utils.py'
            }
        }

        stage('Check Docker') {
            steps {
                bat '''
                    if not exist "%DOCKER_EXE%" (
                        echo ERROR: Docker executable not found.
                        exit /b 1
                    )
                    "%DOCKER_EXE%" --version
                    "%DOCKER_EXE%" info
                '''
            }
        }

        stage('Build Docker Image') {
            steps {
                bat '"%DOCKER_EXE%" build -t %DOCKER_IMAGE%:%BUILD_NUMBER% .'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Python checks and Docker image build passed.'
        }
        failure {
            echo 'BUILD FAILED: Check the first failing stage in Console Output.'
        }
        always {
            echo 'Pipeline execution completed.'
        }
    }
}
