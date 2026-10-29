
pipeline {
    agent any

    environment {
        PYTHON = 'C:\\Users\\shaik\\AppData\\Local\\Programs\\Python\\Python313\\python.exe'
        DOCKER_IMAGE = 'qr-certificate-app'
    }

    stages {
        stage('Checkout') {
            steps {
                echo 'Checking out QR Certificate Verification System from GitHub'
                checkout scm
            }
        }

        stage('Check Python Installation') {
            steps {
                echo 'Checking Python installation'
                bat '"%PYTHON%" --version'
            }
        }

        stage('Python Syntax Check') {
            steps {
                echo 'Checking Python syntax'
                bat '"%PYTHON%" -m py_compile app.py certificate_pdf.py certificate_routes.py database.py models.py utils.py'
            }
        }

        stage('Docker Version Check') {
            steps {
                echo 'Checking Docker installation'
                bat 'docker --version'
            }
        }

        stage('Build Docker Image') {
            steps {
                echo 'Building Docker image'
                bat 'docker build -t %DOCKER_IMAGE%:%BUILD_NUMBER% .'
            }
        }
    }

    post {
        success {
            echo 'SUCCESS: Python syntax check and Docker image build completed.'
        }

        failure {
            echo 'FAILURE: Check Console Output for the stage that failed.'
        }

        always {
            echo 'Jenkins pipeline execution finished.'
        }
    }
}
