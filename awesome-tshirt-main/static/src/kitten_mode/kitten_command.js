import { registry } from "@web/core/registry";

const commandProviderRegistry = registry.category("command_provider");

commandProviderRegistry.add("Kitten", {
  provide: (env, option) => {
    const result = [];
    const { active, enable, disable } = env.services.kitten;
    if (active) {
      result.push({
        action: disable,
        category: "kitten",
        name: env._t("Disable kitten mode"),
      });
    } else {
      result.push({
        action: enable,
        category: "kitten",
        name: env._t("Activate kitten mode"),
      });
    }
    return result;
  },
});