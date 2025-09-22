# User Service

## 📌 Overview

The User Service is the central identity and profile management system for the banking platform. It manages all aspects of customer onboarding, authentication, personal data, verification, and preferences. This service acts as the source of truth for user-related data and provides secure access to other services.

- **Language:** Python 3.11+
- **Dependency Management:** [PDM](https://pdm.fming.dev/)
- **Web Framework:** [FastAPI](https://fastapi.tiangolo.com/)
- **Inter-service Communication:** gRPC, RabbitMQ (async messaging)
- **Data Validation:** Pydantic
- **Database:** PostgreSQL 15+ (Dockerized)
- **Cache/Session/Rate Limiting:** Redis (Dockerized)
- **Message Broker:** RabbitMQ (Dockerized)
- **Object Storage:** AWS S3 / Cloudinary
- **Testing:** pytest, pytest-asyncio
- **Logging:** structlog
- **Metrics:** prometheus-client
- **Error Tracking:** Sentry

## 🐳 Dockerized Services

The following core services run in Docker containers for local development and deployment:

- PostgreSQL
- Redis
- RabbitMQ

See the `docker-compose.yml` file for configuration and startup instructions.

## 🛠️ High-level Documentation

- Handles central identity and profile management business logic
- Interacts with API Gateway, KYC service
- Integrates with 3rd party APIs if any

## 📂 Code Structure

Example:

```
/app
	/api         # FastAPI routers
	/models      # Pydantic models & ORM models
	/services    # Business logic
	/schemas     # Data validation schemas
	/grpc        # gRPC service definitions & stubs
	/core        # Config, logging, utils
/tests         # pytest & pytest-asyncio tests
/proto         # gRPC proto files
/docs          # OpenAPI, architecture docs
```

## 🧩 Design Documentation

- Patterns: Dependency Injection, Repository, Service Layer
- Key abstractions/interfaces: UserRepository, AuthService, StorageService
- Error handling: FastAPI exception handlers, Sentry integration
- Logging: structlog, Prometheus metrics

## 🔌 API Specification

- gRPC proto files → `/proto`
- REST API docs (OpenAPI) → `/docs/openapi.yaml`

## 📦 Third-Party Integrations

- Payment Provider: Paystack / Flutterwave
- Bill Aggregator: XYZ
- Notification: Twilio / SendGrid
- Storage: AWS S3 / Cloudinary

## 🧪 Testing

- Unit tests: `pytest`
- Async tests: `pytest-asyncio`
- Coverage: `pytest --cov`
- CI/CD pipeline: GitHub Actions / GitLab CI

## ▶️ Running Locally

```bash
# 1. Install PDM (if not already installed)
pip install --user pdm

# 2. Install dependencies
pdm install

# 3. Set environment variables (see .env.example)

# 4. Run database migrations (if using Alembic or similar)
# alembic upgrade head

# 5. Start the FastAPI server
pdm run uvicorn app.main:app --reload

# 6. (Optional) Run gRPC server
# pdm run python app/grpc/server.py
```

## 🧪 Running Tests

```bash
pdm run pytest
```

## 📊 Observability & Monitoring

- **Logging:** structlog
- **Metrics:** prometheus-client (exposes /metrics endpoint)
- **Error Tracking:** Sentry (configure DSN in environment)

---

For more details, see the `/docs` folder and code comments.
