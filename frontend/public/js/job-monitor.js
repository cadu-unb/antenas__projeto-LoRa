/**
 * JobMonitor — polling de job a cada 2 segundos.
 *
 * Uso:
 *   const monitor = new JobMonitor(jobId, {
 *     onProgress(pct, status) {},
 *     onDone(result) {},
 *     onFailed(status, errorMsg) {},
 *     onCancelled() {},
 *   });
 *   monitor.start();
 *   // Para cancelar pelo cliente: monitor.stop();
 */
export class JobMonitor {
  constructor(jobId, callbacks = {}) {
    this.jobId = jobId;
    this._onProgress = callbacks.onProgress ?? (() => {});
    this._onDone = callbacks.onDone ?? (() => {});
    this._onFailed = callbacks.onFailed ?? (() => {});
    this._onCancelled = callbacks.onCancelled ?? (() => {});
    this._intervalId = null;
    this._stopped = false;
  }

  start() {
    this._stopped = false;
    this._poll();
    this._intervalId = setInterval(() => this._poll(), 2000);
  }

  stop() {
    this._stopped = true;
    if (this._intervalId !== null) {
      clearInterval(this._intervalId);
      this._intervalId = null;
    }
  }

  async _poll() {
    if (this._stopped) return;
    try {
      const res = await fetch(`/api/v1/jobs/${this.jobId}`);
      if (!res.ok) {
        if (res.status === 404) {
          this.stop();
          this._onFailed("FAILED_TIME_LIMIT", "Job não encontrado no servidor.");
        }
        return;
      }
      const job = await res.json();

      this._onProgress(job.progress ?? 0, job.status);

      if (job.status === "DONE") {
        this.stop();
        this._onDone(job.result);
      } else if (job.status === "CANCELLED") {
        this.stop();
        this._onCancelled();
      } else if (job.status === "FAILED_MEMORY_LIMIT" || job.status === "FAILED_TIME_LIMIT") {
        this.stop();
        this._onFailed(job.status, job.error ?? "Erro desconhecido.");
      }
    } catch (err) {
      console.error("[JobMonitor] poll error:", err);
    }
  }
}
