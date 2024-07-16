# This file is part shipment_production_assign module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.modules.company.tests import CompanyTestMixin
from trytond.tests.test_tryton import ModuleTestCase


class ShipmentProductionAssignTestCase(ModuleTestCase, CompanyTestMixin):
    'Test Shipment Production Assign module'
    module = 'shipment_production_assign'


del ModuleTestCase
