class SubjectPicker {
  constructor() {
    this.tabsContainer = document.querySelector('.subject-picker-list');
    this.tabsItems = [...this.tabsContainer.querySelectorAll('.subject-picker-list__button')];
    this.tabsContent = document.querySelectorAll('.subject-picker-content');
    this.selectedTabIndex = 0;

    this.init();
  }

  /**
   * Hide all content and remove focus from all tabs
   */
  hideAllTabs() {
    this.tabsItems.forEach((item) => {
      item.removeAttribute('aria-selected');
      item.setAttribute('tabindex', '-1');
    });

    this.tabsContent.forEach((content) => {
      content.setAttribute('hidden', '');
    });
  }

  /**
   * Select the current tab and show the corresponding content
   * @param {boolean} setFocus - Whether to set focus to the selected tab
   */
  selectTab(setFocus = false) {
    this.hideAllTabs();

    const selectedTab = this.tabsItems[this.selectedTabIndex];

    const selectedContentId = selectedTab.getAttribute('aria-controls');
    const selectedContent = document.getElementById(selectedContentId);

    selectedTab.setAttribute('aria-selected', 'true');
    selectedTab.removeAttribute('tabindex');
    selectedContent?.removeAttribute('hidden');

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
    const clamp = (index, max) => Math.max(0, Math.min(max, index));
    const step = (delta) => (index, max) => clamp(index + delta, max);

    const keyActions = {
      ArrowRight: step(1),
      ArrowDown: step(1),
      ArrowLeft: step(-1),
      ArrowUp: step(-1),
      Home: () => 0,
      End: (_, max) => max,
    };

    this.tabsContainer.addEventListener('keydown', (event) => {
      const getNextIndex = keyActions[event.key];
      if (!getNextIndex) return;

      event.preventDefault();

      const maxIndex = this.tabsItems.length - 1;
      const nextIndex = getNextIndex(this.selectedTabIndex, maxIndex);

      if (nextIndex === this.selectedTabIndex) return;

      this.selectedTabIndex = nextIndex;
      this.selectTab(true);
    });
  }

  /**
   * Set up click navigation for the subject picker
   */
  setupClickNavigation() {
    this.tabsItems.forEach((item) => {
      item.addEventListener('click', () => {
        this.selectedTabIndex = this.getTabIndex(item);
        this.selectTab();
      });
    });
  }

  /**
   * Initialize the subject picker
   */
  init() {
    this.tabsContainer.removeAttribute('hidden');
    this.selectTab();
    this.setupKeyboardNavigation();
    this.setupClickNavigation();
  }
}

const tabs = new SubjectPicker(document.querySelector('.subject-picker'));
