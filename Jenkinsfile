```groovy
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

        stage('Load Image into Kind') {
            steps {
                sh '''
                    kind load docker-image opspilot:latest --name opspilot-cluster
                '''
            }
        }

        stage('Kubernetes Deploy') {
            steps {
                sh '''
                    kubectl apply -f opspilot-deployment.yaml
                    kubectl apply -f opspilot-service.yaml

                    kubectl rollout restart deployment/opspilot -n opspilot

                    kubectl rollout status deployment/opspilot -n opspilot --timeout=120s
                '''
            }
        }

        stage('Health Check') {
            steps {
                sh '''
                    sleep 5
                    kubectl run curl-test \
                        -n opspilot \
                        --rm \
                        -i \
                        --restart=Never \
                        --image=curlimages/curl \
                        -- \
                        curl -f http://opspilot-service:8000/health
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
```
