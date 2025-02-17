/** @odoo-module **/

import { Avatar } from "@mail/views/web/fields/avatar/avatar";
import { HierarchyRenderer } from "@web_hierarchy/hierarchy_renderer";
import { ResPartnerHierarchyCard } from "./res_partner_hierarchy_card";

export class ResPartnerHierarchyRenderer extends HierarchyRenderer {
    static template = "partner_affiliate.ResPartnerHierarchyRenderer";
    static components = {
        ...HierarchyRenderer.components,
        HierarchyCard: ResPartnerHierarchyCard,
        Avatar,
    };
}
