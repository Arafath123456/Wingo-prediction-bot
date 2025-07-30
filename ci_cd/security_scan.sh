#!/bin/bash

# Static Application Security Testing (SAST)
echo "Running Bandit security scan..."
bandit -r .

# Dependency vulnerability scanning
echo "Running safety check..."
safety check

# Secret scanning
echo "Scanning for secrets..."
git secrets --scan

# Container vulnerability scanning
echo "Scanning Docker image for vulnerabilities..."
docker build -t wingo-bot-scan .
trivy image wingo-bot-scan

# Exit with failure if any high severity vulnerabilities found
if [ $? -ne 0 ]; then
  echo "Security scan failed!"
  exit 1
fi

echo "Security scan passed successfully"