pipeline {
    environment {
        AWS_REGION = 'eu-central-1'
        ECR_REGISTRY = "<your-account-id>.dkr.ecr.${AWS_REGION}.amazonaws.com"
        ECR_REPO = "Crypto-Price"
        IMAGE_TAG = "${env.GIT_COMMIT}"
        RELEASE_NAME = "Crypto"
        CHART_PATH = "./k8s"
        NAMESPACE = "test-crypto-price"
    }
    agent none
    stages {
        stage('Linting Helm Chart') {
            agent { label 'helm' }

            steps {
                container('helm') {
                    echo "Linting Helm Chart..."
                    sh "helm lint ./k8s"
                }
            }
        }
        stage('Build & Push Image') {
            agent { label 'docker' } // Requires agent with both docker and aws cli
            steps {
                echo "Logging into ECR..."
                sh ''' // This is assuming the agent has an IAM role allowing access to ecr
                    aws ecr get-login-password --region $AWS_REGION \
                        | docker login --username AWS --password-stdin $ECR_REGISTRY
                '''

                echo "Building Docker image..."
                sh "docker build -t $ECR_REPO:$IMAGE_TAG ."

                echo "Tagging and pushing..."
                sh '''
                    docker tag $ECR_REPO:$IMAGE_TAG $ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG
                    docker push $ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG
                '''
            }
        }
        stage('Helm Deploy') {
            agent { label 'helm' }

            steps {
                container('helm') {
                    // Agent needs to have serviceaccount with correct permissions
                    sh '''
                        echo "Deploying with Helm..."
                        helm upgrade --install $RELEASE_NAME $CHART_PATH \
                          --namespace $NAMESPACE \
                          --set image.repository=$ECR_REGISTRY/$ECR_REPO \
                          --set image.tag=$IMAGE_TAG
                    '''
                }
            }
        }
        stage('Reload Prometheus Config') {
            agent { label 'curl' }

            steps {
                container('curl') {
                    echo "Reloading prometheus config..."
                    sh "curl -X POST crypto-kube-prometheus-sta-prometheus.default.svc.cluster.local:9090/-/reload"
                }
            }
        }
    }
    post {
        always {
            // Requires credential slack-webhook in jenkins
            withCredentials([string(credentialsId: 'slack-webhook', variable: 'SLACK_WEBHOOK')]) {
                sh '''
                    curl -X POST -H 'Content-type: application/json' \
                    --data '{"text":"Build finished for job: '${JOB_NAME}' (#'${BUILD_NUMBER}')"}' $SLACK_WEBHOOK
                '''
            }
        }
    }
}