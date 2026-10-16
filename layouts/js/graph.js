export function pileLabel(value) {
  if (value === "call") return "Call";
  if (value === "not-call") return "Not-call";
  if (value === "review") return "Review";
  return "—";
}

export function pill(kind, label) {
  const el = document.createElement("span");
  el.className = `pill ${kind}`;
  const dot = document.createElement("i");
  dot.className = "dot";
  el.append(dot, document.createTextNode(label));
  return el;
}

function bandLevel(row, x, y) {
  const wave = Math.abs(Math.sin(row.seed * 0.17 + x * 1.7 + y * 2.3));
  const low = y >= 3;
  const scale = low ? 0.35 : 0.7;
  const boost = row.call && low ? 0.55 : 0;
  return Math.min(1, wave * scale + boost);
}

function bandFill(level) {
  if (level > 0.72) return "#1d4e68";
  if (level > 0.4) return "#8aa4b5";
  return "#e4ddd0";
}

function band(row, x, y) {
  const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
  rect.setAttribute("x", String(x * 4));
  rect.setAttribute("y", String(y * 4.4));
  rect.setAttribute("width", "3.4");
  rect.setAttribute("height", "3.8");
  rect.setAttribute("fill", bandFill(bandLevel(row, x, y)));
  return rect;
}

export function spectrogram(row) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("class", "spec");
  svg.setAttribute("viewBox", "0 0 96 22");
  svg.setAttribute("aria-hidden", "true");
  for (let x = 0; x < 24; x += 1) {
    for (let y = 0; y < 5; y += 1) svg.append(band(row, x, y));
  }
  return svg;
}

export function soundCell(row) {
  if (!row.sample) return document.createTextNode(row.name);
  return pill(`sample-${row.sample}`, row.name);
}

function placeCell(tr, row, value, index) {
  const td = document.createElement("td");
  if (index === 3 || index === 4 || index === 5) td.className = "num";
  if (value instanceof Node) td.append(value);
  else td.textContent = value;
  if (index === 3 && row.high) {
    const mark = document.createElement("span");
    mark.className = "mark";
    mark.textContent = "high";
    td.append(mark);
  }
  tr.append(td);
}

export function fillRow(tr, row) {
  const laya = row.pile === "—" ? "—" : pill(`pile-${row.pile}`, pileLabel(row.pile));
  const cells = [soundCell(row), row.window, spectrogram(row), row.bat, row.baf, row.noise, laya, row.reason];
  cells.forEach((value, index) => placeCell(tr, row, value, index));
}

export function keyOf(row) {
  return `${row.sample}|${row.seed}|${row.window}`;
}
