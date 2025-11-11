const $searchForm = document.getElementById("search-form");
const $sortFormGroup = document.getElementById("sort-form-group");
const $sort = document.getElementById("sort");
if ($searchForm && $sortFormGroup && $sort) {
  $sortFormGroup.parentElement
    .querySelector(".tna-button-group")
    ?.setAttribute("hidden", "");
  $sort.addEventListener("change", () => {
    $searchForm.submit();
  });
}

// search filters for mobile version
const $mobileFiltersButton = document.getElementById("mobile-filters");
const $mobileFiltersButtonText = document.getElementById("mobile-filters-text");
const $visibleAsideElements = document.getElementsByClassName("tna-aside");
if (
  $mobileFiltersButton &&
  $mobileFiltersButtonText &&
  $visibleAsideElements.length
) {
  // mobile view
  const showEventFilters = () => {
    // console.log('mobile view');
    $mobileFiltersButton.style.display = "block";
    // $visibleAsideElements.style.display = "none";
  };

  // desktop view
  const hideEventFilters = () => {
    // console.log('desktop view');
    $mobileFiltersButton.style.display = "none";
  };

  const isMobile = window.matchMedia("(max-width: 48em)");
  isMobile.onchange = (e) => {
    if (e.matches) {
      showEventFilters();
    }
  };

  const isDesktop = window.matchMedia("(min-width: 48em)");
  isDesktop.onchange = (e) => {
    if (e.matches) {
      hideEventFilters();
    }
  };

  $mobileFiltersButtonText.textContent = "Show filters";

  $mobileFiltersButton.onclick = function () {
    if ($mobileFiltersButtonText.textContent === "Show filters") {
      // If the button says "Add Filters", change it to "Hide Filters" and show the aside elements
      $mobileFiltersButtonText.textContent = "Hide filters";
      for (let i = 0; i < $visibleAsideElements.length; i++) {
        $visibleAsideElements[i].style.display = "block";
      }
    } else {
      // If the button says "Hide Filters", change it to "Add Filters" and hide the aside elements
      $mobileFiltersButtonText.textContent = "Show filters";
      for (let i = 0; i < $visibleAsideElements.length; i++) {
        $visibleAsideElements[i].style.display = "none"; // Changed to 'none' to hide
      }
    }
  };

  // resizing of window

  const displayDesktopFilters = () => {
    // console.log('show desktop filter');
    for (let i = 0; i < $visibleAsideElements.length; i++) {
      $visibleAsideElements[i].style.display = "block";
    }
  };

  const displayMobilefilters = () => {
    // console.log("show mobile filter");
    for (let i = 0; i < $visibleAsideElements.length; i++) {
      $visibleAsideElements[i].style.display = "none";
    }
  };

  window.addEventListener("resize", () => {
    // console.log(window.innerWidth);
    if (window.innerWidth > 400) {
      displayDesktopFilters();
    }
    if (window.innerWidth < 400) {
      displayMobilefilters();
    }
  });
}
