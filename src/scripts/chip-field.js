class ChipField {
  constructor(textarea) {
    this.textarea = textarea;
    this.container = textarea.closest(".tna-form-item") || textarea.parentElement;
    this.values = this.parseInitialValues();

    this.createEnhancedInput();
    this.bindEvents();
    this.renderAll();
  }

  parseInitialValues() {
    return new Set(
      this.textarea.value
        .split("\n")
        .map(v => v.trim())
        .filter(Boolean)
    );
  }

  createEnhancedInput() {
    const hint = this.container?.querySelector(".tna-form-item__hint");

    this.input = document.createElement("input");
    this.input.type = "text";
    this.input.className = "tna-text-input";

    if (hint?.id) {
      this.input.setAttribute("aria-describedby", hint.id);
    }

    if (this.textarea.id) {
      this.input.id = `${this.textarea.id}-enhanced`;
      const label = this.container?.querySelector(`label[for="${this.textarea.id}"]`);
      if (label) label.setAttribute("for", this.input.id);
    }

    this.textarea.hidden = true;
    this.textarea.parentElement.appendChild(this.input);

    this.list = document.createElement("ul");
    this.list.className = "tna-compound-filters tna-!--margin-top-xs";
    this.list.setAttribute("role", "list");
    this.textarea.parentElement.appendChild(this.list);

    this.liveRegion = document.createElement("div");
    this.liveRegion.className = "visually-hidden";
    this.liveRegion.setAttribute("aria-live", "polite");
    this.textarea.parentElement.appendChild(this.liveRegion);

    if (hint) {
      hint.textContent = "Type a series and press Enter to add it";
    }
  }

  syncTextarea() {
    this.textarea.value = Array.from(this.values).join("\n");
  }

  announce(message) {
    this.liveRegion.textContent = "";
    requestAnimationFrame(() => {
      this.liveRegion.textContent = message;
    });
  }

  renderChip(value) {
    const li = document.createElement("li");
    li.className = "tna-compound-filters__item";
    li.dataset.value = value;
    li.setAttribute("role", "listitem");

    const label = document.createElement("span");
    label.textContent = value;

    const button = document.createElement("button");
    button.type = "button";
    button.className = "tna-compound-filters__link";
    button.dataset.value = value;
    button.setAttribute("aria-label", `Remove ${value}`);
    button.textContent = "×";

    li.append(label, button);
    this.list.appendChild(li);
  }

  renderAll() {
    this.list.innerHTML = "";
    this.values.forEach(v => this.renderChip(v));
  }

  addValue(rawValue) {
    const value = rawValue.trim();
    if (!value || this.values.has(value)) return;

    this.values.add(value);
    this.syncTextarea();
    this.renderChip(value);
    this.announce(`Added ${value}`);
    this.input.value = "";
  }

  removeValue(value) {
    if (!this.values.has(value)) return;

    this.values.delete(value);
    this.syncTextarea();

    const chip = this.list.querySelector(
      `li[data-value="${CSS.escape(value)}"]`
    );
    chip?.remove();

    this.announce(`Removed ${value}`);
  }

  bindEvents() {
    this.input.addEventListener("keydown", (e) => {
      if (e.key === "Enter") {
        e.preventDefault();
        this.addValue(this.input.value);
      }

      if (e.key === "Backspace" && !this.input.value) {
        const last = Array.from(this.values).at(-1);
        if (last) this.removeValue(last);
      }
    });

    this.list.addEventListener("click", (e) => {
      const button = e.target.closest("button[data-value]");
      if (!button) return;
      this.removeValue(button.dataset.value);
    });
  }
}

document.querySelectorAll("[data-js-chip-field]").forEach(textarea => {
  new ChipField(textarea);
});
