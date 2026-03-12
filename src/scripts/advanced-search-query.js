class AdvancedSearchPreview {
  constructor() {
    this.searchPreview = document.querySelector("[data-js-search-preview]");
    this.searchPreviewQuery = document.querySelector("[data-js-search-preview-query]");
    if (!this.searchPreview || !this.searchPreviewQuery) return;

    this.allWordsInput = document.getElementById("all_words");
    this.exactWords = document.getElementById("exact_words");
    this.anyWords = document.getElementById("any_words");
    this.ignoreWords = document.getElementById("ignore_words");
    this.references = document.getElementById("references");

    this.bindEvents();
    this.update();
  }

  /**
   * Get the values from the textarea
   * @param {HTMLTextAreaElement} textarea - The textarea element
   * @returns {string[]} The values from the textarea
   */
  getChipValues(textarea) {
    if (!textarea) return [];
    return textarea.value
      .split("\n")
      .map(v => v.trim())
      .filter(Boolean);
  }

  /**
   * Bind the events to the elements
   */
  bindEvents() {
    if (this.allWordsInput) {
      this.allWordsInput.addEventListener("input", () => this.update());
    }

    document.addEventListener("chipchange", () => this.update());

    const form = this.searchPreview.closest("form");
    if (form) {
      form.addEventListener("reset", () => {
        requestAnimationFrame(() => this.update());
      });
    }
  }

  /**
   * Append a group of terms to the query parts array.
   * @param {Array} parts - The parts array to append to
   * @param {string[]} terms - The terms to add
   * @param {Object} options
   * @param {string|null} options.prefix - Operator to prepend (e.g. "AND", "NOT", "IN")
   * @param {string} options.joiner - Operator between terms (default "OR")
   * @param {boolean} options.wrap - Whether to wrap in parentheses (default true)
   */
  addGroup(parts, terms, { prefix = null, joiner = "OR", wrap = true } = {}) {
    if (terms.length === 0) return;
    const showParens = wrap && terms.length > 1;
    if (prefix) parts.push({ type: "operator", value: prefix });
    if (showParens) parts.push({ type: "paren", value: "(" });
    terms.forEach((term, i) => {
      if (i > 0) parts.push({ type: "operator", value: joiner });
      parts.push({ type: "term", value: term });
    });
    if (showParens) parts.push({ type: "paren", value: ")" });
  }

  /**
   * Build the query
   * @returns {Array} The query parts
   */
  buildQuery() {
    const parts = [];
    const allWords = this.allWordsInput?.value.trim();

    if (allWords) {
      parts.push({ type: "term", value: allWords });
    }

    this.addGroup(parts, this.getChipValues(this.exactWords), {
      prefix: parts.length > 0 ? "AND" : null,
      joiner: "AND",
      wrap: false,
    });

    this.addGroup(parts, this.getChipValues(this.anyWords), {
      prefix: parts.length > 0 ? "AND" : null,
      joiner: "OR",
      wrap: true,
    });

    this.addGroup(parts, this.getChipValues(this.ignoreWords), {
      prefix: "NOT",
      joiner: "OR",
      wrap: true,
    });

    this.addGroup(parts, this.getChipValues(this.references), {
      prefix: "IN",
      joiner: "OR",
      wrap: true,
    });

    return parts;
  }

  /**
   * Update the search preview
   */
  update() {
    const parts = this.buildQuery();

    if (parts.length === 0) {
      this.searchPreview.hidden = true;
      return;
    }

    this.searchPreviewQuery.innerHTML = "";
    parts.forEach(part => this.renderPart(part));
    this.searchPreview.hidden = false;
  }

  /**
   * Render a part of the query
   * @param {Object} part - The part to render
   */
  renderPart(part) {
    const el = document.createElement("span");
    switch (part.type) {
      case "term":
        el.className = "search-preview__term";
        el.textContent = part.value;
        break;
      case "operator":
        el.className = "search-preview__operator";
        el.textContent = ` ${part.value} `;
        break;
      case "paren":
        el.className = "search-preview__paren";
        el.textContent = part.value === "(" ? " ( " : " ) ";
        break;
    }
    this.searchPreviewQuery.appendChild(el);
  }
}

new AdvancedSearchPreview();
