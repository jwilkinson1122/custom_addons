/** @odoo-module **/

import { registry } from "@web/core/registry";

function executeCloseAndRefreshView({ env, action }) {
  const actionService = env.services.action;
  const originalAction = action._originalAction;

  console.log("Executing close and refresh view action...");
  console.log("Action details:", action);
  console.log("Original action:", originalAction);

  return actionService
    .doAction(
      { type: "ir.actions.act_window_close" },
      {
        onClose: function () {
          console.log("Wizard closed successfully.");
          if (originalAction) {
            console.log("Executing original action to refresh the view...");
            actionService.doAction(originalAction);
          } else {
            console.warn("No original action found to refresh the view.");
          }
        },
      }
    )
    .catch((error) => {
      console.error(
        "Error while executing close and refresh view action:",
        error
      );
    });
}

registry
  .category("action_handlers")
  .add("ir.actions.close_wizard_refresh_view", executeCloseAndRefreshView);

// function executeCloseAndRefreshView({ env, action }) {
//   const actionService = env.services.action;
//   const originalAction = action._originalAction;

//   return actionService.doAction(
//     { type: "ir.actions.act_window_close" },
//     {
//       onClose: function () {
//         if (originalAction) {
//           actionService.doAction(originalAction);
//         }
//       },
//     }
//   );
// }

// registry
//   .category("action_handlers")
//   .add("ir.actions.close_wizard_refresh_view", executeCloseAndRefreshView);
