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
        // eslint-disable-next-line no-unused-vars, max-params
        state: ($el, $scope, event, index) => helpers.getXPathTo(event.target),

        // eslint-disable-next-line no-unused-vars, max-params
        value: ($el, $scope, event, index) => event.target.innerHTML,
      },
    },
  ]);

  analytics.addListeners(
    "#field-descriptions-container",
    "field_descriptions",
    [
      {
        targetElement: "#field-descriptions",
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
          // eslint-disable-next-line camelcase
          data_component_name: "checkboxes",
          // eslint-disable-next-line camelcase
          data_link: ($el) =>
            `Hide field descriptions:${helpers.valueGetters.checked($el)}`,
          // eslint-disable-next-line camelcase
          data_section: "Record details",
          // eslint-disable-next-line camelcase
          data_link_type: "checkboxes",
          // eslint-disable-next-line camelcase
          data_position: 1,
        },
      },
    ],
    "select_feature",
  );
}
