# -*- coding: utf-8 -*-


from odoo import models, fields, api
import random
import math
from odoo.exceptions import ValidationError
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

noms_humans = ["Alaric", "Aric", "Cedric", "Eleanor", "Elara", "Gareth", "Isabella", "Isolde", "Lorna", "Lyra",
               "Roland", "Rowan", "Seraphina", "Theron"]
cognoms_humans = ["Dawnblade", "Flamecaster", "Frostheart", "Ironhammer", "Lightbringer", "Silverhand", "Stormforge",
                  "Stormwatcher", "Swiftwind", "Thunderstrike"]

noms_orcos = ["Durotan", "Garrosh", "Grommash", "Grok", "Gul'dan", "Hellscream", "Kargath", "Kilrogg", "Makar",
              "Nazgrim", "Orgrim", "Saurfang", "Thrall", "Zugor"]
cognoms_orcos = ["Blackhand", "Bloodfury", "Doomhammer", "Frostwolf", "Gorehowl", "Hellscream", "Makar", "Rend",
                 "Skullcrusher", "Stonefist", "Thunderlord", "Warsong", "Wolfheart", "Zugor"]


def name_human_generator():
    random.shuffle(noms_humans)
    random.shuffle(cognoms_humans)
    return f"{noms_humans[0]} {cognoms_humans[0]}"


def name_orcs_generator():
    random.shuffle(noms_orcos)
    random.shuffle(cognoms_orcos)
    return f"{noms_orcos[0]} {cognoms_orcos[0]}"


class Player(models.Model):
    _name = 'res.partner'  # HERENCIA EN EL MODELO
    _inherit = "res.partner"
    _description = 'warcraft player'  # HERENCIA EN EL MODELO

    is_player = fields.Boolean(default="False")
    name = fields.Char(required=True)
    avatar = fields.Image(max_width=200, max_height=200)
    hero = fields.One2many('warcraft.hero', 'player')
    townhalls = fields.Many2many('warcraft.townhall', compute='get_townhalls')

    def get_townhalls(self):
        for p in self:
            p.townhalls = p.hero.townhall


class Hero(models.Model):
    _name = 'warcraft.hero'
    _description = 'Human hero'

    RACE_SELECTION = [('orc', 'Heroe orco'),
                      ('human', 'Heroe humano')]

    avatar = fields.Image(max_width=200, max_height=200)
    name = fields.Char('Name', compute='compute_hero_name', store=True)
    level = fields.Integer(default=1)
    race = fields.Selection(RACE_SELECTION, string='Race', required=True)
    player = fields.Many2one('res.partner', string="Player")
    experience = fields.Float(default='0')
    health = fields.Float(default='100')
    townhall = fields.Many2one('warcraft.townhall', string="Townhall")

    @api.depends('race')
    def compute_hero_name(self):
        for hero in self:
            if hero.race == 'orc':
                hero.name = name_orcs_generator()
            elif hero.race == 'human':
                hero.name = name_human_generator()


class Townhall(models.Model):
    _name = 'warcraft.townhall'
    _description = 'Townhall'

    name = fields.Char(string='Nombre', required=True)
    hero = fields.One2many('warcraft.hero', 'townhall', string="Heroes")
    units = fields.One2many('warcraft.unit', 'townhall', string="Units")
    level = fields.Selection([('1', 'TownHall'), ('2', 'Fortress'), ('3', 'Citadel')], required=True, default='1')
    building = fields.One2many('warcraft.building', 'townhall')
    farm_level = fields.Integer()
    mine_level = fields.Integer()
    sawmill_level = fields.Integer()
    available_buildings = fields.Many2many('warcraft.building_type', compute='compute_available_buildings')

    townhall_attack = fields.One2many('warcraft.battle', 'townhall1')
    townhall_defense = fields.One2many('warcraft.battle', 'townhall2')
    battles = fields.Many2many('warcraft.battle', compute='_battles')

    gold = fields.Float(default=500)
    wood = fields.Float(default=500)
    food = fields.Integer(default=100)

    def compute_available_buildings(self):
        for townhall in self:
            townhall.available_buildings = self.env['warcraft.building_type'].search([]).filtered(
                lambda building_type: building_type.gold_price <= townhall.gold).ids

    def update_resources(self):
        for c in self.search([]):
            wood = c.wood
            gold = c.gold
            food = c.food
            for b in c.building.filtered(lambda b: b.level >= 1):
                wood += b.wood_production
                gold += b.gold_production
                food += b.food_production
            c.write({"gold": gold, "wood": wood, "food": food})

    def _battles(self):
        for townhall in self:
            townhall.battles = townhall.townhall_attack + townhall.townhall_defense


class BuildingType(models.Model):
    _name = 'warcraft.building_type'
    _description = 'Type of buildings'

    name = fields.Char()
    icon = fields.Image(max_width=200, max_height=200)
    food_production = fields.Float()
    gold_production = fields.Float()
    wood_production = fields.Float()
    units_production = fields.Float()
    gold_price = fields.Float()


