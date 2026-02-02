import { Cookies } from "@nationalarchives/frontend/nationalarchives/all.mjs";
import { Accordion } from "./etna-accordion.mjs";

class toggleDetailsListDescriptions {
  constructor(checkbox, detailsList, cookies) {
    this.cookies = cookies;

    this.checkbox = checkbox;
    this.formItem = this.checkbox.closest(".tna-form-item");

    this.detailsList = detailsList;
    this.detailsListItems = this.detailsList.querySelectorAll(
      ".record-details__description",
    );

    if (this.detailsListItems.length === 0) {
      return;
    }

    if (this.formItem) {
      this.showFormItem();
    }

    this.setUpCheckbox();
  }

  showFormItem() {
    this.formItem.removeAttribute("hidden");
    this.formItem
      .querySelector(".tna-form__legend")
      ?.classList.add("tna-visually-hidden");
  }

  setUpCheckbox() {
    this.checkbox?.addEventListener("change", (event) =>
      this.handleCheckboxChange(event.target.checked),
    );

    if (
      this.cookies.isPolicyAccepted("settings") &&
      this.cookies.exists("hide_record_detail_descriptions")
    ) {
      this.checkbox.checked = this.cookies.hasValue(
        "hide_record_detail_descriptions",
        "true",
      );
    }

    this.handleCheckboxChange(this.checkbox.checked);
  }

  handleCheckboxChange(hide) {
    for (const item of this.detailsListItems) {
      if (hide) {
        item.setAttribute("hidden", "");
      } else {
        item.removeAttribute("hidden");
      }
    }

    if (this.cookies.isPolicyAccepted("settings")) {
      this.cookies.set("hide_record_detail_descriptions", hide);
    }
  }
}

const cookies = new Cookies();

const checkbox = document.getElementById("field-descriptions");
const detailsList = document.getElementById("record-details-list");
if (checkbox && detailsList) {
  new toggleDetailsListDescriptions(checkbox, detailsList, cookies);
}

const youtubeLink = document.getElementById("youtube-link");
if (
  youtubeLink &&
  youtubeLink.dataset.youtubeVideoId &&
  cookies.isPolicyAccepted("marketing")
) {
  const embededPlayer = document.createElement("iframe");
  embededPlayer.id = "youtube-embeded-player";
  embededPlayer.setAttribute("width", "100%");
  embededPlayer.setAttribute("height", "400");
  embededPlayer.setAttribute(
    "src",
    `https://www.youtube.com/embed/${youtubeLink.dataset.youtubeVideoId}`,
  );
  embededPlayer.setAttribute("title", "Video: The records we hold");
  embededPlayer.setAttribute("frameborder", "0");
  embededPlayer.setAttribute(
    "allow",
    "accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; web-share",
  );
  embededPlayer.setAttribute(
    "referrerpolicy",
    "strict-origin-when-cross-origin",
  );
  embededPlayer.setAttribute("allowfullscreen", "true");
  embededPlayer.classList.add("tna-!--margin-top-m");
  youtubeLink.replaceWith(embededPlayer);
}

const $accordions = document.querySelectorAll('[data-module="etna-accordion"]');

$accordions.forEach(($accordion) => {
  new Accordion($accordion);
});

// dataLayer push for 'View this record' : goes to discovery
document.addEventListener("DOMContentLoaded", () => {
  const discoveryLinkButton = document.querySelector(".discovery-link");

  if (discoveryLinkButton) {
    discoveryLinkButton.addEventListener("click", () => {
      window.dataLayer = window.dataLayer || [];
      window.dataLayer.push({
        event: "select_promotion",
        promotion_name: "Ordering and viewing options",
        creative_name: "Ordering and viewing options:link",
        creative_slot: "Full description and record details",
      });
    });
  }
});

// ============================================================================
// PROGRESSIVE LOADING FOR RECORD DETAIL PAGES
// ============================================================================

// Load configuration from the page
function loadProgressiveConfig() {
  const configElement = document.getElementById("progressive-loading-config");
  if (!configElement) return null;

  try {
    return JSON.parse(configElement.textContent);
  } catch (e) {
    console.error("Progressive loading: Failed to parse config:", e);
    return null;
  }
}

// Load subjects enrichment (Wagtail related content)
async function loadSubjectsEnrichment(config) {
  const container = document.getElementById("related-content-container");
  if (!container) return;

  try {
    const response = await fetch(config.endpoints.subjects);
    const data = await response.json();

    if (data.success && data.has_content) {
      container.innerHTML = data.html;
      container.classList.remove("progressive-loading");
      container.removeAttribute("aria-busy");
    } else {
      container.remove();
    }
  } catch (error) {
    console.error(
      "Progressive loading: Failed to load subjects enrichment:",
      error,
    );
    showProgressiveError(container, "Failed to load related content");
  }
}

// Load related records
async function loadRelatedRecords(config) {
  const container = document.getElementById("related-records-container");
  if (!container) return;

  try {
    const response = await fetch(config.endpoints.related);
    const data = await response.json();

    if (data.success && data.has_content) {
      container.innerHTML = data.html;
      container.classList.remove("progressive-loading");
      container.removeAttribute("aria-busy");
    } else {
      container.remove();
    }
  } catch (error) {
    console.error(
      "Progressive loading: Failed to load related records:",
      error,
    );
    showProgressiveError(container, "Failed to load related records");
  }
}

