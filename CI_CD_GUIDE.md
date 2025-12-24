# 🚀 CI/CD Implementation Guide

This guide explains how to implement Continuous Integration and Continuous Deployment (CI/CD) for the Smart Negotiator project using **GitHub Actions**.

## 1. Current Setup (CI)

I have added a workflow file at `.github/workflows/ci.yml`. This pipeline automatically runs whenever you push code to the `main` branch or open a Pull Request.

### What it does:
1.  **Environment Setup**: Spins up an Ubuntu runner with Python 3.11.
2.  **Service Integration**: Starts a temporary MySQL service container for testing database interactions.
3.  **Dependency Installation**: Installs all packages from `requirements.txt`.
4.  **Code Quality Check**: Runs `flake8` to check for syntax errors and coding style issues.
5.  **Testing**: Runs `pytest` to execute unit tests.
    *   *Note: I added a placeholder test step. You should create a `tests/` folder and add real unit tests.*
6.  **Build Verification**: Builds the Docker image to ensure the `Dockerfile` is valid and the application can be containerized successfully.

## 2. How to Enable CD (Continuous Deployment)

To automatically deploy your application when changes are pushed to `main`, you can extend the pipeline.

### Option A: Push to Docker Hub (Container Registry)

1.  **Create a Docker Hub Account**: [https://hub.docker.com/](https://hub.docker.com/)
2.  **Add Secrets to GitHub**:
    *   Go to your Repo Settings -> Secrets and variables -> Actions -> New repository secret.
    *   Add `DOCKERHUB_USERNAME` and `DOCKERHUB_TOKEN`.
3.  **Update `ci.yml`**: Add a "Login and Push" step.

```yaml
    - name: Login to Docker Hub
      uses: docker/login-action@v2
      with:
        username: ${{ secrets.DOCKERHUB_USERNAME }}
        password: ${{ secrets.DOCKERHUB_TOKEN }}

    - name: Build and push
      uses: docker/build-push-action@v4
      with:
        context: .
        push: true
        tags: ${{ secrets.DOCKERHUB_USERNAME }}/smartnegotiator:latest
```

### Option B: Deploy to a VPS (e.g., DigitalOcean, AWS EC2)

1.  **Prerequisites**: A server with Docker and Docker Compose installed.
2.  **Add Secrets**: `HOST`, `USERNAME`, `SSH_KEY`.
3.  **Add Deployment Step**:

```yaml
    - name: Deploy to Server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /path/to/smartnegotiator
          git pull origin main
          docker-compose down
          docker-compose up -d --build
```

## 3. Recommended Next Steps

1.  **Write Tests**: Create a `tests/` directory.
    *   Add `test_rag.py` to test the embedding logic.
    *   Add `test_negotiation.py` to test the pricing logic.
2.  **Protect Main Branch**: Go to GitHub Repo Settings -> Branches -> Add rule.
    *   Require status checks to pass before merging.
    *   Select "build-and-test" as the required check.

This ensures that no broken code is ever merged into your production branch.
