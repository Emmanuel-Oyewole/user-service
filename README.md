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
- **Testing:** pytest-asyncio
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
user-service/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── .gitignore
├── .pre-commit-config.yaml
├── README.md
├── LICENSE
├── Dockerfile
├── docker-compose.yml
├── docker-compose.dev.yml
├── pyproject.toml
├── requirements.txt
├── requirements-dev.txt
├── alembic.ini
├── .env.example
├── Makefile
├── scripts/
│   ├── start.sh
│   ├── dev.sh
│   ├── test.sh
│   └── migrate.sh
├── proto/
│   ├── server/               # Proto files we serve (User Service API)
│   │   ├── user.proto
│   │   ├── auth.proto
│   │   └── profile.proto
│   ├── clients/              # Proto files for services we consume
│   │   ├── kyc.proto
│   │   ├── notification.proto
│   │   └── audit.proto
│   └── generated/
│       ├── __init__.py
│       ├── server/           # Generated server code
│       │   ├── __init__.py
│       │   ├── user_pb2.py
│       │   ├── user_pb2_grpc.py
│       │   ├── auth_pb2.py
│       │   ├── auth_pb2_grpc.py
│       │   ├── profile_pb2.py
│       │   └── profile_pb2_grpc.py
│       └── clients/          # Generated client code
│           ├── __init__.py
│           ├── kyc_pb2.py
│           ├── kyc_pb2_grpc.py
│           ├── notification_pb2.py
│           ├── notification_pb2_grpc.py
│           ├── audit_pb2.py
│           └── audit_pb2_grpc.py
├── migrations/
│   ├── versions/
│   └── env.py
├── src/
│   ├── __init__.py
│   ├── main.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── database.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user.py
│   │   ├── mfa.py
│   │   ├── identity.py
│   │   ├── device.py
│   │   └── notification.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   ├── user.py
│   │   ├── auth.py
│   │   ├── mfa.py
│   │   ├── profile.py
│   │   ├── settings.py
│   │   └── response.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── auth.py
│   │   ├── mfa.py
│   │   ├── profile.py
│   │   ├── settings.py
│   │   ├── devices.py
│   │   ├── data.py
│   │   ├── admin.py
│   │   └── health.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py
│   │   ├── user_service.py
│   │   ├── mfa_service.py
│   │   ├── profile_service.py
│   │   ├── notification_service.py
│   │   ├── kyc_service.py
│   │   ├── email_service.py
│   │   ├── sms_service.py
│   │   └── storage_service.py
│   ├── repositories/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── user_repository.py
│   │   ├── mfa_repository.py
│   │   ├── identity_repository.py
│   │   ├── device_repository.py
│   │   └── audit_repository.py
│   ├── grpc_services/            # gRPC Server implementations
│   │   ├── __init__.py
│   │   ├── user_grpc_service.py
│   │   ├── auth_grpc_service.py
│   │   ├── profile_grpc_service.py
│   │   └── grpc_server.py
│   ├── grpc_clients/             # gRPC Client implementations
│   │   ├── __init__.py
│   │   ├── base_client.py
│   │   ├── kyc_client.py
│   │   ├── notification_client.py
│   │   └── audit_client.py
│   ├── messaging/
│   │   ├── __init__.py
│   │   ├── producer.py
│   │   ├── consumer.py
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── user_events.py
│   │   │   └── auth_events.py
│   │   └── events/
│   │       ├── __init__.py
│   │       ├── user_events.py
│   │       └── auth_events.py
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth_middleware.py
│   │   ├── rate_limit_middleware.py
│   │   ├── logging_middleware.py
│   │   └── cors_middleware.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── security.py
│   │   ├── validators.py
│   │   ├── exceptions.py
│   │   ├── constants.py
│   │   ├── helpers.py
│   │   └── cache.py
│   └── core/
│       ├── __init__.py
│       ├── deps.py
│       ├── security.py
│       └── exceptions.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── fixtures/
│   │   ├── __init__.py
│   │   ├── user_fixtures.py
│   │   └── auth_fixtures.py
│   ├── unit/
│   │   ├── __init__.py
│   │   ├── services/
│   │   ├── repositories/
│   │   ├── utils/
│   │   └── models/
│   ├── integration/
│   │   ├── __init__.py
│   │   ├── routes/
│   │   ├── grpc/
│   │   └── messaging/
│   └── e2e/
│       ├── __init__.py
│       └── test_user_flow.py
├── docs/
│   ├── api/
│   │   ├── auth.md
│   │   ├── profile.md
│   │   └── mfa.md
│   ├── deployment/
│   │   ├── docker.md
│   │   └── kubernetes.md
│   └── development/
│       ├── setup.md
│       └── contributing.md
└── monitoring/
    ├── prometheus/
    │   └── rules.yml
    ├── grafana/
    │   └── dashboards/
    └── logs/
        └── logstash.conf
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

# 3. Set environment variable
cp .env.example .env

# start the required docker services
docker-compose -f docker-compose.dev.yml up -d

# 4. Run database migrations
alembic upgrade head

# 5. Start the FastAPI server
pdm run dev

# 6. Run gRPC server in a separate terminal
pdm run grpc
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
