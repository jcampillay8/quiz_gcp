import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
from dash import Dash, dcc, html, Input, Output, callback
import dash_auth
import dash_daq as daq
import json
import random

# Define el diccionario de usuarios y contraseñas
VALID_USERNAME_PASSWORD_PAIRS = {
    'user1': 'pin1',
    'user2': 'pin2'
}

theme = dbc.themes.BOOTSTRAP

# Initialize the Dash app with Bootstrap
app = dash.Dash(__name__, prevent_initial_callbacks=True ,external_stylesheets=[theme, dbc.icons.BOOTSTRAP])
auth = dash_auth.BasicAuth(
    app,
    VALID_USERNAME_PASSWORD_PAIRS
)

quiz_path = 'quiz.json'

# Load the quiz data
with open(quiz_path) as f:
    data = json.load(f)


# Add these lines after loading the quiz data
total_questions = 0
correct_answers = 0
incorrect_answers = 0
input_threshold = 10

app.layout = dbc.Container(
    [
        dbc.Row(dbc.Col(html.H1("Quiz_GCP - Digital Leader", className='text-center mb-4'), width=12)),
        html.Div(id='question-index', style={'display': 'none'}),
        dbc.Row(
            [
                dbc.Col(html.H4(id='question', className='text-center mb-4'), width=12),
                dbc.Col(
                            [
                                dcc.Checklist(id='options', inputStyle={"margin-right": "20px"}),
                            ],
                            width={'size': 12, 'offset': 1},  # Ajusta el ancho y el desplazamiento
                        ),
            ],
            className='justify-content-center mb-4',
        ),
        dbc.Row(
            [
dbc.Col(
    [
        html.Button('Submit', id='submit', n_clicks=0, style={'background-color': 'blue', 'color': 'white'}, className='mx-2'),
        html.Button('Next', id='next', n_clicks=0, style={'background-color': 'green', 'color': 'white'}, className='mx-2'),
        html.Span("Filtro", className="mx-2"),  # Agrega un texto "Filtro"
        dcc.Input(id='input_threshold', type='number', value=input_threshold, style={"width": "50px"}),  # Ajusta el ancho del input
        html.Button("Explanation", id="open-explanation", style={'background-color': 'yellow', 'color': 'black'}, className='mx-2'),
        html.Button("Reset Values", id="reset-values", style={'background-color': 'red', 'color': 'white'}, className='mx-2'),  # Botón de reseteo
    ],
    width={'size': 5, 'offset': 1},  # Ajusta el ancho y el desplazamiento
),
dcc.ConfirmDialog(
    id="confirm",
    message="",
),
dcc.ConfirmDialog(  # Cuadro de diálogo de confirmación para resetear los valores
    id="confirm-reset",
    message="¿Seguro que desea resetar los valores?",
),

            ],
            className='justify-content-center',
        ),
        dbc.Col(html.Div(id='answer', className='text-center mt-4'), width={'size': 6, 'offset': 3}),
dbc.Row(
    [
        dbc.Col(
            [
                dbc.Row(html.Div(id='total_questions', className='text-center'), className='mt-2 mb-1'),
                dbc.Row(html.Div(id='correct_answers', className='text-center'), className='mt-2 mb-1'),
                dbc.Row(html.Div(id='incorrect_answers', className='text-center'), className='mt-2 mb-1'),
            ],
            width=4,
            align="start"  # Alinea el contenido de las filas en la parte superior
        ),
            dbc.Col(
                daq.Gauge(
                    id='gauge-value',
                    size=150,
                    showCurrentValue=True,
                    color={"gradient":True,"ranges":{"green":[0,8],"yellow":[8,14],"red":[14,20]}},
                    value=0,
                    label='    ',
                    max=20,
                    min=0,
                    
                ),
                width=4,
            )
    ],
    justify="center",
    align="center",  # Alinea verticalmente el contenido de las columnas en el centro
),
    ],
    fluid=True,
)


@app.callback(
    [Output('question', 'children'),
     Output('options', 'options'),
     Output('options', 'value'),
     Output('question-index', 'children')],
    [Input('next', 'n_clicks')],
    [State('answer', 'children'),
     State('input_threshold', 'value')],
    prevent_initial_call=True
)
def update_question(n_clicks,answer,threshold):
    if n_clicks >= 0 :
        global question_index, total_questions#,input_threshold
        # Selecciona dos índices de preguntas al azar
        question_index1 = random.randint(0, len(data['ques']) - 1)
        question_index2 = random.randint(0, len(data['ques']) - 1)
        
        while data['valores'][question_index1] < threshold or data['valores'][question_index2] < threshold:
            question_index1 = random.randint(0, len(data['ques']) - 1)
            question_index2 = random.randint(0, len(data['ques']) - 1)
            
        # Compara los valores de las dos preguntas
        if data['valores'][question_index1] >= data['valores'][question_index2]:
            question_index = question_index1
        else:
            question_index = question_index2
        question = data['ques'][question_index]
        option_values = data['options'][question_index]
        options = [{'label': val, 'value': i+1} for i, val in enumerate(option_values)]
        if answer == "":
            total_questions += 0  # Incrementa el contador de preguntas
        else:
            total_questions += 1  # Incrementa el contador de preguntas
        return question, options, [], question_index
    return dash.no_update, dash.no_update, dash.no_update, dash.no_update