class Building(models.Model):
    _name = 'warcraft.building'
    _description = 'Townhall Buildings'
    name = fields.Char(compute='_get_name')
    townhall = fields.Many2one('warcraft.townhall', required=True)
    type = fields.Many2one('warcraft.building_type', required=True)
    level = fields.Integer(default=0)
    icon = fields.Image(related='type.icon')

    update_percent = fields.Float(default=0)
    food_production = fields.Float(compute='production')
    wood_production = fields.Float(compute='production')
    gold_production = fields.Float(compute='production')
    units_production = fields.Float(compute='production')
    gold_price = fields.Float(compute='production')

    @api.depends('type', 'level')
    def production(self):
        for b in self:
            b.food_production = b.type.food_production + b.type.food_production * math.log(b.level + 1)
            b.gold_production = b.type.gold_production + b.type.gold_production * math.log(b.level + 1)
            b.units_production = b.type.units_production + b.type.units_production * math.log(b.level + 1)
            b.wood_production = b.type.wood_production + b.type.wood_production * math.log(b.level + 1)
            b.gold_price = b.type.gold_price + b.level

    @api.depends('type', 'townhall')
    def _get_name(self):
        for b in self:
            b.name = 'undefined'
            if b.type and b.townhall:
                b.name = b.type.name + " " + b.townhall.name + " " + str(b.id)

    def update_level(self):
        for building in self.search([('update_percent', '<', 100)]):
            building.update_percent += 1 / (building.level + 1)
            if building.update_percent >= 100:
                building.update_percent = 100
                building.level += 1
            print(building.name, building.update_percent)

    def update_building(self):
        for b in self:
            if b.update_percent == 100:
                b.update_percent = 0

    @api.constrains('level')
    def _check_level(self):
        for b in self:
            if b.update_percent != 100 and b.level > 0:
                raise ValidationError("You can't update while updating")

    @api.depends('townhall')
    def _get_is_active(self):
        for b in self:
            b.is_active = True
            if b.gold_production < 0 and b.townhall.gold <= abs(b.gold_production):
                b.is_active = False
            if b.wood_production < 0 and b.townhall.wood <= abs(b.wood_production):
                b.is_active = False
            if b.food_production < 0 and b.townhall.food <= abs(b.food_production):
                b.is_active = False


class Unit(models.Model):
    _name = 'warcraft.unit'
    _description = 'Units'

    name = fields.Char()
    townhall = fields.Many2one('warcraft.townhall')
    soldier = fields.Integer()
    archer = fields.Integer()
    training = fields.Float(default=1)
    time_training = fields.Float(default=0)
    total_soldiers = fields.Integer(compute='get_total_soldiers')

    @api.depends('soldier', 'archer')
    def get_total_soldiers(self):
        print(self)
        for unit in self:
            total = unit.soldier + unit.archer
            unit.total_soldiers = total

    def update_training(self):
        for unit in self.search([('time_training', '>', 0)]):
            unit.time_training = unit.time_training - 1
            if unit.time_training <= 0:
                unit.training += 1


class Battle(models.Model):
    _name = 'warcraft.battle'
    _description = 'Battles'

    name = fields.Char()
    start = fields.Datetime(default=lambda self: fields.Datetime.now())
    end = fields.Datetime(compute='get_data_end')
    total_time = fields.Integer(compute='get_data_end')
    remaining_time = fields.Char(compute='get_data_end')
    progress = fields.Float(compute='get_data_end')
    townhall1 = fields.Many2one('warcraft.townhall', domain="[('id','!=',townhall2)]")
    townhall2 = fields.Many2one('warcraft.townhall', domain="[('id','!=',townhall1)]")
    units1 = fields.Many2many('warcraft.unit', domain="[('townhall','=',townhall1), ('training','>',0)]")

    def update_battles(self):
        for b in self.search([]):
            if fields.Datetime.now() > b.end:
                print(b.name)

    @api.depends('start')
    def get_data_end(self):
        for b in self:
            date_start = fields.Datetime.from_string(b.start)
            date_end = date_start + timedelta(hours=2)
            b.end = fields.Datetime.to_string(date_end)
            b.total_time = (date_end - date_start).total_seconds() / 60
            remaining = relativedelta(date_end, datetime.now())
            b.remaining_time = str(remaining.hours) + ":" + str(remaining.minutes) + ":" + str(remaining.seconds)
            passed_time = (datetime.now() - date_start).total_seconds()
            b.progress = (passed_time * 100) / (b.total_time * 60)
            if b.progress > 100:
                b.progress = 100
                b.remaining_time = '00:00:00'


# WIZARDS DE PRUEBA CON EL MODELO BUILDING

