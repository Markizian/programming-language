#https://blog.miguelgrinberg.com/post/building-a-toy-programming-language-in-python


#line_nr

#errors

class My:
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}

    def __init__(self, code):
        self.code = self.clean_up_code(code)
        self.token_feed = self.tokens()
        self.returned_token = None
        self.stack = []
        self.stack_numbers = []
        self.vars = {}

    def clean_up_code(self,code):

        #delete first empty lines
        while code[0:1] == "\n":
            code = code[1:]

        #delete rest empty lines
        while code.find("\n\n") != -1:
            code = str(code).replace('\n\n','\n')

        #delete comments
        code_ready = ""
        code_array = code.strip().split('\n')
        for line in code_array:
            if line[0] != "@":
                code_ready += line+"\n"
        code_ready = code_ready[:-1]

        #prepare string
        code_ready_copy = ""
        str_detected = False
        for char in code_ready:
            if char == '"':
                if str_detected == True:
                    str_detected = False
                else:
                    str_detected = True
            
            if str_detected == False:
                code_ready_copy += char
            else:
                if char == " ":
                    code_ready_copy += "_"
                else:
                    code_ready_copy += char

        #print(code_ready_copy)
        
        return code_ready_copy

    def str_prep(self, str):
        str = str.replace("_"," ")
        str = str.replace('"',"")
        return str

    def raise_error(self, message):
        raise ValueError(f'{message}')

    def tokens(self):
        for line in self.code.strip().split('\n'):
            for token in line.strip().split(' '):
                if token in ['rāķsti', 'nl', 'if', '==', '=', '+', '-', '*', '/']:
                    yield (token,)
                elif token.isnumeric():
                    yield ('int', int(token))
                elif token[0] == '"' and token[-1] == '"':
                    yield ('string', self.str_prep(token))
                elif token == "true":
                    yield ('bool', int(1))
                elif token == "false":
                    yield ('bool', int(0))
                elif token == "type":
                    yield ('function', token)
                elif token == "zimēt":
                    yield ('function', token)
                elif token[0].isalpha() and token[0] != '"' and token[-1] != '"':
                    yield ('variable', token)
                else:
                    self.raise_error(f'Invalid token {token}')
            yield ('\n',)

    def next_token(self):
        if self.returned_token:
            token = self.returned_token
            self.returned_token = None
        else:
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

        func_stack = []
        string_stack = []

        for token in self.stack:
            if token[0] == "rāķsti":
                print_output = True
            elif token[0] == "string":
                string_stack.append(token)
            elif token[0] == "function":
                func_stack.append(token)
            elif token[0] == "int":
                self.stack_numbers.append(token[1])
            elif token[0] == "bool":
                self.stack_numbers.append(token[1])
            elif token[0] in ['+', '-', '*', '/']:
                self.stack_numbers.append(self.stack_calculate(next_operator=token[0]))
                self.stack_numbers.append((token[0], self.precedence[token[0]]))

        if len(self.stack_numbers) > 0:
            self.stack_push(("int",self.stack_calculate()))

        #function stack
        while len(func_stack) > 0:
            match func_stack.pop()[1]:
                case "type":
                    v1 = self.stack.pop()
                    if v1[0] == "function":
                        self.raise_error('Expected argument')

                    v2 = self.stack.pop()

                    self.stack_push(("string", v1[0]))
                case "zimēt":
                    v1 = self.stack.pop()
                    if v1[0] == "function":
                        self.raise_error('Expected argument')

                    v2 = self.stack.pop()

                    if v1[0] != "int":
                        self.raise_error('Expected: invalid argument')

                    self.stack_push(("string", "<>"*v1[1]))

        output = self.stack.pop()
        self.stack = []

        return output

    def parse_program(self):
        if not self.parse_statement():
            self.raise_error('Expected: statement')
        token = self.next_token()
        while token is not None:
            self.return_token(token)
            if not self.parse_statement():
               self.raise_error('Expected: statement')
            token = self.next_token()
        return True
    
    def parse_statement(self):
        if not self.parse_print_statement() and not self.parse_function_statement() and not self.parse_assignment() and not self.parse_newline_statement() and not self.parse_if_statement():
            self.raise_error('Expected: statement, assignment or function')
        token = self.next_token()

        if token is not None:
            while token[0] != '\n':
                token = self.next_token()
        return True
    
    def parse_if_statement(self):
        token = self.next_token()
        if token[0] != 'if':
            self.return_token(token)
            return False
        
        token = self.next_token()
        identifier = ""

        if token[0] == 'variable':
            if token[1] not in self.vars:
                self.raise_error(f'Syntax Error: Unknown variable {token[1]}')
            else:
                identifier = self.vars[token[1]]
        else: 
            self.raise_error(f'Syntax Error: Expected variable')

        token = self.next_token()
        if token[0] != '==':
            self.raise_error('Expected ==')

        comparison = self.next_token()

        if comparison == identifier:
            if not self.parse_statement():
                self.raise_error('Expected: after if statement')
            self.return_token(("\n",))

        return True

    def parse_newline_statement(self):
        token = self.next_token()
        if token[0] != 'nl':
            self.return_token(token)
            return False
        print("")
        return True

    def parse_print_statement(self):
        token = self.next_token()
        if token[0] != 'rāķsti':
            self.return_token(token)
            return False
        if not self.parse_expression():
            self.raise_error('Expected: expression')

        value = self.stack_collapse()[1]

        print(value)
        return True
    
    def parse_function_statement(self):
        token = self.next_token()
        if token[0] != 'function':
            self.return_token(token)
            return False
 
        match token[1]:
            case "type":
                token = self.next_token()
                if token[0] != '\n':
                    self.raise_error('Expected argument')
                else:
                    self.return_token(token)

            case "zimēt":
                token = self.next_token()
                if token[0] != 'int':
                    self.raise_error('Expected argument')
                else:
                    self.return_token(token)

                if not self.parse_expression():
                    self.raise_error('Expected: expression')

                value = self.stack_collapse()
                if value[0] != "int":
                    self.raise_error('Expected: invalid argument')
                print("<>"*value[1])  

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
                self.raise_error(f'Syntax Error: Unknown variable {token[1]}')
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
        if token[0] != '=':
            self.raise_error('Expected =')
        if not self.parse_expression():
            self.raise_error('Expected expression')
        
        self.vars[identifier] = self.stack_collapse()
        self.stack = []
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
    f = open("test.my", "r", encoding="utf-8")
    program = My(f.read())
    program.run()
