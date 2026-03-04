## Typical Tradeoff Layers
1. Requirements layer: what to optimize (latency, cost, reliability, speed)
2. Architecture layer: monolith vs microservices, sync vs async, proxy vs direct
3. Data layer: SQL vs NoSQL, consistency model, indexing/partitioning/caching
4. Infra layer: cloud services vs self-managed, containers vs serverless, regions
5. Delivery/ops layer: CI/CD strategy, rollout/rollback, observability, on-call
6. Security layer: auth model, secrets, network boundaries, abuse controls
7. Vendor/tool layer: Nginx vs ALB, Postgres vs DynamoDB, Redis vs Memcached

# Tradeoff Decision Template

## 1) Decision Summary
- Decision title:
- Date:
- Status: Proposed | Accepted | Deprecated
- Owner:

## 2) Context
- Problem statement:
- Why this matters now:
- Scope (what systems/components are affected):

## 3) Constraints
- Budget:
- Deadline:
- Performance targets (e.g., p95 latency, throughput):
- Reliability targets (e.g., SLO/uptime):
- Security/compliance constraints:
- Team/operational constraints:

## 4) Options Considered
### Option A: <name>
- Description:
- Pros:
- Cons:
- Cost estimate:
- Complexity estimate:
- Key risks:

### Option B: <name>
- Description:
- Pros:
- Cons:
- Cost estimate:
- Complexity estimate:
- Key risks:

### Option C: <name> (optional)
- Description:
- Pros:
- Cons:
- Cost estimate:
- Complexity estimate:
- Key risks:

## 5) Tradeoffs
- What we gain by chosen option:
- What we give up:
- Categories impacted:
  - Performance
  - Reliability
  - Security
  - Cost
  - Delivery speed
  - Developer productivity

## 6) Decision
- Chosen option:
- Why this option is best for current context:
- Assumptions:

## 7) Mitigations for Downsides
- Downside 1 -> Mitigation:
- Downside 2 -> Mitigation:

## 8) Rollout Plan
- Implementation steps:
- Migration/compatibility notes:
- Rollback plan:

## 9) Validation Plan
- Success metrics:
- How we will measure them:
- Test/load/failure drill plan:

## 10) Revisit Triggers
- Conditions that should force re-evaluation:
- Review date:

## 11) Outcome (fill after implementation)
- What happened in production:
- Metrics before vs after:
- Incidents/issues encountered:
- Follow-up actions:
