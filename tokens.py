# 0     NUMERO
# 1     IDENTIFICADOR
# 2     PALABRA_RESERVADA
# 3     OP_ARITMETICO
# 4     OP_RELACIONAL
# 5     OP_LOGICO
# 6     SIMBOLO
# 7     ASIGNACION
# 8     INCREMENTO
# 9     DECREMENTO
tokens = ["NUMERO",
          "IDENTIFICADOR",
          "PALABRA_RESERVADA",
          "OP_ARITMETICO",
          "OP_RELACIONAL",
          "OP_LOGICO",
          "SIMBOLO",
          "ASIGNACION",
          "INCREMENTO",
          "DECREMENTO",
          "COMENTARIO"]

# 0     ENTERO
# 1     REAL
# 2     IF
# 3     ELSE
# 4     DO
# 5     WHILE
# 6     SWITCH
# 7     CASE
# 8     INTEGER
# 9     DOUBLE
# 10    MAIN
# 11    CIN
# 12    COUT
# 13    SUMA
# 14    RESTA
# 15    MULTIPLICACION
# 16    DIVISION
# 17    MODULO
# 18    POTENCIA
# 19    MENOR
# 20    MENOR_IGUAL
# 21    MAYOR
# 22    MAYOR_IGUAL
# 23    DIFERENTE
# 24    IGUAL
# 25    AND
# 26    OR
# 27    PARENTESIS_I
# 28    PARENTESIS_D
# 29    LLAVE_I
# 30    LLAVE_D
# 31    COMA
# 32    PUNTO_Y_COMA
# 33    INCREMENTO
# 34    DECREMENTO
# 35    END
# 36    ENTERO_NEG
# 37    REAL_NEG

sub_tokens = ["ENTERO","REAL","IF","ELSE","DO",
              "WHILE","SWITCH","CASE","INTEGER","DOUBLE",
              "MAIN","CIN","COUT","SUMA","RESTA",
              "MULTIPLICACION","DIVISION","MODULO","POTENCIA","MENOR",
              "MENOR_IGUAL","MAYOR","MAYOR_IGUAL","DIFERENTE","IGUAL",
              "AND","OR","PARENTESIS_I","PARENTESIS_D","LLAVE_I",
              "LLAVE_D","COMA","PUNTO_Y_COMA","INCREMENTO","DECREMENTO",
              "END","ENTERO_NEG","REAL_NEG"]

palabras_reservadas = ["if","else","do","while","switch","case","integer","double","main","cin","cout"]