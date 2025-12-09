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

// Use a standard event listener pattern to ensure code runs after the DOM is loaded
document.addEventListener("DOMContentLoaded", () => {
  // Select the button element using the class name 'discovery-link'
  const discoveryLinkButton = document.querySelector(".discovery-link");

  // 2. Check if the button was found
  if (discoveryLinkButton) {
    // 3. Attach the event listener for the 'click' event
    discoveryLinkButton.addEventListener("click", () => {
      // Prevent the default action (though a button has no default action here,
      // this is good practice for links/forms)
      // event.preventDefault();

      // 4. push to the dataLayer
      window.dataLayer = window.dataLayer || [];

      window.dataLayer.push({
        event: "select_promotion",
        promotion_name: "Ordering and viewing options",
        creative_name: "Ordering and viewing options:link",
        creative_slot: "Full description and record details",
      });
    });

    // console.log("Successfully attached click listener to '.discovery-link'.");
  } else {
    // console.error("Error: Could not find element with class 'discovery-link'.");
  }
});

/**
 * Progressive loading handler for record detail pages
 * 
 * Loads secondary content (delivery options, related records, subjects enrichment)
 * asynchronously after the primary record data is displayed.
 * 
 * For users without JavaScript, <noscript> tags in the template provide full content.
 */

(function() {
  'use strict';

  // Check if this page supports progressive loading
  const progressiveMeta = document.querySelector('meta[name="progressive-load"]');
  if (!progressiveMeta) {
    // Not a progressive load page, exit early
    return;
  }

  /**
   * Load a fragment via AJAX and replace the placeholder
   * 
   * @param {HTMLElement} container - The container element with data-endpoint attribute
   */
  function loadFragment(container) {
    const endpoint = container.dataset.endpoint;
    const fragmentType = container.dataset.fragmentType;

    if (!endpoint) {
      console.error('No endpoint specified for fragment', container);
      return;
    }

    // Make the container visible (was hidden by default)
    container.style.display = '';
    container.classList.remove('progressive-fragment-hidden');

    fetch(endpoint, {
      headers: {
        'X-Requested-With': 'XMLHttpRequest'
      }
    })
    .then(response => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }
      return response.text();
    })
    .then(html => {
      // Handle different fragment types
      if (fragmentType === 'accordion-item') {
        // For accordion items, insert into the accordion
        insertAccordionItem(container, html);
      } else if (fragmentType === 'block') {
        // For blocks, replace the entire container content
        container.innerHTML = html;
        container.classList.remove('progressive-fragment');
      } else if (fragmentType === 'unwrap') {
        // For unwrap type, insert children as siblings and remove container
        const temp = document.createElement('div');
        temp.innerHTML = html;
        
        // Insert each child element as a sibling before the container
        while (temp.firstElementChild) {
          container.parentNode.insertBefore(temp.firstElementChild, container);
        }
        
        // Remove the now-empty container
        container.remove();
      }
    })
    .catch(error => {
      console.error('Failed to load fragment:', error);
      
      // Show error message to user
      container.innerHTML = `
        <div class="tna-message tna-message--error" role="alert">
          <p>We couldn't load this content. Please <a href="${window.location.href}">refresh the page</a> to try again.</p>
        </div>
      `;
    });
  }

  /**
   * Insert an accordion item into the accordion component
   * 
   * @param {HTMLElement} container - The placeholder container
   * @param {string} html - The HTML content to insert
   */
  function insertAccordionItem(container, html) {
    const accordion = document.getElementById('record-extended-details');
    if (!accordion) {
      console.error('Accordion not found');
      container.remove();
      return;
    }

    // Find the accordion container (TNA Design System uses specific classes)
    const accordionContainer = accordion.querySelector('.tna-accordion');
    if (!accordionContainer) {
      console.error('Accordion container not found');
      container.remove();
      return;
    }

    // Parse the HTML fragment
    const temp = document.createElement('div');
    temp.innerHTML = html;
    
    // Get the accordion item
    const item = temp.querySelector('.tna-accordion__item');
    if (item) {
      // Insert as first item (before series info and hierarchy)
      const firstItem = accordionContainer.firstElementChild;
      if (firstItem) {
        accordionContainer.insertBefore(item, firstItem);
      } else {
        accordionContainer.appendChild(item);
      }
      
      // Re-initialize accordion functionality if needed
      initializeAccordionItem(item);
    }
    
    // Remove the placeholder
    container.remove();
  }

  /**
   * Initialize accordion functionality for a newly added item
   * Uses TNA Design System accordion pattern
   * 
   * @param {HTMLElement} item - The accordion item element
   */
  function initializeAccordionItem(item) {
    const button = item.querySelector('.tna-accordion__button');
    const body = item.querySelector('.tna-accordion__body');
    
    if (!button || !body) {
      return;
    }

    // Set up click handler
    button.addEventListener('click', function() {
      const isExpanded = button.getAttribute('aria-expanded') === 'true';
      
      // Toggle this item
      button.setAttribute('aria-expanded', !isExpanded);
      
      // Add/remove active class for styling
      if (!isExpanded) {
        item.classList.add('tna-accordion__item--active');
      } else {
        item.classList.remove('tna-accordion__item--active');
      }
    });

    // Set initial state (collapsed)
    button.setAttribute('aria-expanded', 'false');
    item.classList.remove('tna-accordion__item--active');
  }

  /**
   * Initialize progressive loading for all fragments
   */
  function initProgressiveLoading() {
    const fragments = document.querySelectorAll('.progressive-fragment[data-endpoint]');
    
    if (fragments.length === 0) {
      return;
    }

    // Load all fragments in parallel
    // The browser will handle the concurrent requests efficiently
    fragments.forEach(fragment => {
      loadFragment(fragment);
    });
  }

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initProgressiveLoading);
  } else {
    // DOM already loaded
    initProgressiveLoading();
  }

})();