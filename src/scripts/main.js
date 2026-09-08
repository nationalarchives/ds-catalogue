import Cookies from "@nationalarchives/cookies";
import { initAll } from "@nationalarchives/frontend/nationalarchives/all.mjs";

initAll();

const cookies = new Cookies();

/**
 * BELOW COPIED FROM https://github.com/nationalarchives/ds-frontend/blob/main/src/scripts/main.js
 */
const initNotifications = () => {
  const initialDismissedNotifications = JSON.parse(
    cookies.get("dismissed_notifications") || "[]",
  );
  document
    .querySelectorAll(
      ".etna-global-alert:has(.etna-global-alert__dismiss[value][hidden])",
    )
    .forEach(($globalAlert) => {
      const $alertDismissButton = $globalAlert.querySelector(
        ".etna-global-alert__dismiss",
      );
      // eslint-disable-next-line radix
      const alertUid = parseInt($alertDismissButton.value);
      if (initialDismissedNotifications.includes(alertUid)) {
        $globalAlert.hidden = true;
      } else {
        $alertDismissButton.hidden = false;
        $alertDismissButton.addEventListener("click", () => {
          const dismissedNotifications = JSON.parse(
            cookies.get("dismissed_notifications") || "[]",
          );
          const dismissedNotificationsSet = new Set(dismissedNotifications);
          // eslint-disable-next-line radix
          dismissedNotificationsSet.add(parseInt(alertUid));
          cookies.set(
            "dismissed_notifications",
            JSON.stringify(Array.from(dismissedNotificationsSet)),
            { session: true },
          );
          const $globalAlertWrapper = $globalAlert.closest(
            ".etna-global-alert-wrapper",
          );
          $globalAlert.remove();
          if (
            !$globalAlertWrapper.querySelector(
              ".etna-global-alert, .etna-mourning-notice",
            )
          ) {
            $globalAlertWrapper.remove();
          }
        });
      }
    });
};

if (cookies.preference("settings")) {
  initNotifications();
} else {
  cookies.once("changePreference", (policies) => {
    if (policies.settings) {
      initNotifications();
    }
  });
}
