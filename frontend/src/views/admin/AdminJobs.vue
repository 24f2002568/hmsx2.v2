<template>
  <div>
    <div class="topbar">
      <div class="topbar-title">Background Jobs</div>
      <div class="mono" style="font-size:11px; color:var(--ink-faint); display:flex; align-items:center; gap:6px;">
        <span :class="['worker-dot', workerStatus]"></span>
        {{ workerStatus === 'online' ? 'Worker Online' : workerStatus === 'checking' ? 'Checking...' : 'Worker Offline' }}
      </div>
    </div>
    <div class="content-area">

      <!-- Celery Health Check -->
      <div class="card-hms mb-4">
        <div class="section-header">
          <div class="section-title">Worker Health</div>
          <button @click="pingWorker" :disabled="pinging" class="btn-outline" style="padding:6px 14px; font-size:12px;">
            <span v-if="pinging" class="spinner-ring" style="width:12px;height:12px;margin-right:4px;"></span>
            Ping Worker
          </button>
        </div>
        <div v-if="pingResult" class="ping-result">
          <div class="ping-row"><span>Status</span><strong>{{ pingResult.status }}</strong></div>
          <div class="ping-row"><span>Worker</span><strong>{{ pingResult.worker || '—' }}</strong></div>
          <div class="ping-row"><span>Time (UTC)</span><strong>{{ pingResult.time }}</strong></div>
        </div>
        <div v-else style="font-size:13px; color:var(--ink-faint); padding: 4px 0;">
          Click "Ping Worker" to verify your Celery worker is running.
        </div>
      </div>

      <!-- Scheduled Jobs -->
      <div class="card-hms mb-4">
        <div class="section-header">
          <div class="section-title">Scheduled Jobs</div>
        </div>
        <div class="jobs-grid">
          <div class="job-card">
            <div class="job-icon"><i class="bi bi-bell"></i></div>
            <div class="job-info">
              <div class="job-name">Daily Reminders</div>
              <div class="job-schedule">Every day at 08:00</div>
              <div class="job-desc">Sends appointment reminders to patients with bookings today via email & Google Chat.</div>
            </div>
            <div class="job-actions">
              <button @click="triggerJob('reminders')" :disabled="jobRunning.reminders" class="btn-ink" style="padding:7px 16px; font-size:12px;">
                <span v-if="jobRunning.reminders" class="spinner-ring" style="width:12px;height:12px;margin-right:4px;"></span>
                Run Now
              </button>
              <div v-if="jobResults.reminders" class="job-result-badge">
                ✓ {{ jobResults.reminders.sent }} sent
              </div>
            </div>
          </div>

          <div class="job-card">
            <div class="job-icon"><i class="bi bi-file-earmark-bar-graph"></i></div>
            <div class="job-info">
              <div class="job-name">Monthly Reports</div>
              <div class="job-schedule">1st of every month at 06:00</div>
              <div class="job-desc">Generates HTML activity reports for all doctors and sends them via email.</div>
            </div>
            <div class="job-actions">
              <button @click="triggerJob('reports')" :disabled="jobRunning.reports" class="btn-ink" style="padding:7px 16px; font-size:12px;">
                <span v-if="jobRunning.reports" class="spinner-ring" style="width:12px;height:12px;margin-right:4px;"></span>
                Run Now
              </button>
              <div v-if="jobResults.reports" class="job-result-badge">
                ✓ {{ jobResults.reports.reports_sent }} sent
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Task Monitor -->
      <div class="card-hms">
        <div class="section-header">
          <div class="section-title">Task Monitor</div>
          <div class="mono" style="font-size:11px; color:var(--ink-faint);">Recent task IDs</div>
        </div>
        <div v-if="!taskLog.length" class="empty-state" style="padding:24px 0;">
          <i class="bi bi-list-task"></i>
          <p>NO TASKS RUN YET</p>
        </div>
        <div v-else>
          <div v-for="entry in taskLog" :key="entry.task_id" class="task-log-row">
            <div class="task-log-left">
              <div class="task-name">{{ entry.name }}</div>
              <div class="mono" style="font-size:10px; color:var(--ink-faint);">{{ entry.task_id }}</div>
            </div>
            <div class="task-log-right">
              <span :class="['task-status-badge', entry.status.toLowerCase()]">{{ entry.status }}</span>
              <button v-if="entry.status === 'PENDING'" @click="pollStatus(entry)"
                class="btn-outline" style="padding:3px 8px; font-size:11px; margin-left:8px;">
                Poll
              </button>
              <div v-if="entry.result" class="task-result-text">{{ JSON.stringify(entry.result) }}</div>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { axios, API } from '../../store/auth'

const workerStatus = ref('checking')
const pinging = ref(false)
const pingResult = ref(null)
const jobRunning = ref({ reminders: false, reports: false })
const jobResults = ref({ reminders: null, reports: null })
const taskLog = ref([])

const pingWorker = async () => {
  pinging.value = true
  workerStatus.value = 'checking'
  try {
    const { data } = await axios.post(`${API}/jobs/test-ping`)
    const taskId = data.task_id
    addToLog('Test Ping', taskId)
    // Poll for result
    await pollUntilDone(taskId, (result) => {
      pingResult.value = result
      workerStatus.value = 'online'
    })
  } catch (e) {
    workerStatus.value = 'offline'
  } finally {
    pinging.value = false
  }
}

