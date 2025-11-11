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

const $mobileFiltersButton = document.getElementById("mobile-filters");
const $mobileFiltersButtonText = document.getElementById("mobile-filters-text");
const $visibleAsideElements = document.getElementsByClassName("tna-aside");
if (
  $mobileFiltersButton &&
  $mobileFiltersButtonText &&
  $visibleAsideElements.length
) {
  const showEventFiltersButton = () => {
    $mobileFiltersButton.style.display = "block";
  };

  const hideEventFiltersButton = () => {
    $mobileFiltersButton.style.display = "none";
  };

  const displayFilters = () => {
    for (let i = 0; i < $visibleAsideElements.length; i++) {
      $visibleAsideElements[i].style.display = "block";
    }
    $mobileFiltersButtonText.textContent = "Hide filters";
  };

  const hideFilters = () => {
    for (let i = 0; i < $visibleAsideElements.length; i++) {
      $visibleAsideElements[i].style.display = "none";
    }
    $mobileFiltersButtonText.textContent = "Show filters";
  };

  $mobileFiltersButton.addEventListener("click", () => {
    if ($mobileFiltersButtonText.textContent === "Show filters") {
      displayFilters();
    } else {
      hideFilters();
    }
  });

  const isMobile = window.matchMedia("(max-width: 48em)");
  isMobile.onchange = (e) => {
    if (e.matches) {
      showEventFiltersButton();
      hideFilters();
    } else {
      hideEventFiltersButton();
      displayFilters();
    }
  };

  if (isMobile.matches) {
    hideFilters();
  } else {
    displayFilters();
  }
}
