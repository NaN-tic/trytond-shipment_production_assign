from trytond.model import ModelView, Workflow
from trytond.pool import PoolMeta, Pool


class Move(metaclass=PoolMeta):
    __name__ = 'stock.move'

    def get_linked_production(self):
        SaleLine = Pool().get('sale.line')
        if isinstance(self.origin, Move) and isinstance(self.origin.origin, SaleLine):
            return self.origin.origin.productions

    @classmethod
    def assign(cls, moves):
        pool = Pool()
        Production = pool.get('production')

        super().assign(moves)

        productions = []
        for move in moves:
            linked = move.get_linked_production()
            if not linked:
                continue
            productions.extend(linked)

        if productions:
            Production.assign(productions)

    @classmethod
    def assign_try(cls, moves, with_childs=True, grouping=('product',)):
        pool = Pool()
        Production = pool.get('production')

        success = True
        mapping = {}
        out_of_scope = []
        for move in moves:
            linked = move.get_linked_production()
            if linked:
                mapping[move] = linked[0]
            else:
                out_of_scope.append(move)
        if mapping:
            productions = mapping.values()
            for production in productions:
                if production.state == 'draft':
                    production.state = 'waiting'
            Production.save(productions)
            Production.assign_try(productions)

            to_save = []
            for move, production in mapping.items():
                if production.state != 'assigned':
                    success = False
                    continue
                if production.outputs:
                    move.from_location = production.outputs[0].to_location
                    to_save.append(move)
            cls.save(to_save)

        return super().assign_try(out_of_scope, with_childs, grouping) and success

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
