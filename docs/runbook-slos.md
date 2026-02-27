# **Operational Runbook & SLOs: Simon Game**

**Service Owner: The Dude**

**On-Call Contact:**

**Repository:**

**Production URL:**

## **1\. Service Level Objectives (SLOs)**

*The strict, measurable promises we make regarding the system's performance and reliability. If we breach these, we stop building new features and focus on fixing infrastructure.*

* **Uptime (Availability):** 99.9% uptime per month (allows for \~43 minutes of downtime/month).
* **Read Latency (Leaderboard):** p95 \< 200ms | p99 \< 500ms.
* **Write Latency (Score Submission):** p95 \< 300ms.
* **Data Freshness:** The retrieved leaderboard will be no more than 10 seconds stale.

## **2\. Monitoring & Dashboards**

*Where to look when something goes wrong.*

* **Uptime Monitoring:** \[Link to UptimeRobot or similar service\] \- Pings the /health endpoint every 5 minutes.
* **Infrastructure Metrics:** \[Link to AWS CloudWatch\] \- Monitors EC2 CPU, Memory, and Disk IO.
* **Application Logs:** Accessible directly on the EC2 instance via Docker.
  * *Command to view API logs:* docker logs \--tail 100 \-f fastapi\_backend
  * *Command to view DB logs:* docker logs \--tail 100 \-f postgres\_db

## **3\. Alert Definitions**

*What actually triggers an email/page to the developer.*

| Alert Name | Trigger Condition | Severity |
| :---- | :---- | :---- |
| **API Down** | /health endpoint returns 5xx or times out for 2 consecutive polls. | SEV-1 (Critical) |
| **High Write Latency** | POST /v1/scores p95 \> 300ms for 5 minutes. | SEV-2 (Warning) |
| **Disk Space Low** | EC2 instance disk space \> 85% utilized. | SEV-2 (Warning) |

## **4\. Playbooks (Troubleshooting Guides)**

*Step-by-step instructions on how to fix the system at 3:00 AM when an alert fires.*

### **Playbook A: API is returning 500 Internal Server Error**

**Symptoms:** Uptime monitor fires an alert. Users cannot submit scores or load the leaderboard.

**Resolution Steps:**

1. SSH into the EC2 instance: ssh \-i key.pem ec2-user@\<ip-address\>
2. Check if the Docker containers are running: docker ps
3. If the fastapi\_backend container exited, view the crash logs: docker logs fastapi\_backend
4. If the database connection failed, restart the Postgres container: docker restart postgres\_db, then restart the API: docker restart fastapi\_backend.
5. If the EC2 instance is completely unresponsive, reboot it via the AWS Console.

### **Playbook B: Cache is Down (Read path is slow)**

**Symptoms:** Read latencies spike above 500ms. Logs show RedisConnectionError.

**Resolution Steps:**

1. Verify Redis container status: docker ps | grep redis
2. If Redis is OOM (Out of Memory), restart the container: docker restart redis\_cache.
3. Check the FastAPI logs to ensure the fallback mechanism (querying Postgres directly) is successfully engaging while Redis is rebooting.
4. Verify the frontend is seamlessly rendering the UI despite the latency spike.

### **Playbook C: EC2 Disk is Full**

**Symptoms:** CloudWatch triggers a "Disk Space \> 85%" alert. Database inserts begin failing.

**Resolution Steps:**

1. SSH into the EC2 instance.
2. Check disk usage: df \-h
3. Prune old/dangling Docker images to free up space: docker system prune \-af
4. Clear bloated Docker container logs: truncate \-s 0 /var/lib/docker/containers/\*/\*-json.log

## **5\. Deployment & Rollback Commands**

*Quick reference for standard operational tasks.*

* **Deploy latest main branch:**
  * git pull origin main
  * docker-compose up \-d \--build
* **Rollback to previous tag:**
  * git checkout \<previous-tag\>
  * docker-compose up \-d \--build
* **Run Database Migration:**
  * docker exec \-it fastapi\_backend alembic upgrade head
