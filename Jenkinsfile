pipeline {
  agent any
  triggers { pollSCM('* * * * *') }

  stages {
    stage('Unit tests') {
      steps {
        dir('pulse-checker') {
          sh '''
            python3 -m venv .venv
            . .venv/bin/activate
            pip install -r requirements-dev.txt
            pytest -v
          '''
        }
      }
    }
    stage('Build images') {
      steps {
        sh 'docker build -t pulse-demo-service:ci ./demo-service'
        sh 'docker build -t pulse-checker:ci ./pulse-checker'
      }
    }
    stage('Smoke test') {
      steps {
        sh '''
          docker rm -f pulse-ci-demo || true
          docker run -d --name pulse-ci-demo pulse-demo-service:ci
          sleep 5
          docker exec pulse-ci-demo python -c "import urllib.request, sys; r = urllib.request.urlopen('http://localhost:8000/health'); sys.exit(0 if r.status == 200 else 1)"
        '''
      }
    }
  }

  post {
    always { sh 'docker rm -f pulse-ci-demo || true' }
  }
}
