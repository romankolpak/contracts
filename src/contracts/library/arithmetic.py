from contracts.interface import ContractSemanticError, RValue
from contracts.syntax import (isnumber, W)

class Binary(RValue):
    operations = {
        '+': lambda x, y: x + y,
        '-': lambda x, y: x - y,
        '*': lambda x, y: x * y
    }
    
    precedence = {
        '+': 0,
        '-': 0,
        '*': 1,
    }
    def __init__(self, exprs, glyph, where=None):
        self.where = where
        self.exprs = exprs 
        self.glyph = glyph
        self.operation = Binary.operations[glyph]
        self.precedence = Binary.precedence[glyph]
        
    def eval(self, context):
        vals = []
        for expr in self.exprs:
            val = context.eval(expr, self)
            if not isnumber(val):
                msg = ('I can only do math with numbers, not %r.' % 
                       val.__class__.__name__) 
                raise ContractSemanticError(self, msg, context)
            vals.append(val)
        return reduce(self.operation, vals)
        
    def __repr__(self):
        s = 'Binary(%r,%r)' % (self.exprs, self.glyph)
        return s
    
    def __str__(self):
        def convert(x):
            if isinstance(x, Binary) and x.precedence < self.precedence:
                return '(%s)' % x
            else:
                return '%s' % x
        
        s = self.glyph.join(convert(x) for x in self.exprs)
        return s

    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        l = list(tokens[0])
        exprs = [l.pop(0)]
        while l:
            glyph = l.pop(0)
            expr = l.pop(0)
            assert isnumber(expr) or isinstance(expr, RValue)
            exprs.append(expr)

        return Binary(exprs, glyph, where=where)


class Unary(RValue):
    operations = {
        '-': lambda x:-x,
    }
    def __init__(self, glyph, expr, where=None):
        self.where = where
        self.expr = expr
        self.glyph = glyph
        self.operation = Unary.operations[glyph]
        
    def eval(self, context):
        val = context.eval(self.expr, self)
        if not isnumber(val):
            msg = ('I can only do math with numbers, not %r.' % 
                   val.__class__.__name__) 
            raise ContractSemanticError(self, msg, context)
        
        return self.operation(val)
        
    def __repr__(self):
        s = 'Unary(%r,%r)' % (self.glyph, self.expr)
        return s
    
    def __str__(self): 
        # XXX: precedence
        return '%s%s' % (self.glyph, self.expr)
    
    @staticmethod
    def parse_action(s, loc, tokens):
        where = W(s, loc)
        glyph = tokens[0][0]
        expr = tokens[0][1]
        return Unary(glyph, expr, where=where)
    