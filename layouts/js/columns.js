const fitWidths = [118, 120, 132, 92, 68, 80, 100, 80];
const widths = fitWidths.slice();

function applyWidths() {
  document.querySelectorAll("table.sheet").forEach((table) => {
    table.querySelectorAll("col").forEach((col, index) => {
      col.style.width = `${widths[index]}px`;
    });
  });
}

function bindGrip(grip, index) {
  grip.addEventListener("pointerdown", (event) => {
    event.preventDefault();
    event.stopPropagation();
    const startX = event.clientX;
    const startW = widths[index];
    grip.classList.add("active");
    document.body.classList.add("col-drag");
    function move(moveEvent) {
      widths[index] = Math.max(44, Math.round(startW + moveEvent.clientX - startX));
      applyWidths();
    }
    function up() {
      grip.classList.remove("active");
      document.body.classList.remove("col-drag");
      window.removeEventListener("pointermove", move);
      window.removeEventListener("pointerup", up);
    }
    window.addEventListener("pointermove", move);
    window.addEventListener("pointerup", up);
  });
  grip.addEventListener("dblclick", (event) => {
    event.preventDefault();
    event.stopPropagation();
    widths[index] = fitWidths[index];
    applyWidths();
  });
}

export function bindColumns() {
  document.querySelectorAll("table.sheet").forEach((table) => {
    table.querySelectorAll("th").forEach((th, index) => {
      const grip = document.createElement("span");
      grip.className = "grip";
      grip.title = "Drag to close or extend";
      grip.setAttribute("role", "separator");
      grip.setAttribute("aria-orientation", "vertical");
      grip.setAttribute("aria-label", `Resize ${th.textContent.trim()}`);
      th.append(grip);
      bindGrip(grip, index);
    });
  });
  applyWidths();
}
