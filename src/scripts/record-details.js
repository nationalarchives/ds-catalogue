import { Cookies } from "@nationalarchives/frontend/nationalarchives/all.mjs";
import { Accordion } from "./etna-accordion.mjs";

// Set js_enabled cookie so server knows JS is available on subsequent requests
document.cookie = "js_enabled=true; path=/; SameSite=Lax";

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

// Swap from server-rendered content to progressive loading containers
function swapToProgressiveLoading() {
  // Hide server-rendered content
  document.querySelectorAll(".js-progressive-server-content").forEach((el) => {
    el.setAttribute("hidden", "");
  });

  // Show progressive loading containers
  document.querySelectorAll(".js-progressive-loading").forEach((el) => {
    el.removeAttribute("hidden");
  });
}

// Load subjects enrichment (Wagtail related content)
async function loadSubjectsEnrichment(config) {
  const container = document.getElementById("related-content-container");
  if (!container) return;

  try {
    const response = await fetch(config.endpoints.subjects);
    const data = await response.json();

    if (data.success && data.has_content) {
      container.outerHTML = data.html;
    } else {
      container.remove();
    }
  } catch (error) {
    console.error(
      "Progressive loading: Failed to load subjects enrichment:",
      error,
    );
    container.remove();
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
      container.outerHTML = data.html;
    } else {
      container.remove();
    }
  } catch (error) {
    console.error(
      "Progressive loading: Failed to load related records:",
      error,
    );
    container.remove();
  }
}

// Load delivery options (updates multiple sections)
async function loadDeliveryOptions(config) {
  try {
    const response = await fetch(config.endpoints.delivery);
    const data = await response.json();

    if (
      data.success &&
      data.has_content &&
      data.analytics?.delivery_option_category
    ) {
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
    } else {
      // No valid delivery data - show error message
      hideDeliveryPlaceholders(true);
    }
  } catch (error) {
    console.error(
      "Progressive loading: Failed to load delivery options:",
      error,
    );
    hideDeliveryPlaceholders(true);
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
    "#accordion-progressive .etna-accordion",
  );
  if (!accordion) return;

  const item = document.createElement("div");
  item.className = "etna-accordion__item";
  item.setAttribute("data-isopen", "false");

  const itemIndex = 1;

  item.innerHTML = `
    <h3 class="etna-accordion__heading" id="record-extended-details-progressive-heading-${itemIndex}">
      ${title}
    </h3>
    <div class="etna-accordion__body" id="record-extended-details-progressive-content-${itemIndex}">
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

// Hide delivery option placeholders and optionally show error message
function hideDeliveryPlaceholders(showError = false) {
  const onlineContainer = document.getElementById("available-online-container");
  const inPersonContainer = document.getElementById(
    "available-in-person-container",
  );
  const accordionPlaceholder = document.getElementById(
    "delivery-options-accordion-placeholder",
  );

  if (showError && onlineContainer) {
    // Replace both containers with the error message
    const errorHtml = `
      <div class="tna-column tna-column--width-2-3 tna-column--full-small tna-column--full-tiny tna-!--margin-top-m">
        <div class="tna-aside tna-aside--tight tna-background-contrast full-height-aside">
          <h2 class="tna-heading-m">Access information is unavailable</h2>
          <p>Sorry, information for accessing this record is currently unavailable online. Please try again later.</p>
        </div>
      </div>
    `;
    onlineContainer.outerHTML = errorHtml;
    if (inPersonContainer) inPersonContainer.remove();
  } else {
    if (onlineContainer) onlineContainer.remove();
    if (inPersonContainer) inPersonContainer.remove();
  }

  if (accordionPlaceholder) accordionPlaceholder.remove();
}

// Run progressive loading when DOM is ready
(function () {
  function init() {
    const config = loadProgressiveConfig();
    if (!config) {
      // Not a record detail page with progressive loading config
      return;
    }

    // Swap server-rendered content for progressive loading containers
    swapToProgressiveLoading();

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
    document.addEventListener("DOMContentLoaded", init);
  } else {
    init();
  }
})();
