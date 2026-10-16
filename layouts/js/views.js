import { fillRow, keyOf, pill, pileLabel, spectrogram } from "./graph.js";
import { ui } from "./ui.js";

export function matches(row) {
  const q = ui.query.trim().toLowerCase();
  if (q && !`${row.name} ${row.window}`.toLowerCase().includes(q)) return false;
  if (ui.pile !== "all" && row.pile !== ui.pile) return false;
  return true;
}

function visibleRows() {
  return ui.rows.filter(matches);
}

function paint(tr, row) {
  tr.className = "data";
  tr.dataset.key = keyOf(row);
  if (tr.dataset.key === ui.selectedKey) tr.classList.add("picked");
  fillRow(tr, row);
}

export function renderRead() {
  const shown = ui.rows.filter(matches);
  const readBody = document.getElementById("read-body");
  readBody.replaceChildren();
  shown.forEach((row) => {
    const tr = document.createElement("tr");
    paint(tr, row);
    readBody.append(tr);
  });
  document.getElementById("row-count").textContent = `${shown.length} of ${ui.rows.length}`;
}

function groupHead(key, count) {
  const head = document.createElement("tr");
  head.className = "group";
  const td = document.createElement("td");
  td.colSpan = 8;
  td.append(pill(`pile-${key}`, pileLabel(key)), document.createTextNode(`  ${count}`));
  head.append(td);
  return head;
}

export function renderGrouped() {
  const shown = visibleRows();
  const sortBody = document.getElementById("sort-body");
  sortBody.replaceChildren();
  const order = ["call", "not-call", "review"];
  const piles = ui.pile === "all" ? order : [ui.pile];
  piles.forEach((key) => {
    const group = shown.filter((row) => row.pile === key);
    sortBody.append(groupHead(key, group.length));
    group.forEach((row) => {
      const tr = document.createElement("tr");
      paint(tr, row);
      sortBody.append(tr);
    });
  });
  document.getElementById("sort-count").textContent = `${shown.length} shown`;
}

function cardMeta(row) {
  const meta = document.createElement("div");
  meta.className = "meta";
  if (row.sample) meta.append(pill(`sample-${row.sample}`, row.sample));
  if (row.bat === "—") return meta;
  const score = document.createElement("span");
  score.className = "score";
  score.textContent = `bat ${row.bat}`;
  meta.append(score);
  return meta;
}

function boardCard(row) {
  const card = document.createElement("article");
  card.className = "card";
  const title = document.createElement("strong");
  title.textContent = `${row.name} · ${row.window}`;
  card.dataset.key = keyOf(row);
  card.append(spectrogram(row), title, cardMeta(row));
  return card;
}

export function renderBoard() {
  const board = document.getElementById("board");
  const shown = visibleRows();
  board.replaceChildren();
  ["call", "not-call", "review"].forEach((key) => {
    if (ui.pile !== "all" && ui.pile !== key) return;
    const group = shown.filter((row) => row.pile === key);
    const column = document.createElement("section");
    column.className = "column";
    const header = document.createElement("header");
    const count = document.createElement("span");
    count.textContent = String(group.length);
    header.append(pill(`pile-${key}`, pileLabel(key)), count);
    const cards = document.createElement("div");
    cards.className = "cards";
    group.forEach((row) => cards.append(boardCard(row)));
    column.append(header, cards);
    board.append(column);
  });
}

function tileMeta(row) {
  const meta = document.createElement("div");
  meta.className = "meta";
  if (row.sample) meta.append(pill(`sample-${row.sample}`, row.sample));
  if (row.pile !== "—") meta.append(pill(`pile-${row.pile}`, pileLabel(row.pile)));
  return meta;
}

export function renderGallery() {
  const gallery = document.getElementById("gallery");
  gallery.replaceChildren();
  visibleRows().forEach((row) => {
    const tile = document.createElement("article");
    tile.className = "tile";
    const title = document.createElement("strong");
    title.textContent = `${row.name} · ${row.window}`;
    tile.dataset.key = keyOf(row);
    tile.append(spectrogram(row), title, tileMeta(row));
    gallery.append(tile);
  });
}
