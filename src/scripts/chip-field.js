class ChipField {
  constructor(textarea) {
    this.textarea = textarea;
    this.container = textarea.closest(".tna-form-item") || textarea.parentElement;
    this.values = this.parseInitialValues();

    this.createEnhancedInput();
    this.bindEvents();
    this.renderAll();
  }

  /**
   * Parse the initial values from the textarea
   * @returns {Set} A set of the initial values
   */
  parseInitialValues() {
    return new Set(
      this.textarea.value
        .split("\n")
        .map(v => v.trim())
        .filter(Boolean)
    );
  }

  /**
   * Create the enhanced input
   */
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

    this.button = document.createElement("button");
    this.button.type = "button";
    this.button.className = "tna-button";
    this.button.title = "Add";
    this.button.setAttribute("aria-label", "Add");
    this.button.innerHTML = "Add";

    const wrapper = document.createElement("div");
    wrapper.className = "tna-search-field";
    wrapper.append(this.input, this.button);

    this.textarea.hidden = true;
    this.textarea.parentElement.appendChild(wrapper);

    this.list = document.createElement("ul");
    this.list.className = "tna-compound-filters tna-!--margin-top-xs";
    this.list.setAttribute("role", "list");
    this.textarea.parentElement.appendChild(this.list);

    this.liveRegion = document.createElement("div");
    this.liveRegion.className = "tna-visually-hidden";
    this.liveRegion.setAttribute("aria-live", "polite");
    this.textarea.parentElement.appendChild(this.liveRegion);

    if (hint) {
      const customHint = this.textarea.dataset.jsChipHint;
      hint.textContent = customHint || "Add terms separately by pressing Enter";
    }
  }

  /**
   * Sync the textarea value with the values set
   */
  syncTextarea() {
    this.textarea.value = Array.from(this.values).join("\n");
  }

  /**
   * Announce a message to the user
   * @param {string} message The message to announce
   */
  announce(message) {
    this.liveRegion.textContent = "";
    requestAnimationFrame(() => {
      this.liveRegion.textContent = message;
    });
  }

  /**
   * Render a chip
   * @param {string} value The value to render
   */
  renderChip(value) {
    const li = document.createElement("li");
    li.className = "tna-compound-filters__item";
    li.dataset.value = value;
    li.setAttribute("role", "listitem");

    const label = document.createElement("span");
    label.textContent = value;

    const removeLink = document.createElement("a");
    removeLink.href = "#";
    removeLink.className = "tna-compound-filters__link";
    removeLink.dataset.value = value;
    removeLink.setAttribute("aria-label", `Remove ${value}`);

    li.append(label, removeLink);
    this.list.appendChild(li);
  }

  /**
   * Render all the chips
   */
  renderAll() {
    this.list.innerHTML = "";
    this.values.forEach(v => this.renderChip(v));
  }

  /**
   * Add a value to the field
   * @param {string} rawValue The raw value to add
   */
  addValue(rawValue) {
    const value = rawValue.trim();
    if (!value || this.values.has(value)) return;

    this.values.add(value);
    this.syncTextarea();
    this.renderChip(value);
    this.announce(`Added ${value}`);
    this.input.value = "";
    this.dispatchChange();
  }

  /**
   * Remove a value from the field
   * @param {string} value The value to remove
   */
  removeValue(value) {
    if (!this.values.has(value)) return;

    this.values.delete(value);
    this.syncTextarea();

    const chip = this.list.querySelector(
      `li[data-value="${CSS.escape(value)}"]`
    );
    chip?.remove();

    this.announce(`Removed ${value}`);
    this.dispatchChange();
  }

  dispatchChange() {
    this.textarea.dispatchEvent(new CustomEvent("chipchange", {
      bubbles: true,
      detail: { values: Array.from(this.values) }
    }));
  }

  /**
   * Bind the events to the input and list
   */
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

    this.button.addEventListener("click", () => {
      this.addValue(this.input.value);
      this.input.focus();
    });

    this.list.addEventListener("click", (e) => {
      const link = e.target.closest(".tna-compound-filters__link");
      if (!link) return;
      e.preventDefault();
      this.removeValue(link.dataset.value);
    });

    /**
     * Reset the field and chips when the form is reset
     */
    const form = this.textarea.closest("form");
    if (form) {
      form.addEventListener("reset", () => {
        this.values.clear();
        this.list.innerHTML = "";
      });
    }
  }
}

/**
 * Initialize the chip fields
 */
document.querySelectorAll("[data-js-chip-field]").forEach(textarea => {
  new ChipField(textarea);
});
