from ulauncher.api.client.Extension import Extension
from ulauncher.api.client.EventListener import EventListener
from ulauncher.api.shared.event import KeywordQueryEvent, ItemEnterEvent
from ulauncher.api.shared.item.ExtensionResultItem import ExtensionResultItem
from ulauncher.api.shared.action.RenderResultListAction import RenderResultListAction
from ulauncher.api.shared.action.CopyToClipboardAction import CopyToClipboardAction
from sympy import symbols, Eq, solve, sympify, pretty, latex
from sympy.solvers.inequalities import solve_univariate_inequality
import re

x = symbols('x')

class SolveExtension(Extension):
    def __init__(self):
        super().__init__()
        self.subscribe(KeywordQueryEvent, SolveQueryEventListener())

class SolveQueryEventListener(EventListener):
    def on_event(self, event, extension):
        query = event.get_argument()
        if not query:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png',
                    name='Please type an equation or inequality',
                    description='Example: x^2 = 4',
                    on_enter=HideWindowAction())
            ])

        try:
            query = query.replace('^', '**').replace(' ', '')
            match = re.search(r'(<=|>=|=|<|>)', query)
            if not match:
                raise ValueError("No valid operator found.")
            op = match.group(1)
            left, right = query.split(op, 1)
            left_expr = sympify(left)
            right_expr = sympify(right)

            if op == '=':
                res = solve(Eq(left_expr, right_expr), x)
            else:

                inequality = {
                    '<': left_expr < right_expr,
                    '>': left_expr > right_expr,
                    '<=': left_expr <= right_expr,
                    '>=': left_expr >= right_expr
                }[op]
                res = solve_univariate_inequality(inequality, x, relational=False)

            res_pretty = pretty(res, use_unicode=True)
            res_latex = latex(res)

            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png',
                    name=f"Result: {res_pretty}",
                    description="Click to copy unicode result to clipboard",
                    on_enter=CopyToClipboardAction(res_pretty)),
                ExtensionResultItem(
                    icon='images/icon.png',
                    name=f"Result: {res_latex}",
                    description="Click to copy latex result to clipboard",
                    on_enter=CopyToClipboardAction(res_latex))])

        except Exception as e:
            return RenderResultListAction([
                ExtensionResultItem(
                    icon='images/icon.png',
                    name='Error',
                    description=str(e),
                    on_enter=HideWindowAction())
            ])

if __name__ == '__main__':
    SolveExtension().run()
