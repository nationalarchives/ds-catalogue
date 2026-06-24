import { Accordion } from "./etna-accordion.mjs";

// ============================================================================
// PROGRESSIVE LOADING FOR RECORD DETAIL PAGES
// ============================================================================

const logError = (message, error) => {
  // eslint-disable-next-line no-console
  console.error(message, error);
};

// Read the progressive-loading config embedded in the page.
const loadProgressiveConfig = () => {
  const configElement = document.getElementById("progressive-loading-config");
  if (!configElement) {
    return null;
  }
  try {
    return JSON.parse(configElement.textContent);
  } catch (error) {
    logError("Progressive loading: Failed to parse config:", error);
    return null;
  }
};

// Swap server-rendered HTML into a container, or remove it if empty.
const swapOrRemove = (container, data) => {
  if (data.success && data.has_content) {
    container.outerHTML = data.html;
  } else {
    container.remove();
  }
};

// Fetch server-rendered HTML and apply it to a container, removing the
// container if there is nothing to show.
const replaceContainerFromEndpoint = async (containerId, endpoint, label) => {
  const container = document.getElementById(containerId);
  if (!container) {
    return;
  }
  try {
    const response = await fetch(endpoint);
    const data = await response.json();
    swapOrRemove(container, data);
  } catch (error) {
    logError(`Progressive loading: Failed to load ${label}:`, error);
    container.remove();
  }
};

const loadSubjectsEnrichment = (config) =>
  replaceContainerFromEndpoint(
    "related-content-container",
    config.endpoints.subjects,
    "subjects enrichment",
  );

const loadRelatedRecords = (config) =>
  replaceContainerFromEndpoint(
    "related-records-container",
    config.endpoints.related,
    "related records",
  );

// Replace a section container with server-rendered HTML.
const updateProgressiveSection = (containerId, html) => {
  const container = document.getElementById(containerId);
  if (!container) {
    return;
  }
  container.outerHTML = html;
};

// Prepend a "How to order" item to the extended-details accordion.
const addDeliveryAccordionItem = (title, bodyHtml) => {
  const accordion = document.querySelector(
    "#record-extended-details .etna-accordion",
  );
  if (!accordion) {
    return;
  }

  const item = document.createElement("div");
  item.className = "etna-accordion__item";
  item.setAttribute("data-isopen", "false");
  item.innerHTML = `
    <h3 class="etna-accordion__heading" id="record-extended-details-progressive-heading-1">
      ${title}
    </h3>
    <div class="etna-accordion__body" id="record-extended-details-progressive-content-1">
      ${bodyHtml}
    </div>
  `;

  accordion.insertBefore(item, accordion.firstChild);

  // eslint-disable-next-line no-new
  new Accordion(accordion);
};

// Update the analytics meta tags from the delivery response.
const updateProgressiveAnalytics = (analytics) => {
  const fields = ["delivery_option_category", "delivery_option"];
  fields.forEach((field) => {
    const meta = document.querySelector(`meta[name="tna_root:${field}"]`);
    if (meta) {
      meta.setAttribute("content", analytics[field]);
    }
  });
};

const showDeliveryError = (onlineContainer, inPersonContainer) => {
  onlineContainer.outerHTML = `
    <div class="tna-column tna-column--width-2-3 tna-column--full-small tna-column--full-tiny tna-!--margin-top-m">
      <div class="tna-aside tna-aside--tight tna-background-contrast full-height-aside">
        <h2 class="tna-heading-m">Access information is unavailable</h2>
        <p>Sorry, information for accessing this record is currently unavailable online. Please try again later.</p>
      </div>
    </div>
  `;
  if (inPersonContainer) {
    inPersonContainer.remove();
  }
};

const removeIfPresent = (element) => {
  if (element) {
    element.remove();
  }
};

// Hide the delivery placeholders, optionally swapping in an error message.
const hideDeliveryPlaceholders = (showError = false) => {
  const onlineContainer = document.getElementById("available-online-container");
  const inPersonContainer = document.getElementById(
    "available-in-person-container",
  );
  const accordionPlaceholder = document.getElementById(
    "delivery-options-accordion-placeholder",
  );

  if (showError && onlineContainer) {
    showDeliveryError(onlineContainer, inPersonContainer);
  } else {
    removeIfPresent(onlineContainer);
    removeIfPresent(inPersonContainer);
  }
  removeIfPresent(accordionPlaceholder);
};

// Apply a successful delivery-options response to the page.
const applyDeliveryData = (data) => {
  updateProgressiveSection(
    "available-online-container",
    data.sections.available_online,
  );
  updateProgressiveSection(
    "available-in-person-container",
    data.sections.available_in_person,
  );
  if (data.sections.how_to_order) {
    addDeliveryAccordionItem(
      data.sections.how_to_order_title,
      data.sections.how_to_order,
    );
  }
  if (data.analytics) {
    updateProgressiveAnalytics(data.analytics);
  }
};

const loadDeliveryOptions = async (config) => {
  try {
    const response = await fetch(config.endpoints.delivery);
    const data = await response.json();
    const isValid =
      data.success &&
      data.has_content &&
      data.analytics?.delivery_option_category;
    if (isValid) {
      applyDeliveryData(data);
    } else {
      hideDeliveryPlaceholders(true);
    }
  } catch (error) {
    logError("Progressive loading: Failed to load delivery options:", error);
    hideDeliveryPlaceholders(true);
  }
};

// Entry point: load every progressive section for a record detail page.
export const initProgressiveLoading = () => {
  const config = loadProgressiveConfig();
  if (!config) {
    // Not a record detail page with progressive loading config.
    return;
  }

  loadSubjectsEnrichment(config);
  loadRelatedRecords(config);

  if (config.shouldLoadDelivery) {
    loadDeliveryOptions(config);
  } else {
    hideDeliveryPlaceholders();
  }
};
