import numpy as np
import sympy as sp
from sympy.core.sympify import SympifyError
from typing import Callable, Tuple, Dict
import plotly.graph_objs as go
from scipy.integrate import dblquad

def show_instructions() -> None:
    """
    Exibe as instruções sobre como usar o código e fornece exemplos de funções que podem ser inseridas.
    """
    print("Bem-vindo ao Gerador de Gráfico de Curvas de Nível e Superfícies!")
    print("Este programa permite que você insira uma função matemática de múltiplas variáveis (x, y, z, etc.) e visualize seu gráfico de contorno e/ou superfície.")
    print("\nInstruções:")
    print("1) Insira a função desejada usando 'x', 'y', 'z', etc. como variáveis.")
    print("2) Utilize as funções matemáticas do SymPy, como exp, sin, cos, sqrt, etc.")
    print("3) Fixe valores para variáveis adicionais que não serão plotadas (ex.: z=1).")
    print("4) Não inclua a parte 'f(x,y,...) =' na sua entrada. Apenas insira a expressão matemática.")
    print("5) Use '**' para exponenciação em vez de '^'.")
    print("\nExemplos de funções que você pode inserir:")
    print("  - 'sqrt(x) + y + z'")
    print("  - 'x**2 + y**2 + z**2'")
    print("  - 'sin(x) * cos(y) * z'")
    print("  - 'exp(-x**2 - y**2 + z)'")
    print("\nDigite a função desejada no formato indicado e veja o resultado!")


def parse_function(func_str: str, fixed_vars: Dict[str, float] = None) -> Tuple[Callable[[np.ndarray, np.ndarray], np.ndarray], sp.Expr]:
    """
    Converte uma string de função matemática em uma função Python segura, permitindo a fixação de variáveis.

    Args:
        func_str (str): String da função que o usuário insere.
        fixed_vars (Dict[str, float], optional): Dicionário de variáveis a serem fixadas com seus respectivos valores.

    Returns:
        Callable[[np.ndarray, np.ndarray], np.ndarray]: Função que calcula o valor baseado na entrada x e y, considerando variáveis fixas.
    """
    try:
        variables = sp.symbols('x y ' + ' '.join(fixed_vars.keys() if fixed_vars else []))
        expr = sp.sympify(func_str)
        if fixed_vars:
            expr = expr.subs(fixed_vars)
        func_lambdified = sp.lambdify(('x', 'y'), expr, modules=['numpy'])
        return func_lambdified, expr
    except (SympifyError, TypeError) as e:
        raise ValueError(f"Erro ao interpretar a função: {e}")


def validate_function(func_str: str) -> bool:
    """
    Valida se a string de função fornecida é válida e pode ser convertida em uma função.

    Args:
        func_str (str): String da função que o usuário insere.

    Returns:
        bool: True se a função for válida, False caso contrário.
    """
    try:
        sp.sympify(func_str)
        return True
    except SympifyError:
        return False


