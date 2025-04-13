
# parsetab.py
# This file is automatically generated. Do not edit.
# pylint: disable=W,C,R
_tabversion = '3.10'

_lr_method = 'LALR'

_lr_signature = 'AND ASSIGN BOOL CASE CHAR CIN COMMA COMMENT COUT DECREMENT DIVIDE DO EEQ ELSE END EQ ERROR FALSE FLOAT GE GT ID IF INCREMENT INT INVALID_COMMENT INVALID_ID INVALID_REAL LBRACE LE LPAREN LT MAIN MINUS MODULO NE NOT NUMBER OR PLUS POWER RBRACE REAL RPAREN SEMICOLON STRING SWITCH THEN TIMES TRUE UNTIL WHILEexpression : expression PLUS termexpression : expression MINUS termexpression : termterm : term TIMES factorterm : term DIVIDE factorterm : factorfactor : NUMBERfactor : LPAREN expression RPARENfactor : ID'
    
_lr_action_items = {'NUMBER':([0,5,7,8,9,10,],[4,4,4,4,4,4,]),'LPAREN':([0,5,7,8,9,10,],[5,5,5,5,5,5,]),'ID':([0,5,7,8,9,10,],[6,6,6,6,6,6,]),'$end':([1,2,3,4,6,12,13,14,15,16,],[0,-3,-6,-7,-9,-1,-2,-4,-5,-8,]),'PLUS':([1,2,3,4,6,11,12,13,14,15,16,],[7,-3,-6,-7,-9,7,-1,-2,-4,-5,-8,]),'MINUS':([1,2,3,4,6,11,12,13,14,15,16,],[8,-3,-6,-7,-9,8,-1,-2,-4,-5,-8,]),'RPAREN':([2,3,4,6,11,12,13,14,15,16,],[-3,-6,-7,-9,16,-1,-2,-4,-5,-8,]),'TIMES':([2,3,4,6,12,13,14,15,16,],[9,-6,-7,-9,9,9,-4,-5,-8,]),'DIVIDE':([2,3,4,6,12,13,14,15,16,],[10,-6,-7,-9,10,10,-4,-5,-8,]),}

_lr_action = {}
for _k, _v in _lr_action_items.items():
   for _x,_y in zip(_v[0],_v[1]):
      if not _x in _lr_action:  _lr_action[_x] = {}
      _lr_action[_x][_k] = _y
del _lr_action_items

_lr_goto_items = {'expression':([0,5,],[1,11,]),'term':([0,5,7,8,],[2,2,12,13,]),'factor':([0,5,7,8,9,10,],[3,3,3,3,14,15,]),}

_lr_goto = {}
for _k, _v in _lr_goto_items.items():
   for _x, _y in zip(_v[0], _v[1]):
       if not _x in _lr_goto: _lr_goto[_x] = {}
       _lr_goto[_x][_k] = _y
del _lr_goto_items
_lr_productions = [
  ("S' -> expression","S'",1,None,None,None),
  ('expression -> expression PLUS term','expression',3,'p_expression_plus','sintactico.py',6),
  ('expression -> expression MINUS term','expression',3,'p_expression_minus','sintactico.py',10),
  ('expression -> term','expression',1,'p_expression_term','sintactico.py',14),
  ('term -> term TIMES factor','term',3,'p_term_times','sintactico.py',18),
  ('term -> term DIVIDE factor','term',3,'p_term_div','sintactico.py',22),
  ('term -> factor','term',1,'p_term_factor','sintactico.py',28),
  ('factor -> NUMBER','factor',1,'p_factor_num','sintactico.py',32),
  ('factor -> LPAREN expression RPAREN','factor',3,'p_factor_expr','sintactico.py',36),
  ('factor -> ID','factor',1,'p_factor_id','sintactico.py',40),
]
