from flask import Flask, render_template, request
from main import lv

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def index():
    output = ''
    code = ''
    errors = ''

    if request.method == 'POST':
        code = request.form['code']
        code = code.replace("\r","")

        program = lv(code)
        program.run()
        
        output = program.get_output()
        errors = program.get_error()

    return render_template('index.html', code=code, output=output, errors=errors)

if __name__ == '__main__':
    app.run()