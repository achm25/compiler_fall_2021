class Scope:
    # we need it to find out what decereation in this scope for which one , help us to add it to .data
    block_counter: int = 0
    int_const_counter : int = 1
    string_const_counter : int = 1
    bool_const_counter : int = 1
    double_const_counter : int = 1
    def __init__(self, name=None, parent_scope=None):
        self.name = name
        self.parent_scope = parent_scope
        self.symbols = {}
        self.functions = {}  #for keep functions name


    def add_function(self, fun):
        self.functions[fun.identifier.name] = fun

    def find_function(self, fun):
        if fun in self.functions:
            return self.functions[fun]
        if self.parent_scope is not None:
            return self.parent_scope.find_function(fun)
        else:
            raise Exception("not found!")


    def add_symbol(self, symbol):
        self.symbols[symbol.identifier.name] = symbol

    def find_symbol(self, symbol):
        if symbol in self.symbols:
            return self.symbols[symbol]
        if self.parent_scope is not None:
            return self.parent_scope.find_symbol(symbol)
        else:
            raise Exception("not found!")


    def find_symbol_path(self, symbol):
        if symbol in self.symbols:
            return self
        if self.parent_scope is not None:
            return self.parent_scope.find_symbol_path(symbol)
        else:
            raise Exception("not found!")

    def root_generator(self):

        if self.parent_scope is None:
            return self.name

        name = ""
        root = self.parent_scope
        while root is not None:
            name = root.name + "_" + name
            root = root.parent_scope

        return name + self.name