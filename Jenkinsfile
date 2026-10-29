
pipeline {
    agent any

    stages {
        stage('Checkout') {
            steps {
                echo 'Getting QR Certificate Verification System source code'
                checkout scm
            }
        }

        stage('Python Syntax Check') {
            steps {
                echo 'Checking Python syntax'
                bat 'python --version'
                bat 'python -m py_compile app.py certificate_pdf.py certificate_routes.py database.py models.py utils.py'
            }
        }

        stage('Docker Build') {
            steps {
                echo 'Building Docker image'
                bat 'docker --version'
                bat 'docker build -t qr-certificate-app:%BUILD_NUMBER% .'
            }
        }
    }

    post {
        success {
            echo 'Pipeline completed successfully!'
        }

        failure {
            echo 'Pipeline failed. Check the stage console output.'
        }
    }
}
