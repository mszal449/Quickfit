<div align="center">

<img src="frontend/src/assets/logo.svg" alt="QuickFit logo" width="96" height="96" />

# QuickFit

The training tracker that replaces my Google Sheets.

<!-- ─────────────  TECH STACK BRICKS  ───────────── -->

**Backend**

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)
![Pydantic](https://img.shields.io/badge/Pydantic-E92063?style=for-the-badge&logo=pydantic&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-D71F00?style=for-the-badge&logo=sqlalchemy&logoColor=white)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-4169E1?style=for-the-badge&logo=postgresql&logoColor=white)
![Uvicorn](https://img.shields.io/badge/Uvicorn-499848?style=for-the-badge&logo=gunicorn&logoColor=white)

**Infrastructure**

![Kubernetes](https://img.shields.io/badge/Kubernetes-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)
![Kustomize](https://img.shields.io/badge/Kustomize-326CE5?style=for-the-badge&logo=kubernetes&logoColor=white)
![NGINX](https://img.shields.io/badge/NGINX_Ingress-009639?style=for-the-badge&logo=nginx&logoColor=white)

**Frontend**

![React](https://img.shields.io/badge/React-20232A?style=for-the-badge&logo=react&logoColor=61DAFB)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6?style=for-the-badge&logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-646CFF?style=for-the-badge&logo=vite&logoColor=white)
![Tailwind CSS](https://img.shields.io/badge/Tailwind_CSS-06B6D4?style=for-the-badge&logo=tailwindcss&logoColor=white)
![React Query](https://img.shields.io/badge/React_Query-FF4154?style=for-the-badge&logo=reactquery&logoColor=white)
![React Router](https://img.shields.io/badge/React_Router-CA4245?style=for-the-badge&logo=reactrouter&logoColor=white)

</div>

---

## Overview

QuickFit is a self-hosted workout tracker: plan your training, log sessions from your phone at the gym, and share plans with other people. I built it because I was sick of the Google Sheets mess I'd made for myself.

<div align="center">

| Dashboard | Logging a session | Session complete |
|:---:|:---:|:---:|
| <img src="public/IMG_0057.PNG" alt="Dashboard" width="240" /> | <img src="public/IMG_0058.PNG" alt="Logging a session" width="240" /> | <img src="public/IMG_0062.PNG" alt="Session complete" width="240" /> |

**Plan builder (desktop)**

<img src="public/IMG_0063.PNG" alt="Plan builder" width="820" />

</div>

## Features

- Exercise library with per-exercise history, so you can see how a lift has progressed over time
- Training plan builder (sessions, sets, reps, rest periods, ...)
- Workout logging, including in-progress sessions you can pick back up and finish later
- Share a plan with another user; they log their own progress against it
- Set a default plan per user, whether it's your own or one shared with you
- Google Health integration - connect your account via OAuth, pull workout data in and push completed QuickFit sessions back out

## Tech & why

Built as much to learn as to ship: not just a tracker, but a "properly" built app end to end - real auth, a real deployment story, a real CI/CD pipeline.

| | |
|---|---|
| **Kubernetes** | Same Kustomize manifests deploy to `k3s` on my home server and `minikube` locally - no environment drift |
| **Cloudflare Tunnel** | The home server is exposed to the internet without opening a single port or renting a VPS |
| **Docker + GitHub Actions** | Every push builds, lints and tests; every tag pushes images to `ghcr.io` and rolls out to prod |
| **FastAPI** | Async Python API with dependency injection, JWT auth and a resource-first layout |
| **PostgreSQL + SQLAlchemy + Alembic** | Async SQL stack with versioned migrations, run as a K8s `Job` on deploy |
| **OpenAPI + Orval** | Frontend API types and hooks are generated from the backend spec - the two can't drift |
| **React + TypeScript + Tailwind** | Boring-in-a-good-way frontend, responsive for phone (gym) and desktop (planning) |
| **TanStack Query** | Server state, caching and auth handling without the boilerplate |
| **Taskfile** | One entry point for every dev/lint/test/deploy command (`task dev`, `task lint`, `task k8s-local`) |

## Implementation notes

<details>
<summary><b>Kubernetes &amp; CI/CD</b></summary>

- **Two clusters, one set of manifests** - `k3s` on my home server for prod, `minikube` locally, both built from the same `k8s/base` and diverging only through Kustomize overlays (ingress class, image tag, replica count, resources).
- **Self-hosted, publicly reachable** - a Cloudflare Tunnel fronts the cluster's ingress, so the app is available on a real domain with TLS while the home network stays closed to inbound traffic.
- **Postgres in-cluster** - a `StatefulSet` + PVC (`local-path`) instead of a managed database, specifically to get hands-on with StatefulSets, PVCs, and a headless service — the kind of thing a managed DB would have hidden from me.
- **CI/CD-driven rollout** - GitHub Actions builds and pushes images on every push, then on a tag push: applies k8s secrets from GitHub Secrets, runs Alembic migrations as a one-off `Job`, patches the image tag with `kustomize edit set image`, and waits on the rollout.
- **Secrets** - plain k8s `Secret`s created from GitHub Secrets in the pipeline (or from a local untracked `.env` for `minikube`) — simplest option that's still safe enough at this scale.

</details>

<details>
<summary><b>Backend</b></summary>

- **Project layout** - resource-first (`auth/`, `plan/`, `exercise/`, ... each owning its own router/schema/service) following [zhanymkanov/fastapi-best-practices](https://github.com/zhanymkanov/fastapi-best-practices), rather than the classic layered `routers/`, `schemas/`, `services/` split.
- **Auth** - JWT access + refresh tokens in httpOnly cookies (stateless access token, stateful/revocable refresh token) plus Google OAuth 2.0 login.
- **OpenAPI** - the spec is generated straight from the SQLAlchemy models and Pydantic schemas, no hand-written spec to keep in sync.
- **Testing** - Docker Compose spins up a real Postgres for integration tests instead of mocking the database.
- **Tooling** - `structlog` for structured logs, Ruff for linting and formatting, `uv` as the package manager.

</details>

<details>
<summary><b>Frontend</b></summary>

- **Generated API layer** - Orval turns the backend's OpenAPI spec into typed TanStack Query hooks; no hand-written fetch calls or API types anywhere.
- **Responsive by default** - one codebase for mobile (logging workouts at the gym) and desktop (building plans on a bigger screen) — see the screenshots above.
- **UI** - designed and implemented with the help of Claude Code (I'm no designer at all).

</details>

## Project Structure

```text
quickfit/
├── api/            # FastAPI backend, resource-first structure (auth/, plan/, exercise/, ...)
│   ├── src/
│   ├── alembic/    # DB migrations
│   └── tests/
├── frontend/       # React + TypeScript + Vite + Tailwind
│   └── src/
├── k8s/
│   ├── base/       # shared manifests (deployments, services, ingress, postgres)
│   └── overlays/   # local (minikube) and prod (k3s) patches
├── context/        # planning docs (auth, k8s, product context)
└── Taskfile.yml    # dev/lint/test/deploy commands
```

## License
MIT — see [LICENSE](LICENSE).
