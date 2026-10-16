export const clips = [
  { id: "A", n: 7, noise: "70.6", callAt: 4, bat: "0.507", baf: "0.493", window: "92.4–98.6 s", reason: "agree" },
  { id: "B", n: 9, noise: "76.2", highAt: 1, bat: "0.030", baf: "0.970" },
  { id: "C", n: 6, noise: "71.5", highAt: 1, bat: "0.073", baf: "0.927" },
  { id: "D", n: 20, noise: "77.4", highAt: 1, bat: "0.044", baf: "0.956", reason: "blue-a" },
  { id: "E", n: 22, noise: "", highAt: 1, bat: "0.034", baf: "0.966" },
  { id: "F", n: 5, noise: "", highAt: 1, bat: "0.041", baf: "0.959" }
];

function scoredWindow(clip, index) {
  const call = clip.callAt === index;
  const high = call || clip.highAt === index;
  return {
    name: `Sample ${clip.id}`,
    sample: clip.id,
    window: call ? clip.window : "25 s",
    bat: high ? clip.bat : "—",
    baf: high ? clip.baf : "—",
    noise: clip.noise ? `${clip.noise} dB` : "—",
    pile: call ? "call" : "not-call",
    reason: reasonFor(call, high, clip.reason),
    high: high && !call,
    call,
    seed: clip.id.codePointAt(0) * 100 + index
  };
}

function reasonFor(call, high, saved) {
  if (call) return "agree";
  if (high && saved) return saved;
  return "—";
}

export function pilotRows() {
  const rows = [];
  for (const clip of clips) {
    for (let index = 1; index <= clip.n; index += 1) {
      rows.push(scoredWindow(clip, index));
    }
  }
  return rows;
}

export function pilotSounds() {
  return clips.map((clip) => ({
    id: clip.id,
    file: `2025-11-01-sample-${clip.id.toLowerCase()}.wav`,
    graphs: clip.n,
    noise: clip.noise ? `${clip.noise} dB` : "—"
  }));
}
