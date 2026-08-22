pipeline {

    agent any

    stages {

        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Docker Build') {
            steps {
                sh 'docker build -t opspilot:latest .'
            }
        }
    }

    post {

        success {
            echo 'OpsPilot CI/CD pipeline completed successfully!'
        }

        failure {
            echo 'OpsPilot CI/CD pipeline failed!'
        }
    }
}