class BuildingWizard(models.TransientModel):
    _name = 'warcraft.building_wizard'

    def get_townhall(self):
        return self._context.get('townhall_context')

    name = fields.Char(compute='get_name')
    townhall = fields.Many2one('warcraft.townhall', required=True, default=get_townhall)
    type = fields.Many2one('warcraft.building_type', required=True)
    level = fields.Integer(default=0)
    icon = fields.Image(related='type.icon')

    @api.depends('type', 'townhall')
    def get_name(self):
        for b in self:
            b.name = 'undefined'
            if b.type and b.townhall:
                b.name = b.type.name + " " + b.townhall.name + " " + str(b.id)

    def create_building(self):
        self.env['warcraft.building'].create({
            'type': self.type.id,
            'townhall': self.townhall.id
        })


class BattleWizard(models.TransientModel):
    _name = 'warcraft.battle_wizard'

    def _get_townhall(self):
        return self._context.get('townhall_context')

    state = fields.Selection([
        ('townhalls', "Townhalls Selection"),
        ('units', "Units Selection"),
        ('dates', "Dates Selection"),
    ], default='townhalls')

    name = fields.Char()
    start = fields.Datetime(default=lambda self: fields.Datetime.now())
    townhall1 = fields.Many2one('warcraft.townhall', readonly=True, default=_get_townhall, domain="[('id','!=',townhall2)]")
    townhall2 = fields.Many2one('warcraft.townhall', domain="[('id','!=',townhall1)]")

    available_units = fields.Many2many('warcraft.battle_wizard_unit', compute='get_units')
    units1 = fields.Many2many('warcraft.battle_wizard_unit', readonly=True)

    @api.depends('townhall1')
    def get_units(self):
        available_units = self.env['warcraft.battle_wizard_unit']

        if len(self.townhall1) > 0:
            townhall_available_units = self.townhall1.units;
            for a_unit in townhall_available_units:
                selected = False
                if len(self.units1.filtered(lambda u: u.unit.id == a_unit.id)) > 0:
                    selected = True
                available_units = available_units + self.env['warcraft.battle_wizard_unit'] \
                    .create({"unit": a_unit.id, "selected": selected})
            self.available_units = available_units

    def create_battle(self):
        min_date = fields.Datetime.from_string(fields.Datetime.now()) - timedelta(minutes=5)
        if self.start < min_date:
            self.start = fields.Datetime.now()
        self.env['warcraft.battle'].create({
            "name": self.name,
            "start": self.start,
            "townhall1": self.townhall1.id,
            "townhall2": self.townhall2.id
        })

    def action_previous(self):
        if self.state == 'units':
            self.state = 'townhalls'
        elif self.state == 'dates':
            self.state = 'units'
        return {
            'type': 'ir.actions.act_window',
            'name': 'Launch battle wizard',
            'res_model': self._name,
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': self._context
        }

    def action_next(self):
        if self.state == 'townhalls':
            if len(self.townhall2) > 0:
                self.state = 'units'
            else:
                return {
                    'type': 'ir.actions.client',
                    'tag': 'display_notification',
                    'params': {
                        'message': 'Townhall 2 not selected',
                        'type': 'info',
                        'sticky': False,
                    }
                }
        elif self.state == 'units':
            self.assign_multiple()
            self.state = 'dates'
        print(self)
        return {
            'type': 'ir.actions.act_window',
            'name': 'Launch battle wizard',
            'res_model': self._name,
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': self._context
        }

    def assign_multiple(self):

        context_available_units = self._context.get('wizard_available_units')[0][2]
        selected = self.env['warcraft.battle_wizard_unit'].browse(context_available_units).filtered(
            lambda u: u.selected == True)
        print("context selected", selected)
        self.units1 = selected.ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Launch battle wizard',
            'res_model': self._name,
            'view_mode': 'form',
            'target': 'new',
            'res_id': self.id,
            'context': self._context
        }

    @api.onchange('start')
    def onchange_start(self):
        min_date = fields.Datetime.from_string(fields.Datetime.now()) - timedelta(minutes=5)
        print(min_date, fields.Datetime.now())
        if self.start < min_date:
            self.start = fields.Datetime.now()
            return {
                'warning': {'title': "Warning", 'message': "Min date", 'type': 'notification'},
            }


class BattleWizardUnit(models.TransientModel):
    _name = 'warcraft.battle_wizard_unit'

    unit = fields.Many2one('warcraft.unit')

    name = fields.Char(related='unit.name')
    townhall = fields.Many2one('warcraft.townhall', related='unit.townhall')
    soldiers = fields.Integer(related='unit.soldier')
    archers = fields.Integer(related='unit.archer')
    total_soldiers = fields.Integer(related='unit.total_soldiers')

    selected = fields.Boolean()

    def assign_to_battle(self):
        wizard = self._context.get('battle_wizard_context')
        wizard = self.env['warcraft.battle_wizard'].browse(wizard)
        wizard.write({"units1": [(4, self.id)]})

        return {
            'type': 'ir.actions.act_window',
            'name': 'Launch battle wizard',
            'res_model': wizard._name,
            'view_mode': 'form',
            'target': 'new',
            'res_id': wizard.id,
            'context': wizard._context
        }
