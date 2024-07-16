from trytond.model import ModelView, Workflow
from trytond.pool import PoolMeta, Pool
from trytond.modules.company.model import set_employee


class Move(metaclass=PoolMeta):
    __name__ = 'stock.move'

    def get_linked_production(self):
        SaleLine = Pool().get('sale.line')
        if isinstance(self.origin, Move) and isinstance(self.origin.origin, SaleLine):
            return self.origin.origin.productions

    @classmethod
    def assign_try(cls, moves, with_childs=True, grouping=('product',)):
        pool = Pool()
        Production = pool.get('production')

        productions = []
        out_of_scope = []
        for move in moves:
            linked = move.get_linked_production()
            if linked:
                productions += linked
            else:
                out_of_scope.append(move)
        if productions:
            for production in productions:
                production.state = 'waiting'
            Production.assign_try(productions)
            for production in productions:
                if production.state == 'waiting':
                    cls.assign(production.origin.moves)
        return super().assign_try(out_of_scope, with_childs, grouping)

    @classmethod
    @ModelView.button
    @Workflow.transition('done')
    def do(cls, moves):
        Production = Pool().get('production')

        for move in moves:
            linked = move.get_linked_production()
            if not linked:
                continue
            for production in linked:
                if production.state == 'assigned':
                    Production.run([production])
                if production.state == 'running':
                    Production.done([production])
                if production.state == 'done':
                    if production.outputs:
                        move.lot = production.outputs[0].lot
        super().do(moves)
