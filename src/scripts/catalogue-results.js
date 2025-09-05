const $searchForm = document.getElementById("search-form");
const $sortFormGroup = document.getElementById("sort-form-group");
const $sort = document.getElementById("sort");
$sortFormGroup.parentElement
  .querySelector(".tna-button-group")
  ?.setAttribute("hidden", "");
$sort.addEventListener("change", () => {
  $searchForm.submit();
});

// search filters for mobile version
const $mobileFiltersButton = document.getElementById("mobile-filters");
const $visibleAsideElements = document.getElementsByClassName("tna-aside");

$mobileFiltersButton.textContent = "Add Filters";

$mobileFiltersButton.onclick = function () {
  if ($mobileFiltersButton.textContent === "Add Filters") {
    // If the button says "Add Filters", change it to "Hide Filters" and show the aside elements
    $mobileFiltersButton.textContent = "Hide Filters";
    for (let i = 0; i < $visibleAsideElements.length; i++) {
      $visibleAsideElements[i].style.display = "block";
    }
  } else {
    // If the button says "Hide Filters", change it to "Add Filters" and hide the aside elements
    $mobileFiltersButton.textContent = "Add Filters";
    for (let i = 0; i < $visibleAsideElements.length; i++) {
      $visibleAsideElements[i].style.display = "none"; // Changed to 'none' to hide
    }
  }
};