// Load delivery options (updates 3 sections)
async function loadDeliveryOptions(config) {
  try {
    const response = await fetch(config.endpoints.delivery);
    const data = await response.json();

    if (data.success && data.has_content) {
      // Update "Available online" section
      updateProgressiveSection(
        "available-online-container",
        data.sections.available_online,
      );

      // Update "Available in person" section
      updateProgressiveSection(
        "available-in-person-container",
        data.sections.available_in_person,
      );

      // Add "How to order" to accordion if available
      if (data.sections.how_to_order) {
        addDeliveryAccordionItem(
          data.sections.how_to_order_title,
          data.sections.how_to_order,
        );
      }

      // Update analytics metadata
      if (data.analytics) {
        updateProgressiveAnalytics(data.analytics);
      }

      adjustContentWarningPadding();
    } else {
      hideDeliveryPlaceholders();
    }
  } catch (error) {
    console.error(
      "Progressive loading: Failed to load delivery options:",
      error,
    );
    hideDeliveryPlaceholders();
  }
}

// Update a section by replacing its container
function updateProgressiveSection(containerId, html) {
  const container = document.getElementById(containerId);
  if (!container) return;
  container.outerHTML = html;
}

// Add delivery options accordion item
function addDeliveryAccordionItem(title, bodyHtml) {
  const accordion = document.querySelector(
    '.etna-accordion[data-module="etna-accordion"]',
  );
  if (!accordion) return;

  const item = document.createElement("div");
  item.className = "etna-accordion__item";
  item.setAttribute("data-isopen", "false");

  const itemIndex = 1;

  item.innerHTML = `
    <h3 class="etna-accordion__heading" id="record-extended-details-heading-${itemIndex}">
      ${title}
    </h3>
    <div class="etna-accordion__body" id="record-extended-details-content-${itemIndex}">
      ${bodyHtml}
    </div>
  `;

  accordion.insertBefore(item, accordion.firstChild);

  // Reinitialize accordion
  new Accordion(accordion);
}

// Update analytics meta tags
function updateProgressiveAnalytics(analytics) {
  const metaTags = {
    delivery_option_category: analytics.delivery_option_category,
    delivery_option: analytics.delivery_option,
  };

  Object.entries(metaTags).forEach(([key, value]) => {
    const meta = document.querySelector(`meta[name="tna_root:${key}"]`);
    if (meta) {
      meta.setAttribute("content", value);
    }
  });
}

// Adjust padding if content warning is shown
function adjustContentWarningPadding() {
  const warningContainer = document.getElementById("content-warning-container");
  if (warningContainer && warningContainer.querySelector(".tna-warning")) {
    const section = document.querySelector(".tna-section");
    if (section) {
      section.classList.remove("tna-!--padding-top-l");
      section.classList.add("tna-!--padding-top-s");
    }
  }
}

// Hide delivery option placeholders
function hideDeliveryPlaceholders() {
  const onlineContainer = document.getElementById("available-online-container");
  const inPersonContainer = document.getElementById(
    "available-in-person-container",
  );
  const accordionPlaceholder = document.getElementById(
    "delivery-options-accordion-placeholder",
  );

  if (onlineContainer) onlineContainer.remove();
  if (inPersonContainer) inPersonContainer.remove();
  if (accordionPlaceholder) accordionPlaceholder.remove();
}

// Show error message in container
function showProgressiveError(container, message) {
  if (!container) return;

  container.innerHTML = `
    <div class="tna-container">
      <div class="tna-aside tna-aside--warning">
        <p>${message}. Please refresh the page to try again.</p>
      </div>
    </div>
  `;
  container.classList.remove("progressive-loading");
  container.removeAttribute("aria-busy");
}

// Initialize progressive loading
function initProgressiveLoading() {
  console.log("Progressive loading: Initializing...");

  const config = loadProgressiveConfig();
  if (!config) {
    console.log(
      "Progressive loading: No config found (not a record detail page)",
    );
    return;
  }

  console.log(
    "Progressive loading: Config loaded, starting to load sections...",
  );

  // Load all sections in parallel
  loadSubjectsEnrichment(config);
  loadRelatedRecords(config);

  if (config.shouldLoadDelivery) {
    loadDeliveryOptions(config);
  } else {
    hideDeliveryPlaceholders();
  }
}

// Run progressive loading when DOM is ready
(function () {
  console.log("Progressive loading: IIFE starting...");

  function init() {
    console.log(
      "Progressive loading: init() called, readyState:",
      document.readyState,
    );

    const config = loadProgressiveConfig();
    if (!config) {
      console.log(
        "Progressive loading: No config found (not a record detail page)",
      );
      return;
    }

    console.log(
      "Progressive loading: Config loaded, starting to load sections...",
    );

    // Load all sections in parallel
    loadSubjectsEnrichment(config);
    loadRelatedRecords(config);

    if (config.shouldLoadDelivery) {
      loadDeliveryOptions(config);
    } else {
      hideDeliveryPlaceholders();
    }
  }

  if (document.readyState === "loading") {
    console.log(
      "Progressive loading: DOM still loading, adding event listener",
    );
    document.addEventListener("DOMContentLoaded", init);
  } else {
    console.log("Progressive loading: DOM already loaded, running immediately");
    init();
  }
})();
