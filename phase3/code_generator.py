
int_size = 4
double_size = 8
string_size = 1
bool_size = 1

TYPE_IS_STRING = "string"
TYPE_IS_INT = "int"
TYPE_IS_NULL = "null"
TYPE_IS_DOUBLE = "double"
TYPE_IS_BOOL = "bool"

printStringVal = "printStringVal"
printIntVal  =  "printIntVal"
printDoubleVal = "printDoubleVal"
printBoolVal  = "printBoolVal"

tempIntVar = "tempIntVar"
tempDoubleVar = "tempDoubleVar"
tempBoolVar = "tempBoolVar"
tempStringVar = "tempStringVar"


class CodeGenerator:

    @staticmethod
    def get_type(node, symbol_table):
        if type(node).__name__ == "IdentifierLValue":
            return symbol_table.current_scope.symbols[node.identifier.name].v_type.name
        if type(node).__name__ == "Expression":
            l_operand_type = CodeGenerator.get_type(node.l_operand, symbol_table)
            return l_operand_type
        if type(node).__name__ == "Const":
            return node.v_type

    @staticmethod
    def minus_operation(symbol_table, operation):

        pass

    @staticmethod
    def new_variable(symbol_table, variable):
        code = []
        data = []

        #todo why we need new scope?
        #current_scope = symbol_table.new_scope()
        symbol_table.current_scope.add_symbol(variable)



        if variable.v_type.name == TYPE_IS_INT:
            name_generate = symbol_table.current_scope.root_generator()
            name_generate = name_generate + "__" +  variable.identifier.name
            data += [f"{name_generate}: .word 0"]


        size = int_size
        if variable.v_type.name == TYPE_IS_DOUBLE:
            name_generate = symbol_table.current_scope.root_generator()
            name_generate = name_generate + "__" +  variable.identifier.name
            data += [f"{name_generate}: .double 0.0"]

        if variable.v_type.name == TYPE_IS_STRING:
            name_generate = symbol_table.current_scope.root_generator()
            name_generate = name_generate + "__" +  variable.identifier.name
            data += [f"{name_generate}: .word 0"]


            #todo should be deleted
        if not (variable.is_global or variable.is_in_class or variable.is_func_param):
            variable.local_offset = symbol_table.local_offset
            symbol_table.local_offset += size
            code += [
                f"\tsubu $sp, $sp, {size}\t# Decrement sp to make space for variable {variable.identifier.name}."
            ]

        symbol_table.data_storage += data
        return code

    @staticmethod
    def variable_definition_with_assign(symbol_table, variable):
        code = []
        return code

    @staticmethod
    def variable_definition(symbol_table,variable):
        code  = CodeGenerator.new_variable(symbol_table, variable)
        return code

    @staticmethod
    def new_function(symbol_table, function):
        symbol_table.current_scope.add_function(function)
        symbol_table.local_offset = 0
        if function.parent_class is not None:
            function.label = (
                f"{function.parent_class.identifier.name}_{function.identifier.name}"
            )
        curr_scope = symbol_table.new_scope(name=function.identifier.name)
        for param in function.params:
            curr_scope.add_symbol(param)
        code = [
            f"{function.label}:",
            "\tsubu $sp, $sp, 8\t# decrement sp to make space to save ra, fp",
            "\tsw $fp, 8($sp)\t# save fp",
            "\tsw $ra, 4($sp)\t# save ra",
            "\taddiu $fp, $sp, 8\t# set up new fp",
        ]
        code += function.block.cgen(symbol_table)
        code += [
            "\tmove $sp, $fp\t\t# pop callee frame off stack",
            "\tlw $ra, -4($fp)\t# restore saved ra",
            "\tlw $fp, 0($fp)\t# restore saved fp",
            "\tjr $ra\t\t# return from function",
        ]
        # Reset
        symbol_table.local_offset = 0
        symbol_table.current_scope = curr_scope.parent_scope
        return code

    @staticmethod
    def new_void_function(symbol_table, function):
        symbol_table.current_scope.add_function(function)
        symbol_table.local_offset = 0
        if function.parent_class is not None:
            function.label = (
                f"{function.parent_class.identifier.name}_{function.identifier.name}"
            )
        curr_scope = symbol_table.new_scope(name=function.identifier.name)
        for param in function.params:
            curr_scope.push_symbol(param)
        code = [
            f"{function.label}:",
            "\tsubu $sp, $sp, 8\t# decrement sp to make space to save ra, fp",
            "\tsw $fp, 8($sp)\t# save fp",
            "\tsw $ra, 4($sp)\t# save ra",
            "\taddiu $fp, $sp, 8\t# set up new fp",
        ]
        code += function.block.cgen(symbol_table)
        code += [
            "\tmove $sp, $fp\t\t# pop callee frame off stack",
            "\tlw $ra, -4($fp)\t# restore saved ra",
            "\tlw $fp, 0($fp)\t# restore saved fp",
            "\tjr $ra\t\t# return from function",
        ]
        # Reset
        symbol_table.local_offset = 0
        symbol_table.current_scope = curr_scope.parent_scope
        return code

    @staticmethod
    def new_class(symbol_table,class_var): #todo add class model

        pass

    @staticmethod
    def statement_block(symbol_table, block):
        symbol_table.current_scope.block_counter += 1
        new_scope_name = symbol_table.current_scope.name+"_"+"block"+str(symbol_table.current_scope.block_counter)
        curr_scope = symbol_table.new_scope(name=new_scope_name)
        code = []

        for stm in block.block_statements:
            if type(stm).__name__ == "Variable":
                code += CodeGenerator.new_variable(symbol_table, stm)
            elif type(stm).__name__ == "IfStatement":
                code += CodeGenerator.if_statement(symbol_table, stm)
            elif type(stm).__name__ == "ForStatement":
                code += CodeGenerator.for_statement(symbol_table, stm)
            elif type(stm).__name__ == "PrintNode":
                code += CodeGenerator.print_statement(symbol_table, stm)
            elif type(stm).__name__ == "WhileStatement":
                code += CodeGenerator.while_statement(symbol_table, stm)
            elif type(stm).__name__ == "OptionalExpr":
                code += CodeGenerator.optional_expression_statement(symbol_table, stm)
            elif type(stm).__name__ == "ReturnStatement":
                break



        symbol_table.current_scope = curr_scope.parent_scope
        return code

    @staticmethod
    def optional_expression_statement(symbol_table, op_expr):
        code = []
        if op_expr.expr is not None:
           code += op_expr.expr.cgen(symbol_table)
        return code

    @staticmethod
    def if_statement(symbol_table, if_stm):
        symbol_table.current_scope.block_counter += 1
        code = []
        if if_stm.else_block is None:
            code += if_stm.condition.cgen(symbol_table)
            code.append(f"beqz $t1, IF{if_stm.if_id}")
            code += if_stm.block.cgen(symbol_table)
            code.append(f"IF{if_stm.if_id} END:")
        else:
            CodeGenerator.if_statement_with_else(symbol_table, if_stm)
        return code

    @staticmethod
    def if_statement_with_else(symbol_table,if_stm):
        symbol_table.current_scope.block_counter += 1
        code = []
        code += if_stm.condition.cgen(symbol_table)
        code.append(f"beqz $t1, ELSE {if_stm.if_id}")
        code += if_stm.body.cgen(symbol_table)
        code.append(f"j ELSE{if_stm.if_id} END")
        code.append(f"ELSE{if_stm.if_id}:")
        code += if_stm.else_body.cgen(symbol_table)
        code.append(f"ELSE{if_stm.if_id} END:")
        return code

    @staticmethod
    def while_statement(symbol_table, while_stm):
        symbol_table.current_scope.block_counter += 1
        code = [f"LOOP_{while_stm.while_id}:"]
        code += while_stm.condition.cgen(symbol_table)
        code.append(f"\tlw $t1, 4($sp)\t#load expression value from stack to t1")
        code += [
            f"\tlw $t1,4($sp)\t#copy top stack to t1",
            f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
        ]
        code.append(f"\tbeqz $t1,END_LOOP_{while_stm.while_id}")
        code += while_stm.body.cgen(symbol_table)
        code.append(f"END_LOOP_{while_stm.while_id}:")
        return code

    @staticmethod
    def for_statement(symbol_table, for_stm):
        symbol_table.current_scope.block_counter += 1
        code = []
        if for_stm.init is not None:
            code += for_stm.init.cgen(symbol_table)
            code += [
                f"\tlw $t0,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code.append(f"FOR_{for_stm.for_id}:")
        code += for_stm.condition.cgen(symbol_table)
        code += [
            f"\tlw $t1,4($sp)\t#copy top stack to t1",
            f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
        ]
        code.append(f"\tbeqz $t1,END_LOOP_{for_stm.for_id}")
        code += for_stm.block.cgen(symbol_table)
        if for_stm.update is not None:
            code += for_stm.update.cgen(symbol_table)
            code += [
                f"\tlw $t0,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code.append(f"\tj LOOP_{for_stm.for_id}\t# back to start of for")
        code.append(f"END_LOOP_{for_stm.for_id}:")
        return code

    @staticmethod
    def return_statement(symbol_table, return_stm):
        code = []
        if return_stm.statement is not None:
            code += return_stm.expression.cgen(symbol_table)
            if type(return_stm.statement).__name__ == "Const":
                if return_stm.statement.v_type == "double":
                    code += [
                        f"\tl.d $f0,0($sp)# move top stack to f0",
                        f"\taddu $sp,$sp,{double_size}\t# move sp higher cause of pop",
                    ]
                else:
                    code += [
                        f"\tlw $t0,{int_size}($sp)\t#copy top stack to t0",
                        f"\taddu $sp,$sp,{int_size}\t# move sp higher cause of pop",
                    ]
                    code += ["\tmove $v0, $t0\t# Copy return value to $v0"]
        return code

    @staticmethod
    def break_statement(symbol_table, break_stm):
        return [f"j END_LOOP_{break_stm.break_id}"]

    @staticmethod
    def continue_statement(symbol_table):
        pass


    @staticmethod
    def handle_var_for_print(symbol_table, print_node):
        pass

    @staticmethod
    def print_statement(symbol_table, print_node):
        code = []
        for expr in print_node.expr:

            code += expr.cgen(symbol_table)
            size = int_size
            #todo shlould handle call function and class in print
            if type(expr).__name__ == "Variable" or type(expr).__name__ == "Const":
                const_type = expr.v_type
                if const_type == TYPE_IS_INT:
                    code += [f"\tlw	$t0 , {tempIntVar}{symbol_table.current_scope.int_const_counter % 2}  # add from memory to t0"]
                    code += [f"\tsw	$t0 , {printIntVal}  # add from memory to t0"]
                    code.append(f"\tjal _PrintInt")
                elif const_type == TYPE_IS_STRING:
                    code += [f"\tlw	$t0 , {tempStringVar}{symbol_table.current_scope.string_const_counter % 2}  # add from memory to t0"]
                    code += [f"\tsw	$t0 , {printStringVal}  # add from memory to t0"]
                    code.append(f"\tjal _PrintString")
                elif const_type == TYPE_IS_BOOL:
                    code.append(f"\tjal _PrintBool")
                elif const_type == TYPE_IS_DOUBLE:
                    size = 8
                    code.append(f"\tjal _SimplePrintDouble")
            if type(expr).__name__ == "IdentifierLValue" :
                find_symbol_in_scope = symbol_table.current_scope.find_symbol(expr.identifier.name)
                symbol_type = find_symbol_in_scope.v_type.name
                if  symbol_type == TYPE_IS_INT:
                    find_symbol_in_memory = symbol_table.current_scope.find_symbol_path(expr.identifier.name)  # if return , means we have this symbol
                    symbol_path = find_symbol_in_memory.root_generator() + "__" + expr.identifier.name  # return root path
                    code += [f"\tlw	$t0 , {symbol_path}  # add from memory to t0"]
                    code += [f"\tsw	$t0 , {printIntVal}  # add from memory to t0"]
                    code.append(f"\tjal _PrintInt")
                elif symbol_type == TYPE_IS_STRING:
                    find_symbol_in_memory = symbol_table.current_scope.find_symbol_path(expr.identifier.name)  # if return , means we have this symbol
                    symbol_path = find_symbol_in_memory.root_generator() + "__" + expr.identifier.name  # return root path
                    code += [f"\tlw	$t0 , {symbol_path}  # add from memory to t0"]
                    code += [f"\tsw	$t0 , {printStringVal}  # add from memory to t0"]
                    code.append(f"\tjal _PrintString")
                # elif symbol_type == TYPE_IS_BOOL:  #todo should handle
                #     code.append(f"\tjal _PrintBool")
                # elif symbol_type == TYPE_IS_DOUBLE:
                #     size = 8
                #     code.append(f"\tjal _SimplePrintDouble")


            # code.append(f"\taddu $sp,$sp,{size}\t# clean parameters")
            code.append(f"\tjal _PrintNewLine")
        return code

    @staticmethod
    def logical_or(symbol_table, expr):
        code = []
        code += expr.l_operand.cgen(symbol_table)
        code += expr.r_operand.cgen(symbol_table)
        code += [
            f"\tlw $t0,4($sp)\t#copy top stack to t0",
            f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
        ]
        code += [
            f"\tlw $t1,4($sp)\t#copy top stack to t0",
            f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
        ]
        code.append("\tor $t2,$t1,$t0")
        code.append("\tsw	$t2, printBoolVal # store contents of register $t2 into RAM=")  # todo should be check

        return code

    @staticmethod
    def logical_and(symbol_table, expr):
        code = []
        code += expr.l_operand.cgen(symbol_table)
        code += expr.r_operand.cgen(symbol_table)
        code += [
            f"\tlw $t0,4($sp)\t#copy top stack to t0",
            f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
        ]
        code += [
            f"\tlw $t1,4($sp)\t#copy top stack to t0",
            f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
        ]
        code.append("\tand $t2,$t1,$t0")
        code.append("\tsw	$t2, printBoolVal # store contents of register $t2 into RAM=")  # todo should be check

        return code

    @staticmethod
    def equals_operation(symbol_table, expr):
        code = []
        code += expr.l_operand.cgen(symbol_table)
        code += expr.r_operand.cgen(symbol_table)
        if expr.l_operand.v_type == "int":
            code += [
                f"\tlw $t0,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code += [
                f"\tlw $t1,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code.append("\tseq $t2,$t1,$t0")
            code.append("\tsw	$t2, printBoolVal # store contents of register $t2 into RAM=")  # todo should be check

        else:
            counter = symbol_table.get_label()
            code += [
                f"\tl.d $f0,0($sp)# move top stack to f0",
                f"\taddu $sp,$sp,8\t# move sp higher cause of pop",
            ]
            code += [
                f"\tl.d $f2,0($sp)# move top stack to f2",
                f"\taddu $sp,$sp,8\t# move sp higher cause of pop",
            ]
            code.append("c.eq.d $f2,$f0")
            code.append(f"bc1f __double_le__{counter}")
            code.append("li $t0, 1")
            code.append(f"__double_le__{counter}:")
            code += [
                f"\tsubu $sp,$sp,4\t# move sp down cause of push",
                f"\tsw $t0,4($sp)\t#copy t0 to stack",
            ]
        return code

    @staticmethod
    def not_equals_operation(symbol_table, expr):
        code = []
        code += expr.l_operand.cgen(symbol_table)
        code += expr.r_operand.cgen(symbol_table)
        l_operand_type = CodeGenerator.get_type(expr.l_operand, symbol_table)

        if l_operand_type == "int":
            code += [
                f"\tlw $t0,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code += [
                f"\tlw $t1,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code.append("\tsne $t2,$t1,$t0")
            code.append("\tsw	$t2, printBoolVal # store contents of register $t2 into RAM=") #todo should be check

        else:
            counter = symbol_table.get_label()
            code += [
                f"\tl.d $f0,0($sp)# move top stack to f0",
                f"\taddu $sp,$sp,8\t# move sp higher cause of pop",
            ]
            code += [
                f"\tl.d $f2,0($sp)# move top stack to f2",
                f"\taddu $sp,$sp,8\t# move sp higher cause of pop",
            ]
            code.append("c.eq.d $f2,$f0")
            code.append(f"bc1t __double_le__{counter}")
            code.append("li $t0, 1")
            code.append(f"__double_le__{counter}:")
            code += [
                f"\tsubu $sp,$sp,4\t# move sp down cause of push",
                f"\tsw $t0,4($sp)\t#copy t0 to stack",
            ]
        return code

    @staticmethod
    def lt_operation(symbol_table, expr):
        code = []
        code += expr.l_operand.cgen(symbol_table)
        code += expr.r_operand.cgen(symbol_table)
        l_operand_type = CodeGenerator.get_type(expr.l_operand, symbol_table)

        if l_operand_type == "int":
            code += [
                f"\tlw $t0,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code += [
                f"\tlw $t1,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code.append("slt $t2,$t1,$t0")
            code.append("sw	$t2, printBoolVal # store contents of register $t2 into RAM=")  # todo should be check

        return code

    @staticmethod
    def lte_operation(symbol_table, expr):
        code = []
        code += expr.l_operand.cgen(symbol_table)
        code += expr.r_operand.cgen(symbol_table)
        l_operand_type = CodeGenerator.get_type(expr.l_operand, symbol_table)

        if l_operand_type == "int":
            code += [
                f"\tlw $t0,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code += [
                f"\tlw $t1,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code.append("\tsle $t2,$t1,$t0")
            code.append("\tsw	$t2, printBoolVal # store contents of register $t2 into RAM=")  # todo should be check

        return code

    @staticmethod
    def gt_operation(symbol_table, expr):
        code = []
        code += expr.l_operand.cgen(symbol_table)
        code += expr.r_operand.cgen(symbol_table)
        l_operand_type = CodeGenerator.get_type(expr.l_operand, symbol_table)

        if l_operand_type == "int":
            code += [
                f"\tlw $t0,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code += [
                f"\tlw $t1,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code.append("\tsgt $t2,$t1,$t0")
            code.append("\tsw	$t2, printBoolVal # store contents of register $t2 into RAM=")  # todo should be check

        else:
            counter = symbol_table.get_label()
            code += [
                f"\tl.d $f0,0($sp)# move top stack to f0",
                f"\taddu $sp,$sp,8\t# move sp higher cause of pop",
            ]
            code += [
                f"\tl.d $f2,0($sp)# move top stack to f2",
                f"\taddu $sp,$sp,8\t# move sp higher cause of pop",
            ]
            code.append("c.le.d $f2,$f0")
            code.append(f"bc1t __double_le__{counter}")
            code.append("li $t0, 1")
            code.append(f"__double_le__{counter}:")
            code += [
                f"\tsubu $sp,$sp,8",
                f"\ts.d $f0,0($sp)",
            ]
        return code

    @staticmethod
    def gte_operation(symbol_table, expr):
        code = []
        code += expr.l_operand.cgen(symbol_table)
        code += expr.r_operand.cgen(symbol_table)
        l_operand_type = CodeGenerator.get_type(expr.l_operand, symbol_table)

        if l_operand_type == "int":
            code += [
                f"\tlw $t0,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code += [
                f"\tlw $t1,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code.append("\tsge $t2,$t1,$t0")
            code.append("\tsw	$t2, printBoolVal # store contents of register $t2 into RAM=")  # todo should be check

        return code

    @staticmethod
    def addition_operation(symbol_table, expr):
        code = []
        code += expr.l_operand.cgen(symbol_table)
        code += expr.r_operand.cgen(symbol_table)

        l_operand_type = CodeGenerator.get_type(expr.l_operand, symbol_table)
        if l_operand_type == "int":
            code += [
                f"\tlw $t0,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code += [
                f"\tlw $t1,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code.append("\tadd $t2,$t1,$t0")
            code.append("\tsw	$t2, printIntVal # store contents of register $t2 into RAM=")  # todo should be check
        else:
            code += [
                f"\tl.d $f0,0($sp)# move top stack to f0",
                f"\taddu $sp,$sp,8\t# move sp higher cause of pop",
            ]
            code += [
                f"\tl.d $f2,0($sp)# move top stack to f2",
                f"\taddu $sp,$sp,8\t# move sp higher cause of pop",
            ]
            code.append("add.d $f4, $f2, $f0")
            code += [
                f"\tsubu $sp,$sp,8",
                f"\ts.d $f4,0($sp)",
            ]
        return code

    @staticmethod
    def add_plus(symbol_table):
        pass

    @staticmethod
    def subtraction_operation(symbol_table, expr):
        code = []
        code += expr.l_operand.cgen(symbol_table)
        code += expr.r_operand.cgen(symbol_table)

        l_operand_type = CodeGenerator.get_type(expr.l_operand, symbol_table)

        if l_operand_type == "int":
            code += [
                f"\tlw $t0,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code += [
                f"\tlw $t1,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code.append("sub $t2,$t1,$t0")
            code.append("sw	$t2, printIntVal # store contents of register $t2 into RAM=")  # todo should be check


        return code

    @staticmethod
    def minus_plus(symbol_table):
        pass

    @staticmethod
    def multiplication_operation(symbol_table, expr):
        code = []

        code += expr.l_operand.cgen(symbol_table)
        code += expr.r_operand.cgen(symbol_table)

        l_operand_type = CodeGenerator.get_type(expr.l_operand, symbol_table)
        if l_operand_type == "int":
            code += [
                f"\tlw $t0,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code += [
                f"\tlw $t1,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code.append("\tmul $t2,$t1,$t0")
            code.append("\tsw	$t2, printIntVal # store contents of register $t2 into RAM=")  # todo should be check


        return code

    @staticmethod
    def mul_plus(symbol_table):
        pass

    @staticmethod
    def division_operation(symbol_table, expr):
        code = []
        code += expr.l_operand.cgen(symbol_table)
        code += expr.r_operand.cgen(symbol_table)
        if expr.l_operand.v_type == "int":
            code += [
                f"\tlw $t0,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]
            code += [
                f"\tlw $t1,4($sp)\t#copy top stack to t0",
                f"\taddu $sp,$sp,4\t# move sp higher cause of pop",
            ]

            code.append("\tdiv $t2,$t1,$t0")
            code.append(f"\tsw	$t2, {printIntVal} # store contents of register $t2 into RAM=")  # todo should be check



        return code

    @staticmethod
    def divide_plus(symbol_table):
        pass

    @staticmethod
    def modulo_operation(symbol_table, expr):

        return code

    @staticmethod
    def baghi_plus(symbol_table):
        pass

    @staticmethod
    def not_operation(symbol_table):
        pass

    @staticmethod
    def this_expression(symbol_table):
        pass

    @staticmethod
    def read_integer(symbol_table):
        code = ["\tjal _ReadInteger"]
        which_temp = symbol_table.current_scope.int_const_counter % 2
        code += [f"\tsw	$t0, {tempIntVar}{which_temp}  # add from memory to t0"]


        return code

    @staticmethod
    def read_line(symbol_table,tree):
        code = ["\tjal _ReadLine"]
        which_temp = symbol_table.current_scope.string_const_counter % 2
        code += [f"\tsw	$t0, {tempStringVar}{which_temp}  # add from memory to t0"]
        return code


    @staticmethod
    def func_(symbol_table,tree):
        code = []
        symbol_table.current_scope.string_const_counter += 1
        string_const_address_in_data = f"str_const_number{symbol_table.current_scope.string_const_counter}"

        counter = -1
        function_name = symbol_table.current_scope.name.split("_")
        while "block" in function_name[0:counter]:
            counter -= 1

        function_name = symbol_table.current_scope.name.split("_")[counter]

        data = [f"{string_const_address_in_data}: .asciiz {function_name}"]
        symbol_table.data_storage += data
        which_temp = symbol_table.current_scope.string_const_counter % 2
        #find const value to stack
        code = [
            f"\tla $t0, {string_const_address_in_data}\t# load constant value to $t0",
            f"\tsw $t0, {tempStringVar}{which_temp}\t# load constant value from $to to temp",
        ]

        return code


    @staticmethod
    def line_(symbol_table,tree):
        code = []
        symbol_table.current_scope.string_const_counter += 1
        string_const_address_in_data = f"str_const_number{symbol_table.current_scope.string_const_counter}"
        data = [f"{string_const_address_in_data}: .asciiz \"2\" "]  #todo should be cheked
        symbol_table.data_storage += data
        which_temp = symbol_table.current_scope.string_const_counter % 2
        #find const value to stack
        code = [
            f"\tla $t0, {string_const_address_in_data}\t# load constant value to $t0",
            f"\tsw $t0, {tempStringVar}{which_temp}\t# load constant value from $to to temp",
        ]

        return code

    @staticmethod
    def initiate_class(symbol_table):
        pass

    @staticmethod
    def assignment(symbol_table, assign):
        code = []
        l_identifier_type = CodeGenerator.get_type(assign.l_value, symbol_table)
        r_identifier_type = CodeGenerator.get_type(assign.expr, symbol_table)


        if r_identifier_type != l_identifier_type and r_identifier_type is not None:
            raise  Exception("Semantic Error type 1")
            return code

        if type(assign.expr).__name__ == "ReadInteger":
            code += CodeGenerator.read_integer(symbol_table)
            if l_identifier_type is not None:
                find_symbol_in_memory = symbol_table.current_scope.find_symbol_path(assign.l_value.identifier.name) # if return , means we have this symbol
                symbol_path = find_symbol_in_memory.root_generator() + "__" + assign.l_value.identifier.name  # return root path
                code += [f"\tsw	$t0 , {symbol_path}  # add from memory to t0"]


        if type(assign.expr).__name__ == "ReadLine":
            code += CodeGenerator.read_line(symbol_table)
            if l_identifier_type is not None:
                find_symbol_in_memory = symbol_table.current_scope.find_symbol_path(assign.l_value.identifier.name) # if return , means we have this symbol
                symbol_path = find_symbol_in_memory.root_generator() + "__" + assign.l_value.identifier.name  # return root path
                code += [f"\tsw	$t0 , {symbol_path}  # add from memory to t0"]

        if type(assign.expr).__name__ == "Expression":
            code += assign.expr.cgen(symbol_table)
            find_symbol_in_memory = symbol_table.current_scope.find_symbol_path(assign.l_value.identifier.name)  # if return , means we have this symbol
            symbol_path = find_symbol_in_memory.root_generator() + "__" + assign.l_value.identifier.name  # return root path
            code += [f"\tsw	$t0 , {symbol_path}  # add from memory to t0"]

        if type(assign.expr).__name__ == "IdentifierLValue":
            return code

        if type(assign.expr).__name__ == "Const":
            if r_identifier_type == TYPE_IS_INT:
                code += CodeGenerator.int_const(symbol_table, assign.expr)
                which_temp = symbol_table.current_scope.int_const_counter % 2
                code +=[f"\tlw	$t0, {tempIntVar}{which_temp}  # add from memory to t0"]
                find_symbol_in_memory = symbol_table.current_scope.find_symbol_path(assign.l_value.identifier.name) # if return , means we have this symbol
                symbol_path = find_symbol_in_memory.root_generator() + "__" + assign.l_value.identifier.name  # return root path
                code += [f"\tsw	$t0 , {symbol_path}  # add from memory to t0"]
            elif r_identifier_type == TYPE_IS_STRING:
                code += CodeGenerator.string_const(symbol_table,assign.expr)
                which_temp = symbol_table.current_scope.string_const_counter % 2
                code +=[f"\tlw	$t0, {tempStringVar}{which_temp}  # add from memory to t0"]
                find_symbol_in_memory = symbol_table.current_scope.find_symbol_path(assign.l_value.identifier.name) # if return , means we have this symbol
                symbol_path = find_symbol_in_memory.root_generator() + "__" + assign.l_value.identifier.name  # return root path
                code += [f"\tsw	$t0 , {symbol_path}  # add from memory to t0"]

            # elif r_identifier_type == TYPE_IS_DOUBLE:          #todo should be compelete
            #     code += double_const(symbol_table,assign.expr)
            # elif r_identifier_type == TYPE_IS_BOOL:
            #     code += bool_const(symbol_table,assign.expr)
            # elif r_identifier_type == TYPE_IS_NULL:
            #     code += null_const(symbol_table,assign.expr)
            # elif r_identifier_type == TYPE_IS_STRING:
            #     code += string_const(symbol_table,assign.expr)
        return code

    @staticmethod
    def identifier_l_value(symbol_table):
        pass

    @staticmethod
    def member_access_l_value(symbol_table):
        pass

    @staticmethod
    def array_access_l_value(symbol_table):

        pass

    @staticmethod
    def identifier_l_value(symbol_table):
        pass

    @staticmethod
    def function_call(symbol_table,function):
        code = []

        symbol_table.current_scope.find_function(function.identifier.name)
        code += [f"\tjal {function.identifier.name}"]
        return code

    @staticmethod
    def method_call(symbol_table):
        pass

    @staticmethod
    def identifier(symbol_table):
        pass

    @staticmethod
    def new_identifier(symbol_table):
        pass

    @staticmethod
    def int_const(symbol_table,constant):
        symbol_table.current_scope.int_const_counter += 1
        which_temp = symbol_table.current_scope.int_const_counter % 2
        code = [
            f"\tli $t0, {constant.value}\t# load constant value to $t0",
            f"\tsw $t0, {tempIntVar}{which_temp}\t# load constant value from $to to temp",
        ]
        return code

    @staticmethod
    def double_const(symbol_table,constant):
        pass

    @staticmethod
    def bool_const(symbol_table,constant):
        code = ["cgen bool const"]
        return code

    @staticmethod
    def null_const(symbol_table):
        pass

    @staticmethod
    def string_const(symbol_table,constant):
        symbol_table.current_scope.string_const_counter += 1
        string_const_address_in_data = f"str_const_number{symbol_table.current_scope.string_const_counter}"
        data = [f"{string_const_address_in_data}: .asciiz {constant.value}"]
        symbol_table.data_storage += data
        which_temp = symbol_table.current_scope.string_const_counter % 2
        #find const value to stack
        code = [
            f"\tla $t0, {string_const_address_in_data}\t# load constant value to $t0",
            f"\tsw $t0, {tempStringVar}{which_temp}\t# load constant value from $to to temp",
        ]
        return code
