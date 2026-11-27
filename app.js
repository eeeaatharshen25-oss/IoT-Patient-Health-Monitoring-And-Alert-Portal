// Poll the latest reading for the selected patient. Values are rendered as text, not HTML.
document.addEventListener("DOMContentLoaded", () => {
  const monitor = document.getElementById("monitor");
  if (!monitor) return;
  const patientId = monitor.dataset.patientId;
  const setText = (id, value) => {
    const el = document.getElementById(id);
    if (el) el.textContent = value ?? "—";
  };
  async function refreshReading() {
    try {
      const response = await fetch(`/api/readings/latest?patient_id=${encodeURIComponent(patientId)}`);
      if (!response.ok) return;
      const data = await response.json();
      if (!data || !data.id) return;
      setText("heartRate", data.heart_rate);
      setText("spo2", data.spo2);
      setText("temperature", data.temperature);
      setText("recordedAt", data.recorded_at);
    } catch (error) {
      // Keep the last displayed values if the server is temporarily unavailable.
    }
  }
  window.setInterval(refreshReading, 5000);
});
