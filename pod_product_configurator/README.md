#Odoo Product Configurator

This module is Dynamic configuration wizard for Odoo back-end and the foundation for
external configuration interfaces such 'website_product_configurator'.

By itself this module does not configure custom products but offers the basis for
generating, validating, updating configurable products using configuration interfaces.

# Usage

This module is Dynamic configuration wizard for Odoo back-end and the foundation for
external configuration interfaces such 'website_product_configurator'.

By itself this module does not configure custom products but offers the basis for
generating, validating, updating configurable products using configuration interfaces.


# Requirements / Features

- Inhibition of automatically created variants.
- Extension of attribute lines to offer required, custom and multiple selection.
- Configuration / Compatibility rules between attributes.
- Separation of attributes in different steps.
- Configuration of attributes based on laterality (left/right/both).
- Images for intermediate and final configurations.
- Managing active configuration sessions for external configurators
- Set of helper methods required for any Odoo configuration module.

1️⃣ Product Configuration Process

✔ Step-Based Configurator Wizard:

Users should navigate between steps in a structured manner.
Configurable options should appear dynamically based on previous selections.

✔ Dynamic Attribute Handling:

Attributes should be filtered dynamically based on laterality and other selections.
Unnecessary attributes should be hidden if irrelevant to the selected laterality.

✔ Preset & Historical Configurations:

Ability to save configurations as templates.
Ability to apply past configurations automatically.

2️⃣ Laterality Selection & Configuration

✔ Laterality Options:

Left Only 🦶
Right Only 🦶
Bilateral (Both Left & Right) 👣

✔ Configuration Rules:

Left Only → Configurations apply only to the left foot.
Right Only → Configurations apply only to the right foot.
Bilateral → Configurations apply independently to each foot.

✔ Laterality-Dependent UI/Behavior:

Grid-style UI for bilateral configurations.
Ability to customize left and right sides separately.
Option to copy one side’s configuration to the other.
Comparison view to highlight differences between left and right.
Preservation of past configurations to auto-fill based on history.

✔ Laterality Price Adjustments:

Different pricing rules should apply per foot.
Dynamic price breakdown should be shown in the sales order.
Comparison UI for price changes before finalizing an order.

3️⃣ Sales Order Integration

✔ Sale Order Line Customization:

Each product line must store laterality configurations separately.
Order summary should display left and right foot configurations distinctly.

✔ Laterality-Based Pricing Rules:

The system should calculate pricing based on laterality.
A pricing breakdown per foot should be available.
Custom price adjustments should be applied based on selected configurations.

✔ Session & Order Synchronization:

Each sales order should have a linked configuration session.
The session should be retrieved or created dynamically.
Unconfirmed sessions should not be deleted, but should reset when required.

✔ BOM & Manufacturing Support:

The configurator should generate the correct Bill of Materials (BOM).
Configured products should be linked to the correct manufacturing workflow.

4️⃣ UI & User Experience Enhancements

✔ Configurator UI Features:

Dynamic Forms: Attribute fields should appear based on selected laterality.
Pre-filled Attributes: Previously used configurations should be suggested for reuse.
Attribute Dependency Handling: Only valid attributes should be selectable.

Comparison Screens:

Left vs Right configuration differences.

Pricing change previews.

✔ Session Management & Navigation:

Users should be able to:

Reset configurations while keeping session data.
Navigate back to previous steps in the configurator.
Review differences before finalizing configurations.

✔ Preventing Data Loss & Errors:

Ensure configurations persist across steps.
Preserve laterality settings if the user revisits the configurator.
Prevent duplicate sessions unless explicitly needed.


🚀 Potential Additions/Enhancements & Future Considerations
🔹 Multi-Laterality Presets: Save & reapply asymmetrical configurations.
🔹 Bulk Configuration Updates: Allow multiple products to inherit past settings.
🔹 Error Handling & Logging: Provide detailed logs & error messages for debugging.
🔹 Improved UX/UI: Streamline configurator experience with intuitive controls.