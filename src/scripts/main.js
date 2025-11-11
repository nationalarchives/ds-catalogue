import {
  initAll,
  Cookies,
} from "@nationalarchives/frontend/nationalarchives/all.mjs";

let cookies;

const cookiesDomain =
  document.documentElement.getAttribute("data-cookiesdomain");
if (cookiesDomain) {
  cookies = new Cookies({ domain: cookiesDomain });
} else {
  cookies = new Cookies();
}

initAll();

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

if (cookies.isPolicyAccepted("settings")) {
  initNotifications();
} else {
  cookies.once("changePolicy", (policies) => {
    if (policies["settings"]) {
      initNotifications();
    }
  });
}
