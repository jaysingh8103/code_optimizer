pipeline {
    agent any

    environment {
        PYTHON_VERSION = '3.10'
        VENV_DIR = 'venv'
    }

    stages {
        stage('Checkout') {
            steps {
                git branch: 'main', url: 'https://github.com/jaysingh8103/code_optimizer.git'
            }
        }

        stage('Setup Environment') {
            steps {
                sh """
                python3 -m venv ${VENV_DIR}
                source ${VENV_DIR}/bin/activate
                pip install --upgrade pip
                pip install -r requirements.txt || echo "No requirements.txt found"
                """
            }
        }

        stage('Error Detection') {
            steps {
                sh """
                source ${VENV_DIR}/bin/activate
                python code_optimizer.py .
                """
            }
        }

        stage('Code Formatting') {
            steps {
                sh """
                source ${VENV_DIR}/bin/activate
                black . || echo "Black formatting failed"
                autopep8 --in-place --recursive . || echo "autopep8 formatting failed"
                isort . || echo "isort formatting failed"
                """
            }
        }

        stage('Optimization') {
            steps {
                sh """
                source ${VENV_DIR}/bin/activate
                python code_optimizer.py .
                """
            }
        }

        stage('Show Changes') {
            steps {
                script {
                    def changes = sh(script: 'git status --porcelain', returnStdout: true).trim()
                    if (changes) {
                        echo "The following changes were made:"
                        sh 'git diff'
                    } else {
                        echo "No changes were made."
                    }
                }
            }
        }

        stage('Approval to Commit') {
            when {
                expression {
                    sh(script: 'git status --porcelain', returnStdout: true).trim() != ''
                }
            }
            steps {
                script {
                    input message: 'Do you want to commit and push the changes?', ok: 'Yes'
                }
            }
        }

        stage('Commit and Push Changes') {
            when {
                expression {
                    sh(script: 'git status --porcelain', returnStdout: true).trim() != ''
                }
            }
            steps {
                sh """
                git config user.email "jaypals840@gmail.com"
                git config user.name "jaysingh8103"
                git add .
                git commit -m "Automated code optimization by Jenkins pipeline"
                git push origin main
                """
            }
        }

        stage('Post-Processing') {
            steps {
                echo "Code optimization completed successfully!"
            }
        }
    }

    post {
        success {
            echo '✅ Pipeline completed successfully!'
        }
        failure {
            echo '❌ Pipeline failed! Please check the logs.'
        }
        always {
            sh """
            if [ -d ${VENV_DIR} ]; then
                echo "Deactivating virtual environment"
                deactivate || true
            fi
            """
        }
    }
}
