import { bindColumns } from "./columns.js";
import { renderDetail } from "./detail.js";
import { activePage, addNames, bindPage, renderChrome, renderPages } from "./pages.js";
import { pilotRows, pilotSounds } from "./rows.js";
import { ui } from "./ui.js";
import { renderBoard, renderGallery, renderGrouped, renderRead } from "./views.js";
import { keyOf } from "./graph.js";

const sounds = pilotSounds();
ui.pages = [{ id: "pilot", title: "2025-11-01", sounds, rows: pilotRows() }];
ui.activeId = "pilot";
ui.sounds = sounds;
ui.rows = ui.pages[0].rows;

function render() {
  if (!ui.rows.some((row) => keyOf(row) === ui.selectedKey)) {
    const fallback = ui.rows.find((row) => row.call) || ui.rows[0];
    ui.selectedKey = fallback ? keyOf(fallback) : "";
  }
  renderPages();
  renderChrome();
  renderRead();
  renderGrouped();
  renderBoard();
  renderGallery();
  renderDetail();
}

ui.render = render;

function bindTabs(pairs) {
  for (const [buttonId] of pairs) {
    document.getElementById(buttonId).addEventListener("click", () => {
      for (const [otherButton, otherPanel] of pairs) {
        const on = otherButton === buttonId;
        document.getElementById(otherButton).setAttribute("aria-selected", on ? "true" : "false");
        document.getElementById(otherPanel).classList.toggle("on", on);
      }
    });
  }
}

const fold = document.getElementById("fold-side");
fold.addEventListener("click", () => {
  const closed = document.querySelector(".app").classList.toggle("side-closed");
  fold.setAttribute("aria-expanded", closed ? "false" : "true");
  fold.textContent = closed ? "›" : "Hide sidebar";
  fold.setAttribute("aria-label", closed ? "Show sidebar" : "Hide sidebar");
});

document.querySelector(".stage").addEventListener("click", (event) => {
  const hit = event.target.closest("[data-key]");
  if (!hit) return;
  ui.selectedKey = hit.dataset.key;
  render();
});

document.getElementById("search").addEventListener("input", (event) => {
  ui.query = event.target.value;
  render();
});

document.querySelectorAll(".filters button").forEach((button) => {
  button.addEventListener("click", () => {
    ui.pile = button.dataset.pile;
    document.querySelectorAll(".filters button").forEach((other) => {
      other.setAttribute("aria-pressed", other === button ? "true" : "false");
    });
    render();
  });
});

bindTabs([
  ["tab-drop", "drop"],
  ["tab-sort", "sort"],
  ["tab-export", "export"]
]);
bindTabs([
  ["view-table", "as-table"],
  ["view-board", "as-board"],
  ["view-gallery", "as-gallery"],
  ["view-chart", "as-chart"]
]);

bindColumns();

document.addEventListener("click", (event) => {
  if (!ui.openMenuId) return;
  if (event.target.closest(".page-item")) return;
  ui.openMenuId = "";
  renderPages();
});

document.getElementById("page-search").addEventListener("input", (event) => {
  ui.pageQuery = event.target.value.trim().toLowerCase();
  renderPages();
});

document.getElementById("page-title").addEventListener("input", (event) => {
  const page = activePage();
  if (!page) return;
  page.title = event.target.value;
  renderPages();
});

document.getElementById("new-page").addEventListener("click", () => {
  ui.pageSerial += 1;
  const page = { id: `page-${ui.pageSerial}`, title: "Untitled", sounds: [], rows: [] };
  ui.pages.push(page);
  bindPage(page);
  render();
  document.getElementById("page-title").focus();
});

const bulk = document.getElementById("bulk");
const input = document.getElementById("picture-input");
input.addEventListener("change", () => {
  const names = [...input.files].map((file) => file.webkitRelativePath || file.name);
  if (!names.length) return;
  addNames(names);
});
bulk.addEventListener("dragover", (event) => {
  event.preventDefault();
  bulk.classList.add("over");
});
bulk.addEventListener("dragleave", () => bulk.classList.remove("over"));
bulk.addEventListener("drop", (event) => {
  event.preventDefault();
  bulk.classList.remove("over");
  const names = [...event.dataTransfer.files].map((file) => file.name);
  if (!names.length) return;
  addNames(names);
});

render();