def plot_interactive_surface_and_contour(f: Callable[[np.ndarray, np.ndarray], np.ndarray],
                                         expr: sp.Expr,
                                         x_range: Tuple[float, float],
                                         y_range: Tuple[float, float],
                                         resolution: int,
                                         title: str = 'Superfície e Curvas de Nível da Função') -> None:
    """
    Plota tanto a superfície 3D quanto o gráfico de contorno e a curva de nível para a função dada f(x, y).
    Também calcula e exibe o limite, derivada, gradiente, integrais simbólicas/numéricas e máximo/mínimo global.

    Args:
        f (Callable): Função que aceita dois argumentos (x, y) e retorna um valor.
        expr (sp.Expr): Expressão simbólica da função.
        x_range (Tuple): Intervalo para o eixo x (min, max).
        y_range (Tuple): Intervalo para o eixo y (min, max).
        resolution (int): Resolução do gráfico (número de pontos para x e y).
        title (str, optional): Título do gráfico.
    """
    x, y = sp.symbols('x y')
    x_vals = np.linspace(x_range[0], x_range[1], resolution)
    y_vals = np.linspace(y_range[0], y_range[1], resolution)
    X, Y = np.meshgrid(x_vals, y_vals)
    Z = f(X, Y)


    fx = sp.diff(expr, x)
    fy = sp.diff(expr, y)

    fx_func = sp.lambdify((x, y), fx, modules=['numpy'])
    fy_func = sp.lambdify((x, y), fy, modules=['numpy'])

    Z_fx = fx_func(X, Y)
    Z_fy = fy_func(X, Y)

    grad_magnitude = np.sqrt(Z_fx**2 + Z_fy**2)

    integral_x = sp.integrate(expr, x)
    integral_y = sp.integrate(expr, y)
    integral_xy = sp.integrate(expr, (x, x_range[0], x_range[1]), (y, y_range[0], y_range[1]))


    integral_numerica, _ = dblquad(lambda y, x: f(x, y), x_range[0], x_range[1], lambda x: y_range[0], lambda x: y_range[1])


    Z_min = np.min(Z)
    Z_max = np.max(Z)

 
    surface = go.Surface(z=Z, x=X, y=Y, colorscale='inferno', showscale=False)
    contours = go.Contour(z=Z, x=x_vals, y=y_vals, colorscale='inferno', showscale=False)

    layout = go.Layout(
        title=title,
        scene=dict(
            xaxis=dict(title='x'),
            yaxis=dict(title='y'),
            zaxis=dict(title='z')
        ),
        xaxis=dict(title='x'),
        yaxis=dict(title='y'),
        showlegend=True
    )

    fig = go.Figure(data=[surface, contours], layout=layout)

   
    fig.add_trace(go.Scatter3d(x=[X.flatten()[np.argmin(Z)]], y=[Y.flatten()[np.argmin(Z)]], z=[Z_min],
                               mode='markers', marker=dict(size=5, color='green', symbol='circle'),
                               name=f'Mínimo Global: {Z_min:.2f}'))
    fig.add_trace(go.Scatter3d(x=[X.flatten()[np.argmax(Z)]], y=[Y.flatten()[np.argmax(Z)]], z=[Z_max],
                               mode='markers', marker=dict(size=5, color='red', symbol='circle'),
                               name=f'Máximo Global: {Z_max:.2f}'))


    partials_text = f"∂f/∂x = {sp.pretty(fx)}\n∂f/∂y = {sp.pretty(fy)}"
    integrals_text = (f"∫f(x) dx = {sp.pretty(integral_x)}\n"
                      f"∫f(y) dy = {sp.pretty(integral_y)}\n"
                      f"Integral dupla simbólica = {sp.pretty(integral_xy)}\n"
                      f"Integral dupla numérica ≈ {integral_numerica:.2f}")
    limit_x0_y0 = sp.limit(expr, x, 0).limit(y, 0)
    limit_text = f"lim(x→0, y→0) f(x,y) = {sp.pretty(limit_x0_y0)}"


    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=1, color="white"),
        showlegend=True,
        name=f"Derivadas Parciais:\n{partials_text}"
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=1, color="white"),
        showlegend=True,
        name=f"Integrais:\n{integrals_text}"
    ))

    fig.add_trace(go.Scatter(
        x=[None], y=[None],
        mode='markers',
        marker=dict(size=1, color="white"),
        showlegend=True,
        name=f"Limites:\n{limit_text}"
    ))

    fig.show()


show_instructions()

func_str = input("Digite a função que deseja calcular (use x e y como variáveis): ")

if validate_function(func_str):
    fixed_vars = {}
    while True:
        var_input = input("Digite a variável e valor para fixar (ex.: z=1), ou pressione Enter para continuar: ")
        if not var_input:
            break
        var, value = var_input.split('=')
        fixed_vars[var.strip()] = float(value.strip())


    x_range = tuple(map(float, input("Digite o intervalo para o eixo x (ex.: 0 10): ").split()))
    y_range = tuple(map(float, input("Digite o intervalo para o eixo y (ex.: -5 5): ").split()))
    resolution = int(input("Digite a resolução (número de pontos): "))

    user_function, expr = parse_function(func_str, fixed_vars)
    plot_interactive_surface_and_contour(user_function, expr, x_range, y_range, resolution)
else:
    print("Erro: A função inserida é inválida. Por favor, insira uma função válida.")
