import { keyOf, pileLabel, spectrogram } from "./graph.js";
import { ui } from "./ui.js";

function whyText(row) {
  if (row.call) {
    return "bat 0.507 is larger than baf 0.493, so Blue A calls this window a call. Laya agrees at 0.743.";
  }
  if (row.reason === "blue-a") {
    return "This is the highest bat in Sample D. Laya was under 0.6, so Blue A’s not-call label stayed. The reason is blue-a.";
  }
  if (row.high) {
    return "This is the highest bat in the clip, and it is still far below baf, so the window stays not-call.";
  }
  return "This 25-second window was scored. Its bat is below the clip high, and Laya did not move it to call.";
}

function scoreList(row) {
  const props = document.createElement("dl");
  props.className = "props";
  [
    ["bat", row.bat],
    ["baf", row.baf],
    ["63 Hz", row.noise],
    ["Laya", pileLabel(row.pile)],
    ["Reason", row.reason]
  ].forEach(([label, value]) => {
    const dt = document.createElement("dt");
    dt.textContent = label;
    const dd = document.createElement("dd");
    dd.textContent = value;
    props.append(dt, dd);
  });
  return props;
}

const notes = [
  "Review stays empty. Laya never reached 0.6 while naming the other pile.",
  "A 70.6 dB and C 71.5 dB are the quieter pair. B 76.2 dB and D 77.4 dB are the noisier pair. Six clips are too few to call that a noise effect."
];

export function renderDetail() {
  const row = ui.rows.find((item) => keyOf(item) === ui.selectedKey) || ui.rows.find((item) => item.call) || ui.rows[0];
  const inspector = document.getElementById("inspector");
  inspector.replaceChildren();
  const eyebrow = document.createElement("p");
  eyebrow.className = "eyebrow";
  eyebrow.textContent = "Selected row";
  if (!row) {
    const empty = document.createElement("p");
    empty.textContent = "Open a graph in the table. Its scores show here.";
    inspector.append(eyebrow, empty);
    return;
  }
  ui.selectedKey = keyOf(row);
  const title = document.createElement("h2");
  title.textContent = row.name;
  const sub = document.createElement("p");
  sub.className = "hint";
  sub.textContent = `${row.window} of the recording, drawn as a spectrogram.`;
  const graph = spectrogram(row);
  graph.classList.add("spec-lg");
  const why = document.createElement("p");
  why.textContent = whyText(row);
  const noteList = document.createElement("div");
  noteList.className = "note-list";
  notes.forEach((text) => {
    const p = document.createElement("p");
    p.className = "hint";
    p.textContent = text;
    noteList.append(p);
  });
  inspector.append(eyebrow, title, sub, graph, scoreList(row), why, noteList);
}
