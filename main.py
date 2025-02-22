#https://blog.miguelgrinberg.com/post/building-a-toy-programming-language-in-python

#arg many

#errors array
#errors test
#optimization
#pilniga lokalizacija
#stack reorganization

#array

#comments in code

class lv:
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

    def __init__(self, code):
        self.code = code
        self.token_feed = self.tokens()
        self.token_memory = []
        self.returned_token = None
        self.line_nr = 0
        self.stack = []
        self.stack_numbers = []
        self.vars = {}

    def process_string_in_code(self,code):

        #print(code.split('\n'))#.encode('cp850', errors='replace').decode('cp850'))

        #for line in code.strip().split('\n'):
        #    for token in line.strip().split(' '):
        #        print(token)

        #delete first empty lines
        #while code[0:1] == "\n":
        #    code = code[1:]

        #delete rest empty lines
        #while code.find("\n\n") != -1:
        #    code = str(code).replace('\n\n','\n')

        #delete comments
        #code_ready = ""
        #code_array = code.strip().split('\n')
        #for line in code_array:
        #    if line[0] != "@":
        #        code_ready += line+"\n"
        #code_ready = code_ready[:-1]

        #prepare string
        code_ready = ""
        str_detected = False
        for char in code:
            if char == '"':
                if str_detected == True:
                    str_detected = False
                else:
                    str_detected = True
            
            if str_detected == False:
                code_ready += char
            else:
                if char == " ":
                    code_ready += "_"
                else:
                    code_ready += char

        #print(code_ready_copy.strip().split('\n'))
        
        return code_ready

    def process_string_in_token(self, str):
        str = str.replace("_"," ")
        str = str.replace('"',"")
        return str

    def raise_error(self, message):
        raise ValueError(f'{message}, uz rindas {self.line_nr}')

    def tokens(self):
        self.code = self.process_string_in_code(self.code)

        for line in self.code.split('\n'):
            self.line_nr += 1
            for token in line.split(' '):

                if token == "":
                    break
                elif token[0] == "@":
                    break

                if token in ['raksti', 'jaunlīnija', 'cikls', 'ja', 'vai', 'vel', 'ir', '>', '<', '++', '--', '=', '+', '-', '*', '/']:
                    yield (token,)
                elif token.isnumeric():
                    yield ('int', int(token))
                elif token[0] == '"' and token[-1] == '"':
                    yield ('string', self.process_string_in_token(token))
                elif token == "patiess":
                    yield ('bool', int(1))
                elif token == "aplams":
                    yield ('bool', int(0))
                elif token == "veids":
                    yield ('function', token)
                elif token == "zimet":
                    yield ('function', token)
                elif token.isalpha() and token[0] != '"' and token[-1] != '"':
                    yield ('variable', token)
                else:
                    self.raise_error(f'Nepareizs tokens {token}')
            yield ('\n',)

    def next_token(self):
        if self.returned_token:
            token = self.returned_token
            self.returned_token = None
        else:
            if len(self.token_memory) > 0:
                    token = self.token_memory[0]
                    self.token_memory.pop(0)
                    return token
            try:
                token = next(self.token_feed)
            except StopIteration:
                token = None
        return token

    def return_token(self, token):
        if self.returned_token is not None:
            raise RuntimeError('Cannot return more than one token at a time')
        self.returned_token = token

    def stack_calculate(self, next_operator=None):
        op_precedence = 0 if next_operator is None else \
            self.precedence[next_operator]
        while len(self.stack_numbers) > 1 and self.stack_numbers[-2][1] > op_precedence:
            value2 = self.stack_numbers.pop()
            prev_op = self.stack_numbers.pop()[0]
            value1 = self.stack_numbers.pop()
            if prev_op == '+':
                self.stack_numbers.append(value1 + value2)
            elif prev_op == '-':
                self.stack_numbers.append(value1 - value2)
            elif prev_op == '*':
                self.stack_numbers.append(value1 * value2)
            elif prev_op == '/':
                self.stack_numbers.append(value1 // value2)
        return self.stack_numbers.pop()

    def stack_collapse(self):

        #print(self.stack)

        func_stack = []
        string_stack = []
        other_stack = []
        is_operated = []

        for token in self.stack:
            if token[0] == "string":
                string_stack.append(token)
            elif token[0] == "function":
                func_stack.append(token)
            elif token[0] == "int":
                self.stack_numbers.append(token[1])
            elif token[0] == "bool":
                self.stack_numbers.append(token[1])
                other_stack.append(token)
            elif token[0] in ['+', '-', '*', '/']:
                is_operated.append(token[0])
                if len(string_stack) == 0:
                    self.stack_numbers.append(self.stack_calculate(next_operator=token[0]))
                    self.stack_numbers.append((token[0], self.precedence[token[0]]))

        #print(string_stack)

        #number stack
        if len(self.stack_numbers) > 0:
            self.stack_push(("int",self.stack_calculate()))

        #string stack
        string_res = ""
        if len(string_stack) > 0 and '+' in is_operated:
            while len(string_stack) > 0:
                string_res += string_stack.pop(0)[1]
            self.stack_push(("string",string_res))

        #bool bug kostil
        if len(other_stack) == 1 and other_stack[0][0] == "bool" and len(is_operated) == 0:
            con = self.stack.pop()
            con = list(con)
            con[0] = "bool"
            con = tuple(con)
            self.stack_push(con)

        #function stack
        while len(func_stack) > 0:
            match func_stack.pop()[1]:
                case "veids":
                    v1 = self.stack.pop()
                    if v1[0] == "function":
                        self.raise_error('Paredzams funkcijas arguments')

                    v2 = self.stack.pop()

                    self.stack_push(("string", v1[0]))
                case "zimet":
                    v1 = self.stack.pop()
                    if v1[0] == "function":
                        self.raise_error('Paredzams funkcijas arguments')

                    v2 = self.stack.pop()

                    if v1[0] != "int":
                        self.raise_error('Nepareizs funkcijas arguments')

                    self.stack_push(("string", "<>"*v1[1]))

        output = self.stack.pop()
        self.stack = []

        return output

    def parse_program(self):
        token = self.next_token()
        while token is not None:
            self.return_token(token)

            if not self.parse_statement():
               self.raise_error('Paredzams apgalvojums')
            token = self.next_token()
        return True
    
    def parse_statement(self):
        token = self.next_token()
        if token[0] == '\n':
            return True
        else:
            self.return_token(token)

        if not self.parse_print_statement() and not self.parse_function_statement() and not self.parse_assignment() and not self.parse_newline_statement() and not self.parse_if_statement() and not self.parse_for_loop_statement():
            self.raise_error('Paredzams apgalvojums, mainigo pieskirsana, funkcija vai cikls')
        token = self.next_token()

        if token is not None:
            while token[0] != '\n':
                token = self.next_token()
        return True

    def parse_for_loop_statement(self):
        token = self.next_token()
        if token[0] != 'cikls':
            self.return_token(token)
            return False

        token = self.next_token()
        counter = 0

        if token[0] == 'variable':
            if token[1] not in self.vars:
                self.raise_error(f'Sintakses kluda: Nezinams mainigais {token[1]}')
            else:
                counter = self.vars[token[1]]
        elif token[0] == "int": 
            counter = token[1]
        else:
            self.raise_error(f'Sintakses kluda: Paredzams mainigais')

        token_memory = [('\n',)]
        token = self.next_token()
        while token[0] != '\n':
            if token[0] == 'vel':
                token_memory.append(('\n',))
            else:
                token_memory.append(token)
            token = self.next_token()

        token_memory = token_memory*counter
        token_memory.append(('\n',))

        self.token_memory = token_memory

        return True

    def parse_if_statement(self):
        token = self.next_token()
        if token[0] != 'ja':
            self.return_token(token)
            return False
        
        token = self.next_token()
        identifier = ""

        if token[0] == 'variable':
            if token[1] not in self.vars:
                self.raise_error(f'Sintakses kluda: Nezinams mainigais {token[1]}')
            else:
                identifier = self.vars[token[1]]
        else: 
            self.raise_error(f'Sintakses kluda: Paredzams mainigais')

        token = self.next_token()
        if token[0] != 'ir' and token[0] != '>' and token[0] != '<':
            self.raise_error('Paredzams: ir, >, <')
        if token[0] == '>' and identifier[0] != 'int' or token[0] == '<' and identifier[0] != 'int':
            self.raise_error('Paredzams skaitliskais mainigais')

        instruction = token[0]
        comparison = self.next_token()
        if comparison[0] != 'int':
            self.raise_error('Paredzama skaitliska vertiba')

        token_memory_if = [('\n',)]
        token_memory_else = [('\n',)]
        token = self.next_token()

        while token[0] != '\n' and token[0] != 'vai':
            if token[0] == 'vel':
                token_memory_if.append(('\n',))
            else:
                token_memory_if.append(token)
            token = self.next_token()
        token_memory_if.append(('\n',))
        
        if token[0] == 'vai':
            token = self.next_token()
            while token[0] != '\n':
                if token[0] == 'vel':
                    token_memory_else.append(('\n',))
                else:
                    token_memory_else.append(token)
                token = self.next_token()
            token_memory_else.append(('\n',))

        match instruction:
            case 'ir':
                if identifier == comparison:
                    self.token_memory = token_memory_if
                else:
                    self.token_memory = token_memory_else
            case '>':
                if identifier > comparison:
                    self.token_memory = token_memory_if
                else:
                    self.token_memory = token_memory_else
            case '<':
                if identifier < comparison:
                    self.token_memory = token_memory_if
                else:
                    self.token_memory = token_memory_else

        return True

    def parse_newline_statement(self):
        token = self.next_token()
        if token[0] != 'jaunlīnija':
            self.return_token(token)
            return False
        print("")
        return True

    def parse_print_statement(self):
        token = self.next_token()
        if token[0] != 'raksti':
            self.return_token(token)
            return False
        if not self.parse_expression():
            self.raise_error('Paredzama izteiksme')

        value = self.stack_collapse()[1]

        print(value)
        return True
    
    def parse_function_statement(self):
        token = self.next_token()
        if token[0] != 'function':
            self.return_token(token)
            return False
        self.stack_push(token)
        
        if not self.parse_expression():
            self.raise_error('Paredzama izteiksme')

        value = self.stack_collapse()[1]
        print(value)
 
        """match token[1]:
            case "veids":
                token = self.next_token()
                if token[0] == "":
                    self.raise_error('Paredzams arguments')
                else:
                    self.return_token(token)
                
                token = self.next_token()
                print(token[0])  

            case "zimēt":
                token = self.next_token()
                if token[0] != 'int':
                    self.raise_error('Paredzams arguments')
                else:
                    self.return_token(token)

                if not self.parse_expression():
                    self.raise_error('Paredzama izteiksme')

                value = self.stack_collapse()
                if value[0] != "int":
                    self.raise_error('Nepareizs funkcijas arguments')
                print("<>"*value[1])  
            """

        return True

    def parse_expression(self):
        if self.parse_value() or self.parse_function():
            self.parse_expression()
        if self.parse_operator():
            self.parse_expression()
        return True
    
    def parse_function(self):
        token = self.next_token()
        if token[0] != "function":
            self.return_token(token)
            return False
        
        self.stack_push(token)
        return True

    def parse_value(self):
        token = self.next_token()
        if token[0] not in ['int', 'string', 'bool', 'variable']:
            self.return_token(token)
            return False

        if token[0] == 'variable':
            if token[1] not in self.vars:
                self.raise_error(f'Sintakses kluda: Nezinams mainigais {token[1]}')
            else:
                self.stack_push(self.vars[token[1]])
        else:
            self.stack_push(token)

        return True

    def parse_operator(self):
        token = self.next_token()
        if token[0] not in ['+', '-', '*', '/']:
            self.return_token(token)
            return False

        self.stack_push(token)
        return True

    def parse_assignment(self):
        token = self.next_token()
        if token[0] != 'variable':
            self.return_token(token)
            return False
        identifier = token[1]
    
        token = self.next_token()
        if token[0] != '=' and token[0] != '++' and token[0] != '--':
            self.raise_error('Paredzams =, ++, -- pec mainigaja '+identifier)

        if token[0] == '=':
            if not self.parse_expression():
                self.raise_error('Paredzama izteiksme')
            self.vars[identifier] = self.stack_collapse()
            self.stack = []
        elif token[0] == '++':
            if self.vars[identifier][0] != 'int':
                self.raise_error('Paredzams skaitliskais mainigais')
            self.vars[identifier] = ('int',self.vars[identifier][1]+1)
        elif token[0] == '--': 
            if self.vars[identifier][0] != 'int':
                self.raise_error('Paredzams skaitliskais mainigais')
            self.vars[identifier] = ('int',self.vars[identifier][1]-1)
        
        return True 

    def run(self):
        try:
            return self.parse_program()
        except ValueError as exc:
            print(str(exc))
            return False

    def stack_push(self, arg):
        self.stack.append(arg)

    def stack_pop(self):
        return self.stack.pop()


if __name__ == '__main__':
    f = open("tests.lv", "r", encoding="utf-8")
    program = lv(f.read())
    program.run()
