from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token


style = style_from_dict({
    Token.Command: '#33aa33 bold',
    Token.Operand: '#aa3333 bold',
})
