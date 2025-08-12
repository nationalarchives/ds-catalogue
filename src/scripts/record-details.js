import { Cookies } from "@nationalarchives/frontend/nationalarchives/all.mjs";
import { Accordion } from "./etna-accordion.mjs";

class toggleDetailsListDescriptions {
  constructor(checkbox, detailsList, cookies) {
    this.cookies = cookies;

    this.checkbox = checkbox;
    this.formGroup = this.checkbox.closest(".tna-form__group");

    this.detailsList = detailsList;
    this.detailsListItems = this.detailsList.querySelectorAll(
      ".record-details__description",
    );

    if (this.detailsListItems.length === 0) {
      return;
    }

    if (this.formGroup) {
      this.showFormGroup();
    }

    this.setUpCheckbox();
  }

  showFormGroup() {
    this.formGroup.removeAttribute("hidden");
    this.formGroup
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

const checkbox = document.getElementById("field-descriptions-hide");
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