@app.callback(
    Output('answer', 'children', allow_duplicate=True),
    [Input('submit', 'n_clicks')],
    [State('options', 'value')],
    prevent_initial_call=True
)
def check_answer(n_clicks, values):
    if n_clicks > 0 and values is not None:
        global correct_answers, incorrect_answers
        correct_answer = data['ans'][question_index]
        if isinstance(correct_answer, list):
            if set(values) == set(correct_answer):
                correct_answers += 1
                data['valores'][question_index] -= 1
                with open(quiz_path, 'w') as f:
                    json.dump(data, f, indent=4)
                return dbc.Alert([html.I(className="bi bi-check-circle-fill me-2"),"Correcto!",], color="success", style={"overflow": "auto","whiteSpace": "pre-wrap","font-size": "15px", "margig_top": '10px'}),
            else:
                incorrect_answers += 1
                data['valores'][question_index] += 1
                with open(quiz_path, 'w') as f:
                    json.dump(data, f, indent=4)
                return dbc.Alert([html.I(className="bi bi-exclamation-circle-fill me-2"),"Incorrecto. La respuesta correcta es: {}.".format(correct_answer)], color="danger", style={"overflow": "auto","whiteSpace": "pre-wrap","fontSize": "larger","font-family": "Calibri"})
        else:
            if values[0] == correct_answer:
                correct_answers += 1
                data['valores'][question_index] -= 1
                with open(quiz_path, 'w') as f:
                    json.dump(data, f, indent=4)
                return dbc.Alert([html.I(className="bi bi-check-circle-fill me-2"),"Correcto!",], color="success", style={"overflow": "auto","whiteSpace": "pre-wrap","font-size": "15px", "margig_top": '10px'}),
            else:
                incorrect_answers += 1
                data['valores'][question_index] += 1
                with open(quiz_path, 'w') as f:
                    json.dump(data, f, indent=4)
                return dbc.Alert([html.I(className="bi bi-exclamation-circle-fill me-2"),"Incorrecto. La respuesta correcta es: {}.".format(correct_answer)], color="danger", style={"overflow": "auto","whiteSpace": "pre-wrap","fontSize": "larger","font-family": "Calibri"})
    return dash.no_update


# Agrega estas funciones de devolución de llamada para actualizar los contadores en la interfaz de usuario
@app.callback(
    Output('total_questions', 'children'),
    [Input('next', 'n_clicks')])
def update_total_questions(n_clicks):
    return "Total de preguntas: {}".format(total_questions)

@app.callback(
    Output('correct_answers', 'children'),
    [Input('submit', 'n_clicks')],
    [State('options', 'value')])
def update_correct_answers(n_clicks, value):
    return "Respuestas correctas: {}".format(correct_answers)

@app.callback(
    Output('incorrect_answers', 'children'),
    [Input('submit', 'n_clicks')],
    [State('options', 'value')])
def update_incorrect_answers(n_clicks, value):
    return "Respuestas incorrectas: {}".format(incorrect_answers)

@app.callback(
    Output('gauge-value', 'value'),
    [Input('next', 'n_clicks')],
    [State('question-index', 'children')]
)
def update_gauge(n_clicks, question_index):
    if n_clicks > 0 and question_index is not None:
        return data['valores'][int(question_index)]

    
@app.callback(
    Output('answer', 'children'),
    [Input('next', 'n_clicks')]
)
def clear_answer(n_clicks):
    if n_clicks > 0:
        return ""

@app.callback(
    [Output("confirm", "displayed"), Output("confirm", "message")],
    [Input("open-explanation", "n_clicks")],
    [State("confirm", "displayed"), State("question-index", "children")]
)
def toggle_modal_and_update_message(n_clicks, is_open, question_index):
    if n_clicks > 0:
        # Asegúrate de que question_index sea un número válido y esté dentro de los límites
        question_index = int(question_index)
        if 0 <= question_index < len(data['explanation']):
            return not is_open, data['explanation'][question_index]
    return is_open, ""

@app.callback(
    Output("confirm-reset", "displayed"),
    [Input("reset-values", "n_clicks")]
)
def open_reset_dialog(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        return True
    return False

@app.callback(
    Output("confirm-reset", "message"),
    [Input("confirm-reset", "submit_n_clicks")]
)
def reset_values(n_clicks):
    if n_clicks is not None and n_clicks > 0:
        for i in range(len(data['valores'])):
            data['valores'][i] = 10
        with open(quiz_path, 'w') as f:
            json.dump(data, f, indent=4)
        return "Los valores han sido restablecidos a 10."
    return ""


if __name__ == '__main__':
    app.run_server(debug=True)
