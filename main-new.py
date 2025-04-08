#https://blog.miguelgrinberg.com/post/building-a-toy-programming-language-in-python

#optimization
#comments in code

#projekta darbs

#sait

class lv:
    precedence = {'+': 1, '-': 1, '*': 2, '/': 2}
    function_arg_count = {'veids': 1, 'zīmēt': 2, 'mainīt': 2}

    def __init__(self, code):
        self.code = code
        self.token_feed = self.tokens()
        self.token_memory = []
        self.returned_token = None
        self.line_nr = 0
        self.stack = []
        self.stack_numbers = []
        self.vars = {}

    def errors_list(self, error_code):
        list_of_errors = {
            'Nepareizs tokens': 'Nepareizs tokens', 
            'Nepareizas iekavas': 'Kodā ir nepareizas saliktas iekavas',
            'Paredzams funkarg': 'Paredzams funkcijas arguments',
            'Nepareizs funkarg': 'Nepareizs funkcijas arguments',
            'Nav tādas funkcijas': 'Nav tādas funkcijas',
            'Paredzams apgalvojums': 'Paredzams apgalvojums',
            'Paredzams kaut-kas': 'Paredzams apgalvojums, vērtību piešķiršana mainīgajam, funkcija vai cikls',
            'Sintakses kļūda: Nez mainīgais': 'Sintakses kļūda: Nezināms mainīgais',
            'Sintakses kļūda: Par mainīgais': 'Sintakses kļūda: Paredzams mainīgais',
            'Paredzams: ir, >, <': 'Paredzams: ir, >, <',
            'Paredzams skait mainīgais': 'Paredzams skaitliskais mainīgais',
            'Paredzama skait vērtība': 'Paredzama skaitliskā vērtība',
            'Paredzama izt': 'Paredzama izteiksme',
            'Paredzams =, ++, -- pec mainīgaja': 'Paredzams =, ++, -- pec mainīgaja',
            'Paredzama skait vērtība': 'Paredzama skaitliskā vērtība',
            'Nav zīmes': 'Starp tiem jābūt kādam operatoram',
            'Kodā nedrīkst būt divas atstarpes': 'Kodā nedrīkst būt divas atstarpes',
            'Nepareizs argumentu skaits': 'Nepareizs argumentu skaits',
            'Nepareizs mainīšanas tips': 'Nepareizs mainīšanas tips'
                        }
        
        return list_of_errors[error_code]

    def utf8_string(self, value):
        string = str(value)
        string = str(string.encode('utf-8'))
        string = string[2:-1]
        return string

    def process_string_in_code(self,code):
        #prepare string
        code_ready = ""
        str_detected = False
        line = 1
        last_char = ""

        for char in code:
            if last_char == " " and char == " " and str_detected == False:
                self.raise_error(f'{self.errors_list("Kodā nedrīkst būt divas atstarpes")}, uz rindas {line}')

            if char == '"':
                if str_detected == True:
                    str_detected = False
                else:
                    str_detected = True

            if char == '\n' and str_detected == False:
                line += 1
            elif char == '\n' and str_detected == True:
                self.raise_error(f'{self.errors_list("Nepareizas iekavas")}, uz rindas {line}')
            
            if str_detected == False:
                code_ready += char
            else:
                if char == " ":
                    code_ready += "_"
                else:
                    code_ready += char
            
            last_char = char
        
        return code_ready

    def process_string_in_token(self, str):
        str = str.replace("_"," ")
        str = str.replace('"',"")
        return str

    def raise_error(self, message):
        with open("Kļūdu ziņojums.txt", "w", encoding="utf-8") as file:
            file.write(message)

        message = str(message.encode('utf-8'))
        message = message[2:-1]
        raise ValueError(f'{message}')

    def tokens(self):
        self.code = self.process_string_in_code(self.code)

        for line in self.code.split('\n'):
            self.line_nr += 1

            for token in line.split(' '):
                if token == "":
                    break
                elif token[0] == "@":
                    break

                if token in ['raksti', 'jaunlīnija', 'cikls', 'ja', 'vai', 'vēl', 'ir', '>', '<', '++', '--', '=', '+', '-', '*', '/']:
                    yield (token,)
                elif token.isnumeric():
                    yield ('veselnieks', int(token))
                elif token[0] == '"' and token[-1] == '"':
                    yield ('rinda', self.process_string_in_token(token))
                elif token.find(".") != -1:
                    yield ('pludiņi', float(token))
                elif token == "patiess":
                    yield ('buls', int(1))
                elif token == "aplams":
                    yield ('buls', int(0))
                elif token == "veids":
                    yield ('funkcija', token)
                elif token == "zīmēt":
                    yield ('funkcija', token)
                elif token == "mainīt":
                    yield ('funkcija', token)
                elif token.isalpha() and token[0] != '"' and token[-1] != '"':
                    yield ('mainīgais', token)
                else:
                    self.raise_error(f'{self.errors_list("Nepareizs tokens")} {token}, uz rindas {self.line_nr}')
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
                self.stack_numbers.append(value1 / value2)
        return self.stack_numbers.pop()

    def stack_collapse(self):

        #print(self.stack)

        last_token = []
        args = []
        args_temp = []
        arg_count = 0

        self.stack_numbers = []
        

        ### sadalit pa args
        for token in self.stack:
            if (len(args) == 0) and token[0] == "funkcija":
                args_temp.append(token)
                args.append(args_temp)
                args_temp = []
            else:
                if len(args_temp) != 0 and args_temp[-1] in ['rinda', 'veselnieks', 'buls', 'pludiņi'] and token[0] not in ['funkcija', '+', '-', '*', '/']:
                    self.raise_error(f'{self.errors_list("Nav zīmes")}, uz rindas {self.line_nr}')

                if token[0] in ['funkcija']:
                    if len(args_temp) != 0:
                        args.append(args_temp)
                        args_temp = []

                    arg_count = self.function_arg_count[token[1]]
                    args_temp.append(token)

                if arg_count > 0 and token[0] not in ['funkcija']:
                    args_temp.append(token)
                    arg_count -= 1

                    if arg_count == 0:
                        args.append(args_temp)
                        args_temp = []
                
                elif arg_count == 0:
                    if token[0] in ['rinda', 'veselnieks', 'buls', 'pludiņi'] and len(last_token) != 0 and last_token[0] in ['rinda', 'veselnieks', 'buls', 'pludiņi'] and len(args_temp) != 0:
                        args.append(args_temp)
                        args_temp = []

                    args_temp.append(token)

            last_token = token

        if len(args_temp) != 0:
            args.append(args_temp)
            
        ###

        #print(args_temp)

        ### args proccesing

        args_temp = []
        for arg in args:
            if len(arg) > 1 and (('+',) in arg or ('-',) in arg or ('*',) in arg or ('/',) in arg) and not any('rinda' in sublist for sublist in arg):
                for token in arg:
                    if token[0] == "veselnieks" or token[0] == "buls" or token[0] == "pludiņi":
                        self.stack_numbers.append(token[1])
                    if token[0] in ['+', '-', '*', '/']:
                        self.stack_numbers.append(self.stack_calculate(next_operator=token[0]))
                        self.stack_numbers.append((token[0], self.precedence[token[0]]))

                value = self.stack_calculate()
                if isinstance(value, int):
                    args_temp.append([("veselnieks", value)])
                elif isinstance(value, float):
                    args_temp.append([("pludiņi", value)])
            
            elif len(arg) > 1 and ('+',) in arg and any('rinda' in sublist for sublist in arg):
                string = ""
                for token in arg:
                    if token[0] == "rinda" or token[0] == "veselnieks" or token[0] == "pludiņi":
                        string += str(token[1])
                args_temp.append([("rinda",string)])

            elif len(arg) > 1 and arg[0][0] == "funkcija":
                args_temp.append([self.function_option(arg[0][1], [arg[1::]])])

            else:
                args_temp.append(arg)

        args = args_temp
        ###

        #first function stack
        if args[0][0][0] == "funkcija":
            self.stack_push(self.function_option(args[0][0][1], args[1::]))
            output = self.stack.pop()
        else:
            output = args.pop()[0]

        self.stack = []

        return output

    def function_option(self, function_name, args):
        match function_name:
            case "veids":
                if len(args) != 1:
                    self.raise_error(f'{self.errors_list("Nepareizs argumentu skaits")}, uz rindas {self.line_nr}')

                arg = args[0][0]
                if arg[0] == "funkcija":
                    self.raise_error(f'{self.errors_list("Paredzams funkarg")}, uz rindas {self.line_nr}')

                return ("rinda", arg[0])

            case "zīmēt":
                if len(args) != 2:
                    self.raise_error(f'{self.errors_list("Nepareizs argumentu skaits")}, uz rindas {self.line_nr}')

                arg = args[0][0]
                count = args[1][0]
                if arg[0] == "funkcija":
                    self.raise_error(f'{self.errors_list("Paredzams funkarg")}, uz rindas {self.line_nr}')
                if count[0] != "veselnieks":
                    self.raise_error(f'{self.errors_list("Nepareizs funkarg")}, uz rindas {self.line_nr}')

                return ("rinda", str(arg[1])*count[1]) 
            
            case "mainīt":
                if len(args) != 2:
                    self.raise_error(f'{self.errors_list("Nepareizs argumentu skaits")}, uz rindas {self.line_nr}')

                arg = args[0][0]
                type = args[1][0]
                if arg[0] == "funkcija":
                    self.raise_error(f'{self.errors_list("Paredzams funkarg")}, uz rindas {self.line_nr}')
                if type[0] == "funkcija":
                    self.raise_error(f'{self.errors_list("Paredzams funkarg")}, uz rindas {self.line_nr}')

                match type[1]:
                    case "veselnieks":
                        if arg[0] == "rinda" or arg[0] == "buls":
                            self.raise_error(f'{self.errors_list("Nepareizs mainīšanas tips")}, uz rindas {self.line_nr}')
                        return ("veselnieks", int(arg[1]))
                    case "pludiņi":
                        if arg[0] == "rinda" or arg[0] == "buls":
                            self.raise_error(f'{self.errors_list("Nepareizs mainīšanas tips")}, uz rindas {self.line_nr}')
                        return ("pludiņi", float(arg[1])) 
                    case "rinda":
                        return ("rinda", str(arg[1])) 
                    case "buls":
                        if arg[0] != "veselnieks" and arg[0] != "pludiņi":
                            self.raise_error(f'{self.errors_list("Nepareizs mainīšanas tips")}, uz rindas {self.line_nr}')
                        if int(arg[1]) != 0 and int(arg[1]) != 1:
                            self.raise_error(f'{self.errors_list("Nepareizs mainīšanas tips")}, uz rindas {self.line_nr}')
                        return ("buls", int(arg[1]))
                
                self.raise_error(f'{self.errors_list("Nepareizs funkarg")}, uz rindas {self.line_nr}')
        
        self.raise_error(f'{self.errors_list("Nav tādas funkcijas")}, uz rindas {self.line_nr}')

    def parse_program(self):
        token = self.next_token()
        while token is not None:
            self.return_token(token)

            if not self.parse_statement():
               self.raise_error(f'{self.errors_list("Paredzams apgalvojums")}, uz rindas {self.line_nr}')
            token = self.next_token()
        return True
    
    def parse_statement(self):
        token = self.next_token()
        if token[0] == '\n':
            return True
        else:
            self.return_token(token)

        if not self.parse_print_statement() and not self.parse_function_statement() and not self.parse_assignment() and not self.parse_newline_statement() and not self.parse_if_statement() and not self.parse_for_loop_statement():
            self.raise_error(f'{self.errors_list("Paredzams kaut-kas")}, uz rindas {self.line_nr}')
            
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

        if token[0] == 'mainīgais':
            if token[1] not in self.vars:
                self.raise_error(f'{self.errors_list("Sintakses kļūda: Nez mainīgais")} {token[1]}, uz rindas {self.line_nr}')
            else:
                counter = self.vars[token[1]]
        elif token[0] == "veselnieks": 
            counter = token[1]
        else:
            self.raise_error(f'{self.errors_list("Sintakses kļūda: Par mainīgais")}, uz rindas {self.line_nr}')

        token_memory = [('\n',)]
        token = self.next_token()
        while token[0] != '\n':
            if token[0] == 'vēl':
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

        if token[0] == 'mainīgais':
            if token[1] not in self.vars:
                self.raise_error(f'{self.errors_list("Sintakses kļūda: Nez mainīgais")} {token[1]}, uz rindas {self.line_nr}')
            else:
                identifier = self.vars[token[1]]
        else:
            identifier = token
            #self.raise_error(f'{self.errors_list("Sintakses kļūda: Par mainīgais")}, uz rindas {self.line_nr}')

        token = self.next_token()
        if token[0] != 'ir' and token[0] != '>' and token[0] != '<':
            self.raise_error(f'{self.errors_list("Paredzams: ir, >, <")}, uz rindas {self.line_nr}')
        if token[0] == '>' and identifier[0] != 'veselnieks' or token[0] == '<' and identifier[0] != 'veselnieks':
            self.raise_error(f'{self.errors_list("Paredzams skait mainīgais")}, uz rindas {self.line_nr}')

        instruction = token[0]
        comparison = self.next_token()
        if (instruction == ">" or instruction == "<") and comparison[0] != 'veselnieks':
            self.raise_error(f'{self.errors_list("Paredzama skait vērtība")}, uz rindas {self.line_nr}')

        token_memory_if = [('\n',)]
        token_memory_else = [('\n',)]
        token = self.next_token()

        while token[0] != '\n' and token[0] != 'vai':
            if token[0] == 'vēl':
                token_memory_if.append(('\n',))
            else:
                token_memory_if.append(token)
            token = self.next_token()
        token_memory_if.append(('\n',))
        
        if token[0] == 'vai':
            token = self.next_token()
            while token[0] != '\n':
                if token[0] == 'vēl':
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
            self.raise_error(f'{self.errors_list("Paredzama izt")}, uz rindas {self.line_nr}')
            
        print(self.utf8_string(self.stack_collapse()[1]))
        return True
    
    def parse_function_statement(self):
        token = self.next_token()
        if token[0] != 'funkcija':
            self.return_token(token)
            return False
        self.stack_push(token)
        
        if not self.parse_expression():
            self.raise_error(f'{self.errors_list("Paredzama izt")}, uz rindas {self.line_nr}')
            
        print(self.utf8_string(self.stack_collapse()[1]))
        return True

    def parse_expression(self):
        if self.parse_value() or self.parse_function():
            self.parse_expression()
        if self.parse_operator():
            self.parse_expression()
        return True
    
    def parse_function(self):
        token = self.next_token()
        if token[0] != "funkcija":
            self.return_token(token)
            return False
        
        self.stack_push(token)
        return True

    def parse_value(self):
        token = self.next_token()
        if token[0] not in ['veselnieks', 'rinda', 'buls', 'mainīgais', 'pludiņi']:
            self.return_token(token)
            return False

        if token[0] == 'mainīgais':
            if token[1] not in self.vars:
                self.raise_error(f'{self.errors_list("Sintakses kļūda: Nez mainīgais")} {token[1]}, uz rindas {self.line_nr}')

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
        if token[0] != 'mainīgais':
            self.return_token(token)
            return False
        identifier = token[1]
    
        token = self.next_token()
        if token[0] != '=' and token[0] != '++' and token[0] != '--':
            self.raise_error(f'{self.errors_list("Paredzams =, ++, -- pec mainīgaja")} {identifier}, uz rindas {self.line_nr}')

        if token[0] == '=':
            if not self.parse_expression():
                self.raise_error(f'{self.errors_list("Paredzama izt")}, uz rindas {self.line_nr}')
            self.vars[identifier] = self.stack_collapse()
            self.stack = []
        elif token[0] == '++':
            if self.vars[identifier][0] != 'veselnieks':
                self.raise_error(f'{self.errors_list("Paredzams skait mainīgais")}, uz rindas {self.line_nr}')
            self.vars[identifier] = ('veselnieks',self.vars[identifier][1]+1)
        elif token[0] == '--': 
            if self.vars[identifier][0] != 'veselnieks':
                self.raise_error(f'{self.errors_list("Paredzams skait mainīgais")}, uz rindas {self.line_nr}')
            self.vars[identifier] = ('veselnieks',self.vars[identifier][1]-1)
        
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
