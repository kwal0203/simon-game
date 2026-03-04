# **Project Execution Plan: Simon Game**

**Document Owner: The dude**

**Target Start Date: 03/02/2026**

**Target Completion Date: 08/03/2026**

**Status:** \[Draft / **Approved** / In Progress\]

## **1\. Executive Summary**

A web-based Simon Game is being built where gameplay occurs on the client side. The game will have a dynamic leaderboard that records the top 100 scores across all players playing the game. The end-to-end implementation has a constraint of one week.

## **2\. High-Level Milestones**

A quick snapshot of the project phases so stakeholders can see the critical path without reading every single ticket.

* Milestone 1: Local MVP \+ core game logic (03/05/2026)
* Milestone 2: Production deployment (03/07/2026)
* Milestone 3: Production hardening \+ scaling (03/09/2026)

## **3\. Detailed Task Breakdown**

The actionable tickets. Every task should be small enough to be completed in 1 to 2 days.

### **Milestone 1: Local MVP \+ core game logic**

| Task ID | Task Name | Description | Dependencies | Estimate | Status |
| :---- | :---- | :---- | :---- | :---- | :---- |
| 1.0a | Setup directory structure | All components are given their own directory in the source code repo: database, frontend, backend, assets, tests. | None | 0.25 days | Done |
| 1.0b | Setup dev environment/tooling | Use uv, ruff, pyright, mypy, pytest, pre-commit, loguru, pydantic, vitetest, @testing-library/react, @testing-library/jest-dom jsdom, @testing-library/user-event | None | 0.25 days | Done |
| 1.0c | Test scaffolding | Add at least one test for each must-have behaviour. | None | 0.25 days | Done |
| 1.1 | Database Setup | Initialize schema and write first Alembic migration. Seed database. ORM models. | None | 0.5 days | Done |
| 1.2 | API Models | Create Pydantic models for API request/response contracts. | None | 0.5 days | Done |
| 1.3 | Read path | Write GET /v1/leaderboard | 1.1, 1.2 | 0.25 days | Done |
| 1.4 | Write path | Write POST /v1/scores | 1.1, 1.2 | 0.25 days | Done |
| 1.5a | React Frontend: State machine | Write the React frontend game play. | None | 0.25 days | Done |
| 1.5b | React frontend: UI | Write the React frontend leaderboard and gameplay UI. | None | 0.25 | Done |
| 1.5c | React frontend: Integration | Stitch the UI, state machine and database together | 1.1 \- 1.4, 1.5a, 1.5b | 0.25 | Done |
| 1.6 | Integration | Integrate frontend, backend and database. | 1.3, 1.4, 1.5 | 0.5 days | Done |
| 1.7 | Gameplay testing | Manual testing of gameplay running on localhost GET and POST endpoints use database appropriately Duplicate scores rejected by database | 1.1, 1.2, 1.3, 1.4 | 0.25 days | Done |
| 1.7a | Expand automated tests | Add integration tests for GET /v1/leaderboard and POST /v1/scores, plus regression tests for duplicate submission behaviour. | 1.3, 1.4, 1.6 | 0.25 days | To Do |

###

### **Milestone 2: Production deployment**

| Task ID | Task Name | Description | Dependencies | Estimate | Status |
| :---- | :---- | :---- | :---- | :---- | :---- |
| 2.1 | Dockerization | Write Dockerfiles for each system component and docker-compose. | 1.7 | 0.5 days | Done |
| 2.2 | Infrastructure Setup | Provision cloud instances, configure security groups. | None | 0.5 days | Done |
| 2.5a | CI/CD setup | Setup GitHub Actions to handle automated deployment. Add a dedicated db migration docker to run during CI/CD. | 2.1 | 0.5 days | Done |
| 2.3 | Public domain | Register public domain and point A-records at EC2 elastic IP address | 2.2 | 0.5 days | Done |
| 2.4 | Certificates | Provision Let’s Encrypt for certificate generation and add reverse proxy | 2.4 | 0.5 days | Done |
| 2.6 | Validation | Game is reachable and playable at public URL Game only accessible on port 80 or 443 Database port 5432 not accessible Leaderboard rejects duplicate writes | 2.1 \- 2.5 | 0.5 days | Done |

##

### **Milestone 3: Production hardening and scaling**

| Task ID | Task Name | Description | Dependencies | Estimate | Status |
| :---- | :---- | :---- | :---- | :---- | :---- |
| 3.1 | CDN | Serve static game assets from a CDN | None | 0.5 days | To Do |
| 3.2 | Rate-limiting | Update the POST /v1/scores endpoint to apply IP rate limiting | None | 0.5 days | To Do |
| 3.3 | Redis cache | Dockerize Redis service and put it in front of database. Update GET /v1/leaderboard to check cache first and to read database and write cache upon miss. Update POST /v1/scores to invalidate cache when a new score enters the database | None | 0.5 days | To Do |
| 3.4 | Scale database reads | Configure PostgreSQL to have N read replicas (start with 1). Update POST /v1/scores to write to primary database. Update GET /v1/leaderboard to hit read replicas (probably already done in 2.3). | 2.2 | 0.5 days | To Do |
| 3.5 | Validation | Load test using locust to validate p95/p99 latency targets (200ms/500ms read, 300ms write) with 1000 users Test cache stampede using locust Test rate-limiting on the write path using locust. | 2.1 \- 2.4 | 0.5 days | To Do |

## **4\. Risk Register & Mitigations**

Identify what could block you from hitting your deadlines and how you will handle it if it happens.

| Risk | Impact (H/M/L) | Mitigation Strategy |
| :---- | :---- | :---- |
| Docker/Nginx networking conflicts: Nginx reverse proxy can’t resolve IP address of React frontend or FastAPI backend  | High | Use a docker-compose.yaml with a shared custom Docker bridge network so the services can be resolved by name rather than IP |
| DNS/SSL propagation delays: Let’s Encrypt certification fails because the domains A-record hasn’t propagated across global DNS servers | Medium | Register the domain on Day 1 of the execution to get ready for the certification step days later. |
| Cache invalidation race condition: A user may view the leaderboard before the cache has been invalidated. Stale data that does not contain their high score is returned. | Medium | Optimistic UI update: When a user submits a score, the returned rank can be used to update the local leaderboard UI. This guarantees the user sees their score instantly. |

##

## **5\. Definition of Done (DoD)**

*The strict criteria that must be met before this project is officially considered "complete."*

* Game is reachable on public URL
* Deployment is automated
* Write path is idempotent \+ rate limited
* Read path is scaled
* Read and write paths adhere to p95/p99 latencies
