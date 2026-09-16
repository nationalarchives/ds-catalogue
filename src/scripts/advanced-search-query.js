/* eslint-disable max-lines */
const INDEX_FIRST = 0,
  MIN_PARENS_LENGTH = 2,
  PARSE_RADIX = 10;

class AdvancedSearchPreview {
  constructor() {
    this.initElements();
    if (!this.searchPreview || !this.searchPreviewQuery) {
      return;
    }

    this.bindEvents();
    this.update();
  }

  initElements() {
    this.searchPreview = document.querySelector("[data-js-search-preview]");
    this.searchPreviewQuery = document.querySelector(
      "[data-js-search-preview-query]",
    );

    this.allWordsInput = document.getElementById("id_all_words");
    this.exactWords = document.getElementById("id_exact_words");
    this.anyWords = document.getElementById("id_any_words");
    this.ignoreWords = document.getElementById("id_ignore_words");
    this.references = document.getElementById("id_references");
  }

  static getChipValues(textarea) {
    if (!textarea) {
      return [];
    }
    return textarea.value
      .split("\n")
      .map((value) => value.trim())
      .filter(Boolean);
  }

  bindEvents() {
    this.addInputListeners();

    document.addEventListener("chipchange", () => this.update());

    const form = this.searchPreview.closest("form");
    if (form) {
      this.attachFormHandlers(form);
    }
  }

  addInputListeners() {
    const inputs = [
      this.allWordsInput,
      this.exactWords,
      this.anyWords,
      this.ignoreWords,
      this.references,
    ];
    inputs.forEach((el) => {
      if (el) {
        el.addEventListener("input", () => this.update());
      }
    });
  }

  attachFormHandlers(form) {
    form.addEventListener("reset", () => {
      requestAnimationFrame(() => this.update());
    });
    form.addEventListener("submit", (ev) => {
      // Prevent submit if any textarea exceeds configured limits
      const textareas = [
        this.exactWords,
        this.anyWords,
        this.ignoreWords,
        this.references,
      ];
      const invalid = textareas.some((ta) =>
        AdvancedSearchPreview.isOverLimit(ta),
      );
      if (invalid) {
        ev.preventDefault();
        const first = textareas.find((ta) =>
          AdvancedSearchPreview.isOverLimit(ta),
        );
        if (first) {
          first.focus();
        }
      }
    });
  }

  static isOverLimit(textarea) {
    if (!textarea) {
      return false;
    }
    const maxChars =
      parseInt(
        textarea.getAttribute("maxlength") || String(INDEX_FIRST),
        PARSE_RADIX,
      ) || INDEX_FIRST;
    const maxLines =
      parseInt(
        textarea.getAttribute("data-max-lines") || String(INDEX_FIRST),
        PARSE_RADIX,
      ) || INDEX_FIRST;
    const { chars, lines } = AdvancedSearchPreview.getCounts(textarea);
    if (maxChars && chars > maxChars) {
      return true;
    }
    if (maxLines && lines > maxLines) {
      return true;
    }
    return false;
  }

  static getCounts(textarea) {
    const chars = textarea.value.length;
    const lines = textarea.value
      .split("\n")
      .map((line) => line.trim())
      .filter(Boolean).length;
    return { chars, lines };
  }

  static getMaxValues(textarea) {
    const maxChars =
      parseInt(
        textarea.getAttribute("maxlength") || String(INDEX_FIRST),
        PARSE_RADIX,
      ) || INDEX_FIRST;
    const maxLines =
      parseInt(
        textarea.getAttribute("data-max-lines") || String(INDEX_FIRST),
        PARSE_RADIX,
      ) || INDEX_FIRST;
    return { maxChars, maxLines };
  }

  static addGroup(
    parts,
    terms,
    { prefix = null, joiner = "OR", wrap = true } = {},
  ) {
    if (terms.length === INDEX_FIRST) {
      return;
    }
    const showParens = wrap && terms.length >= MIN_PARENS_LENGTH;
    if (prefix) {
      parts.push({ type: "operator", value: prefix });
    }
    if (showParens) {
      parts.push({ type: "paren", value: "(" });
    }
    terms.forEach((term, index) => {
      if (index > INDEX_FIRST) {
        parts.push({ type: "operator", value: joiner });
      }
      parts.push({ type: "term", value: term });
    });
    if (showParens) {
      parts.push({ type: "paren", value: ")" });
    }
  }

  buildQuery() {
    const parts = [];
    this.pushAllWords(parts);
    this.pushExactWords(parts);
    this.pushAnyWords(parts);
    this.pushIgnoreWords(parts);
    this.pushReferenceWords(parts);
    return parts;
  }
  pushAllWords(parts) {
    const allWords = this.allWordsInput?.value.trim();
    if (allWords) {
      parts.push({ type: "term", value: allWords });
    }
  }