const triggerJob = async (type) => {
  jobRunning.value[type] = true
  const endpoint = type === 'reminders' ? 'trigger-reminders' : 'trigger-reports'
  const name = type === 'reminders' ? 'Daily Reminders' : 'Monthly Reports'
  try {
    const { data } = await axios.post(`${API}/jobs/${endpoint}`)
    addToLog(name, data.task_id)
    await pollUntilDone(data.task_id, (result) => {
      jobResults.value[type] = result
    })
  } catch (e) {
    console.error('Job trigger failed', e)
  } finally {
    jobRunning.value[type] = false
  }
}

const pollUntilDone = async (taskId, onDone, maxAttempts = 15) => {
  for (let i = 0; i < maxAttempts; i++) {
    await new Promise(r => setTimeout(r, 2000))
    try {
      const { data } = await axios.get(`${API}/jobs/task-status/${taskId}`)
      updateLogEntry(taskId, data.status, data.result)
      if (data.status === 'SUCCESS') { onDone(data.result); return }
      if (data.status === 'FAILURE') { return }
    } catch {}
  }
}

const pollStatus = async (entry) => {
  try {
    const { data } = await axios.get(`${API}/jobs/task-status/${entry.task_id}`)
    updateLogEntry(entry.task_id, data.status, data.result)
  } catch {}
}

const addToLog = (name, taskId) => {
  taskLog.value.unshift({ name, task_id: taskId, status: 'PENDING', result: null })
  if (taskLog.value.length > 20) taskLog.value.pop()
}

const updateLogEntry = (taskId, status, result) => {
  const entry = taskLog.value.find(e => e.task_id === taskId)
  if (entry) { entry.status = status; entry.result = result }
}
</script>

<style scoped>
.worker-dot {
  width: 8px; height: 8px;
  border-radius: 50%;
  display: inline-block;
}
.worker-dot.online { background: #1a6b1a; }
.worker-dot.offline { background: #c00; }
.worker-dot.checking {
  background: #888;
  animation: pulse 1s infinite;
}
@keyframes pulse { 0%,100% { opacity:1; } 50% { opacity:0.3; } }

.ping-result {
  background: var(--paper-off);
  border: 1px solid var(--border);
  border-radius: var(--radius);
  padding: 12px 16px;
}
.ping-row {
  display: flex;
  justify-content: space-between;
  padding: 6px 0;
  border-bottom: 1px solid var(--border);
  font-size: 13px;
}
.ping-row:last-child { border-bottom: none; }
.ping-row span { color: var(--ink-faint); font-family: var(--font-mono); font-size: 10px; letter-spacing: 0.1em; text-transform: uppercase; }
.ping-row strong { font-family: var(--font-mono); font-size: 12px; }

.jobs-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }

.job-card {
  display: flex;
  gap: 16px;
  background: var(--paper-off);
  border: 1px solid var(--border);
  border-radius: var(--radius-lg);
  padding: 20px;
  align-items: flex-start;
}

.job-icon {
  width: 40px; height: 40px;
  background: var(--ink);
  border-radius: var(--radius);
  display: flex; align-items: center; justify-content: center;
  color: var(--paper);
  font-size: 18px;
  flex-shrink: 0;
}

.job-info { flex: 1; }

.job-name {
  font-family: var(--font-display);
  font-size: 15px;
  font-weight: 700;
  margin-bottom: 2px;
}

.job-schedule {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.12em;
  text-transform: uppercase;
  color: var(--ink-faint);
  margin-bottom: 8px;
}

.job-desc {
  font-size: 12px;
  color: var(--ink-muted);
  line-height: 1.5;
}

.job-actions {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 6px;
  flex-shrink: 0;
}

.job-result-badge {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.1em;
  color: #1a6b1a;
  background: #f5fff5;
  border: 1px solid #b8d8b8;
  padding: 3px 8px;
  border-radius: 20px;
}

/* Task log */
.task-log-row {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  padding: 12px 0;
  border-bottom: 1px solid var(--border);
  gap: 16px;
}
.task-log-row:last-child { border-bottom: none; }

.task-name {
  font-size: 13px;
  font-weight: 600;
  margin-bottom: 2px;
}

.task-log-right {
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  gap: 4px;
}

.task-status-badge {
  font-family: var(--font-mono);
  font-size: 10px;
  letter-spacing: 0.1em;
  text-transform: uppercase;
  padding: 2px 8px;
  border-radius: 20px;
  border: 1px solid;
}
.task-status-badge.pending   { background: #f5f5f5; color: #666; border-color: #ddd; }
.task-status-badge.success   { background: #f5fff5; color: #1a6b1a; border-color: #b8d8b8; }
.task-status-badge.failure   { background: #fff5f5; color: #9b2020; border-color: #e5b0b0; }
.task-status-badge.started   { background: #f5f5f5; color: #333; border-color: #ccc; }

.task-result-text {
  font-family: var(--font-mono);
  font-size: 10px;
  color: var(--ink-faint);
  max-width: 260px;
  word-break: break-all;
}

@media (max-width: 768px) {
  .jobs-grid { grid-template-columns: 1fr; }
}
</style>
