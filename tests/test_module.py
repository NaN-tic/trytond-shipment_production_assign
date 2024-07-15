# This file is part shipment_production_assign module for Tryton.
# The COPYRIGHT file at the top level of this repository contains
# the full copyright notices and license terms.
from trytond.tests.test_tryton import ModuleTestCase
from trytond.modules.company.tests import (
    CompanyTestMixin, create_company, set_company)
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.transaction import Transaction
from trytond.pool import Pool


class ShipmentProductionAssignTestCase(ModuleTestCase):
    'Test Shipment Production Assign module'
    module = 'shipment_production_assign'

    @with_transaction()
    def test_party_identifiers(self):
        'Party Identifiers'
        pool = Pool()
        company = create_company()


del ModuleTestCase