  pushExactWords(parts) {
    let prefixForExact = null;
    if (parts.length > INDEX_FIRST) {
      prefixForExact = "AND";
    }
    AdvancedSearchPreview.addGroup(
      parts,
      AdvancedSearchPreview.getChipValues(this.exactWords),
      {
        prefix: prefixForExact,
        joiner: "AND",
        wrap: false,
      },
    );
  }

  pushAnyWords(parts) {
    let prefixForAny = null;
    if (parts.length > INDEX_FIRST) {
      prefixForAny = "AND";
    }
    AdvancedSearchPreview.addGroup(
      parts,
      AdvancedSearchPreview.getChipValues(this.anyWords),
      {
        prefix: prefixForAny,
        joiner: "OR",
        wrap: true,
      },
    );
  }

  pushIgnoreWords(parts) {
    AdvancedSearchPreview.addGroup(
      parts,
      AdvancedSearchPreview.getChipValues(this.ignoreWords),
      {
        prefix: "NOT",
        joiner: "OR",
        wrap: true,
      },
    );
  }

  pushReferenceWords(parts) {
    AdvancedSearchPreview.addGroup(
      parts,
      AdvancedSearchPreview.getChipValues(this.references),
      {
        prefix: "IN",
        joiner: "OR",
        wrap: true,
      },
    );
  }

  update() {
    const parts = this.buildQuery();

    if (parts.length === INDEX_FIRST) {
      this.searchPreview.hidden = true;
      return;
    }

    this.searchPreviewQuery.innerHTML = "";
    parts.forEach((part) => this.renderPart(part));
    this.searchPreview.hidden = false;
    // update counters for monitored textareas
    [this.exactWords, this.anyWords, this.ignoreWords, this.references].forEach(
      (ta) => AdvancedSearchPreview.updateCounters(ta),
    );
  }

  static formatSuffix(maxValue) {
    if (maxValue) {
      return `/${maxValue}`;
    }
    return "";
  }

  static setCounterText(counter, { chars, lines, charSuffix, lineSuffix }) {
    const charEl = counter.querySelector(".char-count");
    const lineEl = counter.querySelector(".line-count");
    if (charEl) {
      charEl.textContent = `${chars}${charSuffix}`;
    }
    if (lineEl) {
      lineEl.textContent = `${lines}${lineSuffix}`;
    }
  }

  static buildMessages({ maxChars, maxLines, chars, lines }) {
    const msgs = [];
    if (maxChars && chars > maxChars) {
      msgs.push(`Maximum ${maxChars} characters`);
    }
    if (maxLines && lines > maxLines) {
      msgs.push(`Maximum ${maxLines} lines`);
    }
    return msgs;
  }

  static setErrorState(textarea, errorEl, msgs) {
    if (msgs.length) {
      textarea.classList.add("textarea--error");
      if (errorEl) {
        errorEl.textContent = msgs.join(". ");
        errorEl.hidden = false;
      }
    } else {
      textarea.classList.remove("textarea--error");
      if (errorEl) {
        errorEl.textContent = "";
        errorEl.hidden = true;
      }
    }
  }

  static updateCounters(textarea) {
    if (!textarea) {
      return;
    }
    const { maxChars, maxLines } = AdvancedSearchPreview.getMaxValues(textarea);
    const { chars, lines } = AdvancedSearchPreview.getCounts(textarea);
    const counter = document.querySelector(
      `[data-counter-for="${textarea.id}"]`,
    );
    if (counter) {
      AdvancedSearchPreview.setCounterText(counter, {
        chars,
        lines,
        charSuffix: AdvancedSearchPreview.formatSuffix(maxChars),
        lineSuffix: AdvancedSearchPreview.formatSuffix(maxLines),
      });
    }
    const errorEl = document.querySelector(`[data-error-for="${textarea.id}"]`);
    const msgs = AdvancedSearchPreview.buildMessages({
      maxChars,
      maxLines,
      chars,
      lines,
    });
    AdvancedSearchPreview.setErrorState(textarea, errorEl, msgs);
  }

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
        if (part.value === "(") {
          el.textContent = " ( ";
        } else {
          el.textContent = " ) ";
        }
        break;
      default:
        // Unknown part type; render as plain text to avoid breaking the preview.
        el.className = "search-preview__unknown";
        el.textContent = String(part.value || "");
        break;
    }
    this.searchPreviewQuery.appendChild(el);
  }
}

window.advancedSearchPreview = new AdvancedSearchPreview();
