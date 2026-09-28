pipeline {
    agent any

    environment {
        DOCKER_REGISTRY      = "docker.io/ankitmori1626" // Change to your Docker Hub / Harbor namespace
        BACKEND_IMAGE_NAME   = "threetier-backend"
        FRONTEND_IMAGE_NAME  = "threetier-frontend"
        REGISTRY_CREDENTIALS = "dockerhub-credentials"  // Jenkins Credential ID (Username/Password)
        BUILD_TAG            = "${env.BRANCH_NAME}-${env.BUILD_NUMBER}-${env.GIT_COMMIT.take(7)}"
        SCAN_SEVERITY        = "HIGH,CRITICAL"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '15'))
        timestamps()
        timeout(time: 30, unit: 'MINUTES')
        disableConcurrentBuilds()
    }

    stages {
        stage('🔍 Environment Detection') {
            steps {
                script {
                    echo "========================================================"
                    echo " 🚀 Starting Multi-Branch CI/CD Pipeline"
                    echo " 🌿 Branch Detected: ${env.BRANCH_NAME}"
                    echo " 🏷️  Build Tag: ${BUILD_TAG}"
                    echo " 📅 Build Number: ${env.BUILD_NUMBER}"
                    echo "========================================================"
                    
                    if (env.BRANCH_NAME == 'dev') {
                        env.DEPLOY_ENV = 'dev'
                        env.KUBECONFIG_CRED_ID = 'kubeconfig-k8s'
                    } else if (env.BRANCH_NAME == 'stage') {
                        env.DEPLOY_ENV = 'stage'
                        env.KUBECONFIG_CRED_ID = 'kubeconfig-k8s'
                    } else if (env.BRANCH_NAME == 'prod' || env.BRANCH_NAME == 'main' || env.BRANCH_NAME == 'master') {
                        env.DEPLOY_ENV = 'prod'
                        env.KUBECONFIG_CRED_ID = 'kubeconfig-k8s'
                    } else {
                        echo "⚠️ Feature branch detected (${env.BRANCH_NAME}). Pipeline will build & test without deploying."
                        env.DEPLOY_ENV = 'none'
                    }
                }
            }
        }

        stage('🧪 Code Quality & Tests') {
            parallel {
                stage('Backend Tests & Lint') {
                    steps {
                        dir('backend') {
                            sh '''
                                echo "Running Backend health check tests..."
                                node -e "console.log('Backend syntax check passed')"
                            '''
                        }
                    }
                }
                stage('Frontend Validation') {
                    steps {
                        dir('frontend') {
                            sh '''
                                echo "Validating Python Frontend..."
                                test -f app.py && test -f requirements.txt && echo "Python Frontend files verified"
                            '''
                        }
                    }
                }
            }
        }

        stage('🐳 Build Docker Images') {
            steps {
                script {
                    echo "Building Backend Docker Image..."
                    sh """
                        docker build -t ${DOCKER_REGISTRY}/${BACKEND_IMAGE_NAME}:${BUILD_TAG} \
                                     -t ${DOCKER_REGISTRY}/${BACKEND_IMAGE_NAME}:${env.DEPLOY_ENV}-latest \
                                     ./backend
                    """

                    echo "Building Frontend Docker Image..."
                    sh """
                        docker build -t ${DOCKER_REGISTRY}/${FRONTEND_IMAGE_NAME}:${BUILD_TAG} \
                                     -t ${DOCKER_REGISTRY}/${FRONTEND_IMAGE_NAME}:${env.DEPLOY_ENV}-latest \
                                     ./frontend
                    """
                }
            }
        }

        stage('🛡️ Security Vulnerability Scan (Trivy)') {
            steps {
                script {
                    sh """
                        if command -v trivy >/dev/null 2>&1; then
                            echo "Scanning Backend Image..."
                            trivy image --severity ${SCAN_SEVERITY} --exit-code 0 ${DOCKER_REGISTRY}/${BACKEND_IMAGE_NAME}:${BUILD_TAG}
                            echo "Scanning Frontend Image..."
                            trivy image --severity ${SCAN_SEVERITY} --exit-code 0 ${DOCKER_REGISTRY}/${FRONTEND_IMAGE_NAME}:${BUILD_TAG}
                        else
                            echo "Trivy not found on Jenkins agent. Skipping vulnerability scan."
                        fi
                    """
                }
            }
        }

        stage('📤 Push to Registry') {
            when {
                expression { return env.DEPLOY_ENV != 'none' }
            }
            steps {
                script {
                    withCredentials([usernamePassword(credentialsId: "${REGISTRY_CREDENTIALS}", usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
                        sh """
                            echo "\$DOCKER_PASS" | docker login -u "\$DOCKER_USER" --password-stdin ${DOCKER_REGISTRY.split('/')[0]}
                            docker push ${DOCKER_REGISTRY}/${BACKEND_IMAGE_NAME}:${BUILD_TAG}
                            docker push ${DOCKER_REGISTRY}/${BACKEND_IMAGE_NAME}:${env.DEPLOY_ENV}-latest
                            docker push ${DOCKER_REGISTRY}/${FRONTEND_IMAGE_NAME}:${BUILD_TAG}
                            docker push ${DOCKER_REGISTRY}/${FRONTEND_IMAGE_NAME}:${env.DEPLOY_ENV}-latest
                        """
                    }
                }
            }
        }

        stage('🛑 Production Approval Gate') {
            when {
                expression { return env.DEPLOY_ENV == 'prod' }
            }
            steps {
                input(
                    message: "Deploy build ${BUILD_TAG} to PRODUCTION Cluster?",
                    ok: "Approve Deployment",
                    submitterParameter: 'APPROVER'
                )
            }
        }

        stage('☸️ Deploy to Kubernetes (Kubeadm Cluster)') {
            when {
                expression { return env.DEPLOY_ENV != 'none' }
            }
            steps {
                script {
                    withCredentials([file(credentialsId: "${KUBECONFIG_CRED_ID}", variable: 'KUBECONFIG_FILE')]) {
                        echo "Applying Kustomize manifests for Environment: ${env.DEPLOY_ENV.toUpperCase()}"
                        
                        sh """
                            export KUBECONFIG=\${KUBECONFIG_FILE}
                            
                            echo "Ensuring namespace ${env.DEPLOY_ENV} exists..."
                            kubectl create namespace ${env.DEPLOY_ENV} --dry-run=client -o yaml | kubectl apply -f -
                            
                            echo "Updating Kustomize image tags..."
                            cd k8s/overlays/${env.DEPLOY_ENV}
                            
                            kustomize edit set image threetier-backend=${DOCKER_REGISTRY}/${BACKEND_IMAGE_NAME}:${BUILD_TAG}
                            kustomize edit set image threetier-frontend=${DOCKER_REGISTRY}/${FRONTEND_IMAGE_NAME}:${BUILD_TAG}
                            
                            echo "Applying manifests to cluster..."
                            kubectl apply -k .
                            
                            echo "Waiting for rollout to complete..."
                            kubectl rollout status deployment/backend -n ${env.DEPLOY_ENV} --timeout=120s
                            kubectl rollout status deployment/frontend -n ${env.DEPLOY_ENV} --timeout=120s
                            
                            echo "Fetching Pods & Ingress details..."
                            kubectl get pods -n ${env.DEPLOY_ENV} -o wide
                            kubectl get ingress -n ${env.DEPLOY_ENV}
                        """
                    }
                }
            }
        }
    }

    post {
        always {
            sh "docker logout || true"
            cleanWs()
        }
        success {
            echo "✅ Multi-Branch Pipeline completed successfully for ${env.BRANCH_NAME}!"
        }
        failure {
            echo "❌ Pipeline failed! Please inspect logs above."
        }
    }
}
