# import ply.lex as lex
#
# # define token name here
# ID = 'ID'
# HEXADECIMAL = 'HEXADECIMAL'
# FLOATNUMBER = 'FLOATNUMBER'
# INTNUMBER = 'INTNUMBER'
# EQUAL = 'EQUAL'
# NOTEQUAL = 'NOTEQUAL'
# GREATEREQUALS = 'GREATEREQUALS'
# LESSEQUAL = 'LESSEQUAL'
# SIGNS = 'SIGNS'
# AND = 'AND'
# OR = 'OR'
# MINUS = 'MINUS'
# BOOLEAN = 'BOOLEAN'
# STRINGLITERAL = 'STRINGLITERAL'
# MINUSEQUAL = 'MINUSEQUAL'
# PLUSEQUAL = 'PLUSEQUAL'
#
#
#
#
#
# reserved_words = {
#     '__func__': '__func__',
#     '__line__': '__line__',
#     'bool': 'bool',
#     'break': 'break',
#     'btoi': 'btoi',
#     'class': 'class',
#     'continue': 'continue',
#     'define': 'define',
#     'double': 'double',
#     'dtoi': 'dtoi',
#     'else': 'else',
#     'for': 'for',
#     'if': 'if',
#     'import': 'import',
#     'int': 'int',
#     'itob': 'itob',
#     'itod': 'itod',
#     'new': 'new',
#     'NewArray': 'NewArray',
#     'null': 'null',
#     'Print': 'Print',
#     'private': 'private',
#     'public': 'public',
#     'ReadInteger': 'ReadInteger',
#     'ReadLine': 'ReadLine',
#     'return': 'return',
#     'string': 'string',
#     'this': 'this',
#     'void': 'void',
#     'while': 'while',
# }
#
#
#
# reserved = reserved_words
#
# # List of token names.This is always required
# tokens = [ID,
#           HEXADECIMAL,
#           FLOATNUMBER,
#           INTNUMBER,
#           STRINGLITERAL,
#           BOOLEAN,
#           EQUAL,
#           NOTEQUAL,
#           GREATEREQUALS,
#           MINUSEQUAL,
#           PLUSEQUAL,
#           LESSEQUAL,
#           AND,
#           OR,
#           MINUS,
#           SIGNS,
#           ] + list(reserved.values())
#
# # Regular expression rules for simple tokens
# t_SIGNS = r"[@_!+#$%^&*()<>?/|}{~:=,;\[\]]"
#
#
# # A regular expression rule with some action code
#
# def t_COMMENT(t):
#     r'//.*'
#     pass
#
#
# def t_AND(t):
#     r'\&&'
#     return t
#
#
# def t_OR(t):
#     r'\|{2}'
#     return t
#
#
# def t_LESSEQUAL(t):
#     r'\<='
#     return t
#
#
# def t_MINUSEQUAL(t):
#     r'\-='
#     return t
#
#
# def t_GREATEREQUALS(t):
#     r'-'
#     return t
#
#
# def t_MINUS(t):
#     r'\>='
#     return t
#
#
# def t_NOTEQUAL(t):
#     r'\!='
#     return t
#
#
# def t_PLUSEQUAL(t):
#     r'\+='
#     return t
#
#
# def t_EQUAL(t):
#     r'={2}'
#     return t
#
#
# def t_HEXADECIMAL(t):
#     r'\b0x[0-9A-z]+\b'
#     return t
#
#
# def t_FLOATNUMBER(t):
#     r'[-+]?\d*\.\d*'
#     t.value = float(t.value)
#     return t
#
#
# def t_INTNUMBER(t):
#     r'[-+]?\d+'
#     t.value = int(t.value)
#     return t
#
#
# def t_BOOLEAN(t):
#     r'\btrue\b|\bfalse\b'
#     return t
#
#
# def t_newline(t):
#     r'\n+'
#     t.lexer.lineno += len(t.value)
#
#
# def t_STRINGLITERAL(t):
#     r"'(\\'|[^'])*(?!<\\)'|\"(\\\"|[^\"])*(?!<\\)\""
#     return t
#
#
# def t_ID(t):
#     r'[a-zA-Z_][a-zA-Z_0-9]*'
#     t.type = reserved.get(t.value, 'ID')  # Check for reserved words
#     return t
#
# # A string containing ignored characters (spaces and tabs)
# t_ignore = ' \t'
#
#
# # Error handling rule
# def t_error(t):
#     print("Illegal character '%s'" % t.value[0])
#     t.lexer.skip(1)
#
#
#
#
# def find_define_word(t):
#     final_text = ""
#     saved_list = []
#     for line in t.splitlines():
#         line = line.strip()
#         temp_list = line.split(" ", 2)
#         if "define" in temp_list:
#             saved_list.append({"key": temp_list[1], "value": temp_list[2]})
#             line = ""
#
#         if line != "":
#             final_text = final_text + line + "\n"
#
#     return final_text, saved_list
#
#
# def replace_define_word(t, word_list):
#     for item in word_list:
#         t = t.replace(item["key"], item["value"])
#     return t
#
#
# def handleDefine(t):
#     text, word_list = find_define_word(t)
#     return replace_define_word(text, word_list)
#
# def judgment_format_write(token):
#     if token.type == ID:
#         # print("T_ID", token.value)
#         return "T_ID" + " " +str(token.value)
#     elif token.type in reserved_words.values():
#         # print(token.value)
#         return str(token.value)
#     elif token.type == INTNUMBER:
#         # print("T_INTLITERAL", token.value)
#         return "T_INTLITERAL" + " " +str(token.value)
#     elif token.type == STRINGLITERAL:
#         # print("T_STRINGLITERAL", token.value)
#         return "T_STRINGLITERAL" + " " +str(token.value)
#     elif token.type == FLOATNUMBER:
#         # print("T_DOUBLELITERAL", token.value)
#         return "T_DOUBLELITERAL" + " " +str(token.value)
#     elif token.type == HEXADECIMAL:
#         # print("T_INTLITERAL", token.value)
#         return "T_INTLITERAL" + " " +str(token.value)
#     elif token.type == BOOLEAN:
#         # print("T_BOOLEANLITERAL", token.value)
#         return "T_BOOLEANLITERAL" + " " +str(token.value)
#     else:
#         # print(token.value)
#         return str(token.value)
#
# def run(input_file_address: str) -> str:
#     result = ''
#     # Build the lexer
#     lexer = lex.lex()
#     with open(input_file_address) as input_file:
#         data = input_file.read()
#
#     lexer.input(handleDefine(data))
#     while True:
#         token = lexer.token()
#         if not token:
#             break  # No more input
#         result += judgment_format_write(token) + "\n"
#
#     return result[:-1]
#
#
# actual = run("input.txt")
# print(actual)
# # # Test it out
# # data = r'''
# # define SEMICOLON ;
# # define FOR100 for(i = 0; i < 100; i += 1)
# #
# # FOR100
# # Print(i)SEMICOLON
# # '''
# #
# #
# # # Give the lexer some input
# # lexer.input(handleDefine(data))
# #
# #
# #
# # # Tokenize
# # result = ""
# # while True:
# #     tok = lexer.token()
# #     if not tok:
# #         break  # No more input
# #     # print(tok.type, tok.value, tok.lineno, tok.lexpos)  #more option for print
# #     # judgment_format(tok)
# #     result += judgment_format_write(tok) + "\n"
# #
# # print(result)
