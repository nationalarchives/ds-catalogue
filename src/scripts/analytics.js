import {
  GA4,
  helpers,
} from "@nationalarchives/frontend/nationalarchives/analytics.mjs";

const ga4Id = document.documentElement.getAttribute("data-ga4id");
if (ga4Id) {
  const analytics = new GA4({ id: ga4Id });

  analytics.addListeners(document.documentElement, "document", [
    {
      eventName: "double_click",
      on: "dblclick",
      data: {
        // eslint-disable-next-line no-unused-vars
        state: ($el, $scope, event, index) => helpers.getXPathTo(event.target),
        // eslint-disable-next-line no-unused-vars
        value: ($el, $scope, event, index) => event.target.innerHTML,
      },
    },
  ]);

  analytics.addListeners(
    "#field-descriptions",
    "field_descriptions",
    [
      {
        targetElement: "#field-descriptions-hide",
        on: "change",
        data: {
          state: helpers.valueGetters.checked,
          value: ($el) => $el.parentNode.innerText.trim(),
          group: ($el, $scope) =>
            $scope
              .closest(".tna-form__group")
              ?.querySelector(".tna-form__heading")
              ?.innerText?.trim(),
        },
        rootData: {
          data_component_name: "checkboxes",
          data_link: ($el) =>
            `Hide field descriptions:${helpers.valueGetters.checked($el)}`,
          data_section: "Record details",
          data_link_type: "checkboxes",
          data_position: 1,
        },
      },
    ],
    "select_feature",
  );
}
