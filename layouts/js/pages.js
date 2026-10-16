import { ui } from "./ui.js";

export function activePage() {
  return ui.pages.find((item) => item.id === ui.activeId);
}

export function bindPage(page) {
  ui.activeId = page.id;
  ui.sounds = page.sounds;
  ui.rows = page.rows;
  ui.selectedKey = "";
  ui.query = "";
  const search = document.getElementById("search");
  if (search) search.value = "";
}

function closeAll() {
  ui.activeId = "";
  ui.sounds = [];
  ui.rows = [];
  ui.selectedKey = "";
}

function takeOver(index) {
  const next = ui.pages[index] || ui.pages[index - 1];
  if (next) bindPage(next);
  else closeAll();
}

export function deletePage(id) {
  const index = ui.pages.findIndex((page) => page.id === id);
  if (index < 0) return;
  const wasOpen = ui.pages[index].id === ui.activeId;
  ui.pages.splice(index, 1);
  if (wasOpen) takeOver(index);
  ui.render();
}

function dotsIcon() {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 16 16");
  svg.setAttribute("width", "16");
  svg.setAttribute("height", "16");
  svg.setAttribute("aria-hidden", "true");
  [3.5, 8, 12.5].forEach((cx) => {
    const circle = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    circle.setAttribute("cx", String(cx));
    circle.setAttribute("cy", "8");
    circle.setAttribute("r", "1.15");
    circle.setAttribute("fill", "currentColor");
    svg.append(circle);
  });
  return svg;
}

function menuIcon(kind) {
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
  svg.setAttribute("viewBox", "0 0 16 16");
  svg.setAttribute("width", "14");
  svg.setAttribute("height", "14");
  svg.setAttribute("aria-hidden", "true");
  const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
  path.setAttribute("fill", "currentColor");
  path.setAttribute("d", kind === "rename"
    ? "M11.4 1.6a1.2 1.2 0 0 1 1.7 0l1.3 1.3a1.2 1.2 0 0 1 0 1.7L6.7 12.3 3.5 13l.7-3.2 7.2-8.2Z"
    : "M6.2 1.5h3.6l.5 1.2H13v1.3H3V2.7h2.7l.5-1.2ZM4.3 5h7.4l-.55 8.1H4.85L4.3 5Z");
  svg.append(path);
  return svg;
}

function focusTitle() {
  const title = document.getElementById("page-title");
  title.focus();
  title.select();
}

function pageMenu(page) {
  const menu = document.createElement("div");
  menu.className = "page-menu";
  menu.setAttribute("role", "menu");
  const rename = document.createElement("button");
  rename.type = "button";
  rename.append(menuIcon("rename"), document.createTextNode("Rename"));
  rename.addEventListener("click", () => {
    if (page.id !== ui.activeId) bindPage(page);
    ui.openMenuId = "";
    ui.render();
    focusTitle();
  });
  const rule = document.createElement("div");
  rule.className = "menu-rule";
  const remove = document.createElement("button");
  remove.type = "button";
  remove.className = "danger";
  remove.append(menuIcon("delete"), document.createTextNode("Delete"));
  remove.addEventListener("click", () => {
    ui.openMenuId = "";
    deletePage(page.id);
  });
  menu.append(rename, rule, remove);
  return menu;
}

function pageRow(page) {
  const row = document.createElement("div");
  row.className = "page-row";
  const button = document.createElement("button");
  button.type = "button";
  button.className = "day";
  button.setAttribute("aria-pressed", page.id === ui.activeId ? "true" : "false");
  const name = document.createElement("b");
  name.textContent = page.title || "Untitled";
  button.append(name);
  button.addEventListener("click", () => {
    ui.openMenuId = "";
    bindPage(page);
    ui.render();
  });
  const more = document.createElement("button");
  more.type = "button";
  more.className = "more-btn";
  more.append(dotsIcon());
  more.setAttribute("aria-label", `Options for ${page.title || "Untitled"}`);
  more.setAttribute("aria-expanded", ui.openMenuId === page.id ? "true" : "false");
  more.addEventListener("click", (event) => {
    event.stopPropagation();
    ui.openMenuId = ui.openMenuId === page.id ? "" : page.id;
    renderPages();
  });
  row.append(button, more);
  return row;
}

function pageItem(page) {
  const item = document.createElement("div");
  item.className = "page-item";
  item.append(pageRow(page));
  if (ui.openMenuId === page.id) item.append(pageMenu(page));
  return item;
}

export function renderPages() {
  const pageList = document.getElementById("page-list");
  pageList.replaceChildren();
  const shown = ui.pages.filter((page) => page.title.toLowerCase().includes(ui.pageQuery));
  if (!shown.length) {
    if (!ui.pageQuery) return;
    const note = document.createElement("p");
    note.className = "more";
    note.textContent = "No page matches.";
    pageList.append(note);
    return;
  }
  shown.forEach((page) => pageList.append(pageItem(page)));
}

function setBlank(empty) {
  document.getElementById("page-empty").hidden = !empty;
  document.getElementById("page-filled").hidden = empty;
  document.getElementById("sort-blank").hidden = !empty;
  document.getElementById("export-blank").hidden = !empty;
  document.getElementById("sort").classList.toggle("is-empty", empty);
  document.getElementById("export").classList.toggle("is-empty", empty);
}

export function renderChrome() {
  const page = activePage();
  const title = document.getElementById("page-title");
  const meta = document.getElementById("page-meta");
  document.getElementById("no-page").hidden = Boolean(page);
  if (!page) {
    setBlank(true);
    document.getElementById("page-empty").hidden = true;
    title.disabled = true;
    title.value = "";
    meta.textContent = "No page open.";
    return;
  }
  title.disabled = false;
  const empty = ui.rows.length === 0;
  setBlank(empty);
  if (document.activeElement !== title) title.value = page.title;
  meta.textContent = empty
    ? "Empty. Drop sounds into this page."
    : `${ui.rows.length} graphs from ${ui.sounds.length} sounds`;
}

export function addNames(names) {
  const page = activePage();
  names.forEach((name) => {
    const file = name.split(/[\\/]/).pop();
    const id = `f${page.sounds.length + 1}`;
    page.sounds.push({ id, file, graphs: "—", noise: "—" });
    page.rows.push({
      name: file,
      sample: "",
      window: "not compiled",
      bat: "—",
      baf: "—",
      noise: "—",
      pile: "—",
      reason: "—",
      high: false,
      call: false,
      seed: page.rows.length + 1
    });
  });
  ui.sounds = page.sounds;
  ui.rows = page.rows;
  ui.render();
}
