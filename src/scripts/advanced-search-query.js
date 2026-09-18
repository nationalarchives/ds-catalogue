const DEBOUNCE_DELAY_MS = 150;

class AdvancedSearchPreview {
  constructor() {
    this.initElements();
    if (!this.searchPreview || !this.searchPreviewQuery || !this.form) {
      return;
    }

    this.debounceTimeout = null;
    this.requestId = 0;

    this.bindEvents();
    this.update();
  }

  /**
   * Cache the preview, form, endpoint and query-building form fields.
   */
  initElements() {
    this.searchPreview = document.querySelector("[data-js-search-preview]");
    this.searchPreviewQuery = document.querySelector(
      "[data-js-search-preview-query]",
    );
    this.form = this.searchPreview?.closest("form");
    this.previewUrl = this.searchPreview?.dataset.jsSearchPreviewUrl;

    this.allWordsInput = document.getElementById("id_all_words");
    this.exactWords = document.getElementById("id_exact_words");
    this.anyWords = document.getElementById("id_any_words");
    this.ignoreWords = document.getElementById("id_ignore_words");
  }

  /**
    * Bind updates to field changes, chip changes and form resets.
   */
  bindEvents() {
    [this.allWordsInput, this.exactWords, this.anyWords, this.ignoreWords]
      .filter(Boolean)
      .forEach((input) => {
        input.addEventListener("input", () => this.scheduleUpdate());
      });

    document.addEventListener("chipchange", () => this.scheduleUpdate());

    this.form.addEventListener("reset", () => {
      requestAnimationFrame(() => this.update());
    });
  }

  /**
   * Debounce preview updates so typing does not call the API on every keypress.
   */
  scheduleUpdate() {
    clearTimeout(this.debounceTimeout);
    this.debounceTimeout = setTimeout(() => this.update(), DEBOUNCE_DELAY_MS);
  }

  /**
   * Build the POST payload using the current form values.
   */
  buildFormData() {
    const formData = new FormData(this.form);

    if (this.allWordsInput) {
      formData.set(this.allWordsInput.name, this.allWordsInput.value);
    }
    [this.exactWords, this.anyWords, this.ignoreWords].forEach((input) => {
      if (input) {
        formData.set(input.name, input.value);
      }
    });

    return formData;
  }

  /**
   * Render the structured query parts returned by the backend.
   */
  renderQuery(parts) {
    if (!parts.length) {
      this.searchPreview.hidden = true;
      return;
    }

    this.searchPreviewQuery.innerHTML = "";
    parts.forEach((part) => this.renderPart(part));
    this.searchPreview.hidden = false;
  }

  /**
    * Render one query part with the existing preview styling classes.
   * @param {Object} part - The part to render
   */
  renderPart(part) {
    const { type, value } = part;
    const el = document.createElement("span");
    switch (type) {
      case "term":
        el.className = "search-preview__term";
        el.textContent = value;
        break;
      case "operator":
        el.className = "search-preview__operator";
        el.textContent = ` ${value} `;
        break;
      case "paren":
        el.className = "search-preview__paren";
        if (value === "(") {
          el.textContent = " ( ";
        } else {
          el.textContent = " ) ";
        }
        break;
      default:
        el.textContent = String(value || "");
        break;
    }
    this.searchPreviewQuery.appendChild(el);
  }

  /**
    * Start a fresh preview request and ignore failures for stale requests.
   */
  async update() {
    const currentRequestId = this.nextRequestId();

    try {
      await this.renderResponse(currentRequestId);
    } catch {
      if (currentRequestId === this.requestId) {
        this.searchPreview.hidden = true;
      }
    }
  }

  /**
   * Return the ID for the latest preview request.
   */
  nextRequestId() {
    this.requestId += 1;
    return this.requestId;
  }

  /**
   * Fetch the backend-built query preview and render it if it is still current.
   */
  async renderResponse(currentRequestId) {
    const response = await fetch(this.previewUrl, {
      method: "POST",
      body: this.buildFormData(),
      credentials: "same-origin",
    });

    if (!response.ok || currentRequestId !== this.requestId) {
      return;
    }

    const data = await response.json();
    if (currentRequestId === this.requestId) {
      this.renderQuery(data.parts || []);
    }
  }
}

window.advancedSearchPreview = new AdvancedSearchPreview();
