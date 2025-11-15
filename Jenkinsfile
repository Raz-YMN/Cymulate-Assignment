pipeline {
    stages {
        agent { label 'kubeval' }

        stage('Lint Kubernetes YAMLs') {
            agent { label 'kubeval' }

            steps {
                sh '''
                    echo "Linting Kubernetes manifests..."
                    kubeval --strict --ignore-missing-schemas --directories ./k8s
                '''
            }
        }
    }
}