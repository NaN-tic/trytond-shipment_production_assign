# This file is part shipment_production_assign module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.pool import Pool
from . import shipment

def register():
    Pool.register(
        shipment.ShipmentOut,
        shipment.Move,
        module='shipment_production_assign', type_='model')
    Pool.register(
        module='shipment_production_assign', type_='wizard')
    Pool.register(
        module='shipment_production_assign', type_='report')
