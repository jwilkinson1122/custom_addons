# -*- coding: utf-8 -*-
import json
import logging
from odoo import api, models

_logger = logging.getLogger(__name__)

class CpqConditionUtils(models.AbstractModel):
    _name = "cpq.condition.utils"
    _description = "CPQ Condition Evaluator Utilities"

    @api.model
    def evaluate_condition_json(self, condition_json, context_data):
        """
        Evaluates a JSON logic block against a dictionary of context data.
        Example condition_json: {"quantity_to_make": {"gte": 2}, "laterality": "bilateral"}
        """
        try:
            if not condition_json:
                return True  # No condition means always valid

            condition = json.loads(condition_json)

            def match_rule(key, expected):
                actual = context_data.get(key)
                if isinstance(expected, dict):
                    for op, val in expected.items():
                        if op == "eq" and actual != val:
                            return False
                        if op == "neq" and actual == val:
                            return False
                        if op == "gte" and not (actual >= val):
                            return False
                        if op == "lte" and not (actual <= val):
                            return False
                        if op == "gt" and not (actual > val):
                            return False
                        if op == "lt" and not (actual < val):
                            return False
                else:
                    if actual != expected:
                        return False
                return True

            return all(match_rule(k, v) for k, v in condition.items())

        except Exception as e:
            _logger.exception("Error evaluating condition JSON: %s", condition_json)
            return False

    @api.model
    def get_active_nonproduct_notes(self, partner_id, context_data=None):
        """
        Returns a list of notes from cpq.rules.nonproduct that match the partner hierarchy and pass any condition.
        """
        context_data = context_data or {}
        partner = self.env['res.partner'].browse(partner_id)
        partners = partner.mapped('commercial_partner_id') | partner

        rules = self.env['cpq.rules.nonproduct'].search([
            ('partner_id', 'in', partners.ids),
            ('active', '=', True),
        ])

        matched_notes = []
        for rule in rules:
            if self.evaluate_condition_json(rule.condition_json, context_data):
                matched_notes.append(rule.note)

        return matched_notes

    @api.model
    def get_active_order_notes(self, partner_id, context_data=None):
        """
        Returns a list of notes from cpq.rules.order.note that match the partner hierarchy and pass any condition.
        """
        context_data = context_data or {}
        partner = self.env['res.partner'].browse(partner_id)
        partners = partner.mapped('commercial_partner_id') | partner

        rules = self.env['cpq.rules.order.note'].search([
            ('partner_id', 'in', partners.ids),
            ('active', '=', True),
        ])

        matched_notes = []
        for rule in rules:
            if self.evaluate_condition_json(rule.condition_json, context_data):
                matched_notes.append(rule.note)

        return matched_notes

    @api.model
    def get_active_logic_rules(self, partner_id, context_data=None):
        """
        Returns a list of logic rules (as dict) from cpq.rules.logic that match the partner hierarchy and pass any condition.
        """
        context_data = context_data or {}
        partner = self.env['res.partner'].browse(partner_id)
        partners = partner.mapped('commercial_partner_id') | partner

        rules = self.env['cpq.rules.logic'].search([
            ('partner_id', 'in', partners.ids),
            ('active', '=', True),
        ])

        matched_logic = []
        for rule in rules:
            if self.evaluate_condition_json(rule.condition_json, context_data):
                matched_logic.append({
                    "note": rule.note,
                    "condition": rule.condition_json,
                    "attribute_id": rule.attribute_id.id,
                    "value_id": rule.value_id.id if rule.value_id else None,
                })

        return matched_logic

