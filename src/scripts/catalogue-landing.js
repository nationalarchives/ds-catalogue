const FIRST_TAB_INDEX = 0;
const TAB_INDEX_STEP = 1;

class SubjectPicker {
  constructor() {
    this.tabsContainer = document.querySelector(".subject-picker-list");
    this.tabsItems = [
      ...this.tabsContainer.querySelectorAll(".subject-picker-list__button"),
    ];
    this.tabsContent = document.querySelectorAll(".subject-picker-content");
    this.selectedTabIndex = FIRST_TAB_INDEX;

    this.init();
  }

  /**
   * Hide all content and remove focus from all tabs
   */
  hideAllTabs() {
    this.tabsItems.forEach((item) => {
      item.setAttribute("aria-selected", "false");
      item.setAttribute("tabindex", "-1");
    });

    this.tabsContent.forEach((content) => {
      content.setAttribute("hidden", "");
    });
  }

  /**
   * Select the current tab and show the corresponding content
   * @param {boolean} setFocus - Whether to set focus to the selected tab
   */
  selectTab(setFocus = false) {
    this.hideAllTabs();

    const selectedTab = this.tabsItems[this.selectedTabIndex];

    const selectedContentId = selectedTab.getAttribute("aria-controls");
    const selectedContent = document.getElementById(selectedContentId);

    selectedTab.setAttribute("aria-selected", "true");
    selectedTab.removeAttribute("tabindex");
    selectedContent?.removeAttribute("hidden");

    if (setFocus) {
      selectedTab.focus();
    }
  }

  /**
   * Get the index of the given tab item
   * @param {HTMLElement} item - The tab item to get the index of
   * @returns {number} The index of the given tab item
   */
  getTabIndex(item) {
    return this.tabsItems.indexOf(item);
  }

  /**
   * Set up keyboard navigation for arrow key controls
   */
  setupKeyboardNavigation() {
    const clamp = (index, max) =>
      Math.max(FIRST_TAB_INDEX, Math.min(max, index));

    const getNextIndex = (key, index, max) => {
      switch (key) {
        case "ArrowRight":
        case "ArrowDown":
          return clamp(index + TAB_INDEX_STEP, max);
        case "ArrowLeft":
        case "ArrowUp":
          return clamp(index - TAB_INDEX_STEP, max);
        case "Home":
          return FIRST_TAB_INDEX;
        case "End":
          return max;
        default:
          return null;
      }
    };

    this.tabsContainer.addEventListener("keydown", (event) => {
      const maxIndex = this.tabsItems.length - TAB_INDEX_STEP;
      const nextIndex = getNextIndex(
        event.key,
        this.selectedTabIndex,
        maxIndex,
      );

      if (nextIndex === null) {
        return;
      }

      event.preventDefault();

      if (nextIndex === this.selectedTabIndex) {
        return;
      }

      this.selectedTabIndex = nextIndex;
      this.selectTab(true);
    });
  }

  /**
   * Set up click navigation for the subject picker
   */
  setupClickNavigation() {
    this.tabsItems.forEach((item) => {
      item.addEventListener("click", () => {
        this.selectedTabIndex = this.getTabIndex(item);
        this.selectTab();
      });
    });
  }

  /**
   * Initialize the subject picker
   */
  init() {
    this.tabsContainer.removeAttribute("hidden");
    this.selectTab();
    this.setupKeyboardNavigation();
    this.setupClickNavigation();
  }
}

// eslint-disable-next-line no-new
new SubjectPicker();
