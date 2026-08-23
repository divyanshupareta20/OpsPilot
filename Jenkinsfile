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

        stage('Docker Deploy') {
            steps {
                sh '''
                    docker rm -f opspilot || true

                    docker network inspect opspilot-network >/dev/null 2>&1 || \
                    docker network create opspilot-network

                    docker network connect opspilot-network mysql 2>/dev/null || true

                    docker run -d \
                        --name opspilot \
                        --network opspilot-network \
                        -p 8000:8000 \
                        -e DB_HOST=mysql \
                        -e DB_PORT=3306 \
                        -e DB_USER=root \
                        -e DB_PASSWORD=opspilot123 \
                        -e DB_NAME=opspilot \
                        opspilot:latest
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    sleep 10
                    curl -f http://localhost:8000/health
                '''
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