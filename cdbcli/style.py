from prompt_toolkit.styles import style_from_dict
from prompt_toolkit.token import Token


style = style_from_dict({
    Token.Command: '#5FFB17 bold',
    Token.Operand: '#f0ffff',
})
