from odoo import fields, models


class ProjectPhase(models.Model):
    _name = "project.phase"

    name = fields.Char(string="Phase", required=True)


class ProjectType(models.Model):
    _name = "project.type"

    name = fields.Char(string="Type", required=True)


class ProjectRate(models.Model):
    _name = "project.rate"

    name = fields.Char(string="Rate To Use", required=True)


class ProjectEntity(models.Model):
    _name = "project.entity"

    name = fields.Char(string="Entity", required=True)


class DecisionType(models.Model):
    """Decision Type"""
    _name = "decision.type"

    name = fields.Char("Decision Type", required=True)


class DecisionMade(models.Model):
    """Decision Type"""
    _name = "decision.made"

    name = fields.Char("Decision Made At", required=True)


class DocumentRequired(models.Model):
    """Decision Type"""
    _name = "document.required"

    name = fields.Char("Document Required", required=True)
