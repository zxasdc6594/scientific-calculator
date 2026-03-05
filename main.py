#!/usr/bin/env python3
"""
高级科学计算器 - Kivy版
可打包为 Android APK
"""

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.tabbedpanel import TabbedPanel, TabbedPanelItem
from kivy.uix.textinput import TextInput
from kivy.uix.spinner import Spinner
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window
from kivy.graphics import Color, RoundedRectangle
from kivy.properties import StringProperty, NumericProperty
import math


class CalcButton(Button):
    """自定义计算器按钮"""
    
    def __init__(self, text='', bg_color=(0.3, 0.3, 0.3, 1), 
                 text_color=(1, 1, 1, 1), font_size=20, **kwargs):
        super().__init__(**kwargs)
        self.text = text
        self.font_size = font_size
        self.background_normal = ''
        self.background_color = bg_color
        self.color = text_color
        self.bold = True
        self.font_name = 'Roboto'
        
        # 绑定触摸事件改变颜色
        self.original_color = bg_color
        
    def on_press(self):
        # 按下时变亮
        r, g, b, a = self.original_color
        self.background_color = (min(r + 0.2, 1), min(g + 0.2, 1), min(b + 0.2, 1), a)
        
    def on_release(self):
        # 释放时恢复
        self.background_color = self.original_color


class CalculatorDisplay(BoxLayout):
    """显示屏组件"""
    
    expression = StringProperty("")
    result = StringProperty("0")
    mode = StringProperty("DEG")
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.size_hint_y = 0.25
        self.padding = [10, 10, 10, 10]
        
        with self.canvas.before:
            Color(0.1, 0.15, 0.2, 1)
            self.rect = RoundedRectangle(pos=self.pos, size=self.size, radius=[10])
        self.bind(pos=self.update_rect, size=self.update_rect)
        
        # 模式指示
        mode_layout = BoxLayout(size_hint_y=0.2)
        self.mode_label = Label(text=self.mode, color=(0, 1, 0.5, 1), 
                               font_size=14, size_hint_x=0.3, halign='right')
        self.memory_label = Label(text='', color=(1, 0.5, 0, 1),
                                 font_size=14, size_hint_x=0.3, halign='left')
        mode_layout.add_widget(self.memory_label)
        mode_layout.add_widget(Label(size_hint_x=0.4))  # 占位
        mode_layout.add_widget(self.mode_label)
        self.add_widget(mode_layout)
        
        # 表达式显示
        self.expr_label = Label(text='', color=(0.5, 0.7, 0.9, 1),
                               font_size=18, size_hint_y=0.3, halign='right',
                               valign='middle')
        self.expr_label.bind(texture_size=self.expr_label.setter('size'))
        self.add_widget(self.expr_label)
        
        # 结果显示
        self.result_label = Label(text='0', color=(0, 1, 0.8, 1),
                                 font_size=40, size_hint_y=0.5, halign='right',
                                 valign='middle', bold=True)
        self.result_label.bind(texture_size=self.result_label.setter('size'))
        self.add_widget(self.result_label)
        
    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size
        
    def update(self, expression='', result='0', mode='DEG', memory=False):
        self.expr_label.text = expression[-50:] if len(expression) > 50 else expression
        self.result_label.text = result
        self.mode_label.text = mode
        self.memory_label.text = 'M' if memory else ''


class ScientificCalculator(BoxLayout):
    """科学计算器主界面"""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.padding = 5
        self.spacing = 5
        
        # 计算状态
        self.current_input = ""
        self.expression = ""
        self.result = "0"
        self.angle_mode = "DEG"
        self.memory = 0
        self.history = []
        self.waiting_for_operand = False
        
        # 颜色定义
        self.num_color = (0.3, 0.3, 0.3, 1)
        self.op_color = (0.85, 0.45, 0.05, 1)
        self.func_color = (0.2, 0.35, 0.4, 1)
        self.clear_color = (0.65, 0.2, 0.2, 1)
        self.equal_color = (0.15, 0.55, 0.3, 1)
        
        self.setup_ui()
        
    def setup_ui(self):
        # 显示屏
        self.display = CalculatorDisplay()
        self.add_widget(self.display)
        
        # 模式按钮行
        mode_row = BoxLayout(size_hint_y=0.08, spacing=3)
        self.angle_btn = Button(text='DEG', background_color=self.func_color,
                               color=(0, 1, 0.5, 1), font_size=14, bold=True)
        self.angle_btn.bind(on_press=self.toggle_angle_mode)
        mode_row.add_widget(self.angle_btn)
        
        for text, cmd in [('历史', self.show_history), ('方程', self.show_equation),
                         ('矩阵', self.show_matrix), ('换算', self.show_convert)]:
            btn = Button(text=text, background_color=(0.35, 0.35, 0.35, 1),
                        font_size=13)
            btn.bind(on_press=lambda x, c=cmd: c())
            mode_row.add_widget(btn)
        self.add_widget(mode_row)
        
        # 按钮网格
        self.create_buttons()
        
    def create_buttons(self):
        buttons = [
            [('sin', self.func_color), ('cos', self.func_color), ('tan', self.func_color),
             ('ln', self.func_color), ('log', self.func_color)],
            [('asin', self.func_color), ('acos', self.func_color), ('atan', self.func_color),
             ('eˣ', self.func_color), ('10ˣ', self.func_color)],
            [('x²', self.func_color), ('x³', self.func_color), ('√', self.func_color),
             ('∛', self.func_color), ('xʸ', self.func_color)],
            [('n!', self.func_color), ('1/x', self.func_color), ('π', self.func_color),
             ('e', self.func_color), ('%', self.func_color)],
            [('MC', self.clear_color), ('MR', self.clear_color), ('M+', self.clear_color),
             ('M-', self.clear_color), ('±', self.func_color)],
            [('7', self.num_color), ('8', self.num_color), ('9', self.num_color),
             ('DEL', self.clear_color), ('AC', self.clear_color)],
            [('4', self.num_color), ('5', self.num_color), ('6', self.num_color),
             ('×', self.op_color), ('÷', self.op_color)],
            [('1', self.num_color), ('2', self.num_color), ('3', self.num_color),
             ('+', self.op_color), ('-', self.op_color)],
            [('0', self.num_color), ('.', self.num_color), ('(', self.func_color),
             (')', self.func_color), ('=', self.equal_color)],
        ]
        
        for row_data in buttons:
            row = BoxLayout(size_hint_y=0.1, spacing=3)
            for text, color in row_data:
                btn = CalcButton(text=text, bg_color=color)
                btn.bind(on_press=lambda x, t=text: self.on_button_press(t))
                row.add_widget(btn)
            self.add_widget(row)
    
    def on_button_press(self, text):
        commands = {
            '0': lambda: self.input_number('0'),
            '1': lambda: self.input_number('1'),
            '2': lambda: self.input_number('2'),
            '3': lambda: self.input_number('3'),
            '4': lambda: self.input_number('4'),
            '5': lambda: self.input_number('5'),
            '6': lambda: self.input_number('6'),
            '7': lambda: self.input_number('7'),
            '8': lambda: self.input_number('8'),
            '9': lambda: self.input_number('9'),
            '.': lambda: self.input_decimal(),
            '+': lambda: self.input_operator('+'),
            '-': lambda: self.input_operator('-'),
            '×': lambda: self.input_operator('*'),
            '÷': lambda: self.input_operator('/'),
            '=': lambda: self.calculate(),
            'AC': lambda: self.all_clear(),
            'DEL': lambda: self.delete_last(),
            '±': lambda: self.toggle_sign(),
            '%': lambda: self.percentage(),
            'sin': lambda: self.scientific_func('sin'),
            'cos': lambda: self.scientific_func('cos'),
            'tan': lambda: self.scientific_func('tan'),
            'asin': lambda: self.scientific_func('asin'),
            'acos': lambda: self.scientific_func('acos'),
            'atan': lambda: self.scientific_func('atan'),
            'ln': lambda: self.scientific_func('ln'),
            'log': lambda: self.scientific_func('log'),
            'eˣ': lambda: self.scientific_func('exp'),
            '10ˣ': lambda: self.scientific_func('10x'),
            'x²': lambda: self.scientific_func('x2'),
            'x³': lambda: self.scientific_func('x3'),
            '√': lambda: self.scientific_func('sqrt'),
            '∛': lambda: self.scientific_func('cbrt'),
            'xʸ': lambda: self.input_operator('**'),
            'n!': lambda: self.scientific_func('factorial'),
            '1/x': lambda: self.scientific_func('reciprocal'),
            'π': lambda: self.input_constant('pi'),
            'e': lambda: self.input_constant('e'),
            '(': lambda: self.input_parenthesis('('),
            ')': lambda: self.input_parenthesis(')'),
            'MC': lambda: self.memory_clear(),
            'MR': lambda: self.memory_recall(),
            'M+': lambda: self.memory_add(),
            'M-': lambda: self.memory_subtract(),
        }
        
        if text in commands:
            commands[text]()
    
    # ========== 输入处理 ==========
    
    def input_number(self, num):
        if self.waiting_for_operand:
            self.current_input = num
            self.waiting_for_operand = False
        else:
            if self.current_input == "0" and num != "0":
                self.current_input = num
            elif self.current_input != "0":
                self.current_input += num
        self.update_display()
    
    def input_decimal(self):
        if self.waiting_for_operand:
            self.current_input = "0."
            self.waiting_for_operand = False
        elif '.' not in self.current_input:
            self.current_input += '.' if self.current_input else "0."
        self.update_display()
    
    def input_operator(self, op):
        if self.current_input:
            self.expression += self.current_input + ' ' + op + ' '
            self.current_input = ""
        elif self.expression:
            self.expression = self.expression[:-3] + ' ' + op + ' '
        self.waiting_for_operand = False
        self.update_display()
    
    def input_parenthesis(self, p):
        self.current_input += p
        self.update_display()
    
    def input_constant(self, const):
        if const == 'pi':
            value = str(math.pi)
        else:
            value = str(math.e)
        
        if self.waiting_for_operand or not self.current_input:
            self.current_input = value
        else:
            self.current_input += '*' + value
        self.waiting_for_operand = False
        self.update_display()
    
    # ========== 计算功能 ==========
    
    def calculate(self):
        if not self.current_input and not self.expression:
            return
        
        try:
            full_expr = self.expression + self.current_input
            expr = full_expr.replace('×', '*').replace('÷', '/')
            result = eval(expr)
            
            if isinstance(result, float):
                if abs(result) < 1e-10:
                    result = 0
                elif abs(result) >= 1e10 or (abs(result) < 1e-4 and result != 0):
                    result = f"{result:.8e}"
                else:
                    result = round(result, 10)
                    if result == int(result):
                        result = int(result)
            
            self.history.append(f"{full_expr} = {result}")
            if len(self.history) > 50:
                self.history.pop(0)
            
            self.expression = ""
            self.result = str(result)
            self.current_input = str(result)
            self.waiting_for_operand = True
            self.update_display()
            
        except ZeroDivisionError:
            self.result = "错误：除数为零"
            self.update_display()
        except:
            self.result = "错误"
            self.update_display()
    
    def scientific_func(self, func):
        try:
            value = float(self.current_input) if self.current_input else 0
            
            if self.angle_mode == "DEG":
                angle_value = math.radians(value)
            else:
                angle_value = value
            
            if func == 'sin':
                result = math.sin(angle_value)
            elif func == 'cos':
                result = math.cos(angle_value)
            elif func == 'tan':
                result = math.tan(angle_value)
            elif func == 'asin':
                result = math.asin(value)
                if self.angle_mode == "DEG":
                    result = math.degrees(result)
            elif func == 'acos':
                result = math.acos(value)
                if self.angle_mode == "DEG":
                    result = math.degrees(result)
            elif func == 'atan':
                result = math.atan(value)
                if self.angle_mode == "DEG":
                    result = math.degrees(result)
            elif func == 'ln':
                result = math.log(value)
            elif func == 'log':
                result = math.log10(value)
            elif func == 'exp':
                result = math.exp(value)
            elif func == '10x':
                result = 10 ** value
            elif func == 'x2':
                result = value ** 2
            elif func == 'x3':
                result = value ** 3
            elif func == 'sqrt':
                result = math.sqrt(value)
            elif func == 'cbrt':
                result = value ** (1/3)
            elif func == 'factorial':
                if value < 0 or value != int(value):
                    raise ValueError("阶乘需要非负整数")
                result = math.factorial(int(value))
            elif func == 'reciprocal':
                result = 1 / value
            else:
                result = value
            
            if isinstance(result, float):
                result = round(result, 10)
                if result == int(result):
                    result = int(result)
            
            self.current_input = str(result)
            self.waiting_for_operand = True
            self.update_display()
            
        except:
            self.result = "错误"
            self.update_display()
    
    def toggle_sign(self):
        if self.current_input:
            if self.current_input.startswith('-'):
                self.current_input = self.current_input[1:]
            else:
                self.current_input = '-' + self.current_input
            self.update_display()
    
    def percentage(self):
        try:
            value = float(self.current_input) if self.current_input else 0
            self.current_input = str(value / 100)
            self.update_display()
        except:
            pass
    
    # ========== 清除功能 ==========
    
    def all_clear(self):
        self.current_input = ""
        self.expression = ""
        self.result = "0"
        self.waiting_for_operand = False
        self.update_display()
    
    def delete_last(self):
        if self.current_input:
            self.current_input = self.current_input[:-1]
        self.update_display()
    
    # ========== 角度模式 ==========
    
    def toggle_angle_mode(self, instance):
        self.angle_mode = "RAD" if self.angle_mode == "DEG" else "DEG"
        instance.text = self.angle_mode
        self.update_display()
    
    # ========== 内存功能 ==========
    
    def memory_clear(self):
        self.memory = 0
        self.update_display()
    
    def memory_recall(self):
        self.current_input = str(self.memory)
        self.waiting_for_operand = True
        self.update_display()
    
    def memory_add(self):
        try:
            value = float(self.current_input) if self.current_input else 0
            self.memory += value
            self.update_display()
        except:
            pass
    
    def memory_subtract(self):
        try:
            value = float(self.current_input) if self.current_input else 0
            self.memory -= value
            self.update_display()
        except:
            pass
    
    # ========== 显示更新 ==========
    
    def update_display(self):
        display_expr = self.expression + self.current_input
        self.display.update(
            expression=display_expr,
            result=self.result,
            mode=self.angle_mode,
            memory=self.memory != 0
        )
    
    # ========== 高级功能弹窗 ==========
    
    def show_history(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=5)
        
        scroll = ScrollView()
        history_label = Label(text='\n'.join(reversed(self.history)) if self.history else '暂无历史记录',
                             size_hint_y=None, valign='top', halign='left',
                             color=(0, 1, 0.8, 1), font_size=16)
        history_label.bind(texture_size=history_label.setter('size'))
        history_label.text_size = (None, None)
        scroll.add_widget(history_label)
        content.add_widget(scroll)
        
        clear_btn = Button(text='清除历史', size_hint_y=0.15,
                          background_color=self.clear_color)
        def clear_history(instance):
            self.history.clear()
            history_label.text = '暂无历史记录'
        clear_btn.bind(on_press=clear_history)
        content.add_widget(clear_btn)
        
        popup = Popup(title='计算历史', content=content,
                     size_hint=(0.9, 0.8))
        popup.open()
    
    def show_equation(self):
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        # 一元二次方程
        content.add_widget(Label(text='一元二次方程 ax² + bx + c = 0',
                                color=(0, 1, 0.8, 1), font_size=16, size_hint_y=0.15))
        
        input_row1 = BoxLayout(size_hint_y=0.1, spacing=5)
        inputs = {}
        for label in ['a', 'b', 'c']:
            input_row1.add_widget(Label(text=f'{label}=', color=(1,1,1,1), size_hint_x=0.2))
            inputs[label] = TextInput(multiline=False, input_filter='float')
            input_row1.add_widget(inputs[label])
        content.add_widget(input_row1)
        
        result_label = Label(text='', color=(0, 1, 0.5, 1), font_size=18, size_hint_y=0.25)
        
        def solve_quadratic(instance):
            try:
                a, b, c = float(inputs['a'].text), float(inputs['b'].text), float(inputs['c'].text)
                discriminant = b**2 - 4*a*c
                
                if discriminant < 0:
                    real = -b / (2*a)
                    imag = math.sqrt(-discriminant) / (2*a)
                    result_label.text = f'x₁ = {real:.4f} + {imag:.4f}i\nx₂ = {real:.4f} - {imag:.4f}i'
                elif discriminant == 0:
                    result_label.text = f'x = {-b/(2*a):.6f} (重根)'
                else:
                    x1 = (-b + math.sqrt(discriminant)) / (2*a)
                    x2 = (-b - math.sqrt(discriminant)) / (2*a)
                    result_label.text = f'x₁ = {x1:.6f}\nx₂ = {x2:.6f}'
            except:
                result_label.text = '输入错误'
        
        solve_btn = Button(text='求解', size_hint_y=0.12, background_color=self.equal_color)
        solve_btn.bind(on_press=solve_quadratic)
        content.add_widget(solve_btn)
        content.add_widget(result_label)
        
        # 线性方程组
        content.add_widget(Label(text='─' * 30, color=(0.5,0.5,0.5,1), size_hint_y=0.08))
        content.add_widget(Label(text='线性方程组', color=(0, 1, 0.8, 1), font_size=16, size_hint_y=0.1))
        
        linear_inputs = {}
        input_row2 = BoxLayout(size_hint_y=0.1, spacing=3)
        for label in ['a₁', 'b₁', 'c₁', 'a₂', 'b₂', 'c₂']:
            input_row2.add_widget(Label(text=label, color=(1,1,1,1), size_hint_x=0.15, font_size=12))
            linear_inputs[label] = TextInput(multiline=False, input_filter='float', size_hint_x=0.18)
            input_row2.add_widget(linear_inputs[label])
        content.add_widget(input_row2)
        
        linear_result = Label(text='', color=(0, 1, 0.5, 1), font_size=16, size_hint_y=0.15)
        
        def solve_linear(instance):
            try:
                a1 = float(linear_inputs['a₁'].text)
                b1 = float(linear_inputs['b₁'].text)
                c1 = float(linear_inputs['c₁'].text)
                a2 = float(linear_inputs['a₂'].text)
                b2 = float(linear_inputs['b₂'].text)
                c2 = float(linear_inputs['c₂'].text)
                
                det = a1 * b2 - a2 * b1
                if abs(det) < 1e-10:
                    linear_result.text = '无解或无穷多解'
                else:
                    x = (c1 * b2 - c2 * b1) / det
                    y = (a1 * c2 - a2 * c1) / det
                    linear_result.text = f'x = {x:.6f}\ny = {y:.6f}'
            except:
                linear_result.text = '输入错误'
        
        linear_btn = Button(text='求解线性方程组', size_hint_y=0.1, background_color=self.equal_color)
        linear_btn.bind(on_press=solve_linear)
        content.add_widget(linear_btn)
        content.add_widget(linear_result)
        
        popup = Popup(title='方程求解器', content=content, size_hint=(0.95, 0.9))
        popup.open()
    
    def show_matrix(self):
        content = BoxLayout(orientation='vertical', padding=10, spacing=8)
        
        content.add_widget(Label(text='矩阵运算 (2×2)', color=(0, 1, 0.8, 1), font_size=18, size_hint_y=0.1))
        
        # 矩阵输入区域
        matrices_row = BoxLayout(size_hint_y=0.25, spacing=10)
        
        # 矩阵A
        matrix_a_layout = BoxLayout(orientation='vertical')
        matrix_a_layout.add_widget(Label(text='矩阵 A', color=(1,1,1,1), size_hint_y=0.3))
        a_grid = GridLayout(cols=2, spacing=3)
        a_inputs = []
        for _ in range(4):
            inp = TextInput(multiline=False, input_filter='float')
            a_inputs.append(inp)
            a_grid.add_widget(inp)
        matrix_a_layout.add_widget(a_grid)
        matrices_row.add_widget(matrix_a_layout)
        
        # 矩阵B
        matrix_b_layout = BoxLayout(orientation='vertical')
        matrix_b_layout.add_widget(Label(text='矩阵 B', color=(1,1,1,1), size_hint_y=0.3))
        b_grid = GridLayout(cols=2, spacing=3)
        b_inputs = []
        for _ in range(4):
            inp = TextInput(multiline=False, input_filter='float')
            b_inputs.append(inp)
            b_grid.add_widget(inp)
        matrix_b_layout.add_widget(b_grid)
        matrices_row.add_widget(matrix_b_layout)
        
        content.add_widget(matrices_row)
        
        # 操作按钮
        ops_row = BoxLayout(size_hint_y=0.12, spacing=3)
        result_label = Label(text='', color=(0, 1, 0.5, 1), font_size=16, size_hint_y=0.3)
        
        def get_matrix(inputs):
            return [[float(inputs[0].text or 0), float(inputs[1].text or 0)],
                    [float(inputs[2].text or 0), float(inputs[3].text or 0)]]
        
        def matrix_add(instance):
            A, B = get_matrix(a_inputs), get_matrix(b_inputs)
            result_label.text = f"A + B =\n[{A[0][0]+B[0][0]:.2f}  {A[0][1]+B[0][1]:.2f}]\n[{A[1][0]+B[1][0]:.2f}  {A[1][1]+B[1][1]:.2f}]"
        
        def matrix_sub(instance):
            A, B = get_matrix(a_inputs), get_matrix(b_inputs)
            result_label.text = f"A - B =\n[{A[0][0]-B[0][0]:.2f}  {A[0][1]-B[0][1]:.2f}]\n[{A[1][0]-B[1][0]:.2f}  {A[1][1]-B[1][1]:.2f}]"
        
        def matrix_mul(instance):
            A, B = get_matrix(a_inputs), get_matrix(b_inputs)
            result = [[sum(A[i][k]*B[k][j] for k in range(2)) for j in range(2)] for i in range(2)]
            result_label.text = f"A × B =\n[{result[0][0]:.2f}  {result[0][1]:.2f}]\n[{result[1][0]:.2f}  {result[1][1]:.2f}]"
        
        def matrix_det(instance):
            A = get_matrix(a_inputs)
            det = A[0][0]*A[1][1] - A[0][1]*A[1][0]
            result_label.text = f'|A| = {det:.4f}'
        
        def matrix_trans(instance):
            A = get_matrix(a_inputs)
            result_label.text = f"Aᵀ =\n[{A[0][0]:.2f}  {A[1][0]:.2f}]\n[{A[0][1]:.2f}  {A[1][1]:.2f}]"
        
        for text, cmd in [('A+B', matrix_add), ('A-B', matrix_sub), ('A×B', matrix_mul),
                         ('det(A)', matrix_det), ('Aᵀ', matrix_trans)]:
            btn = Button(text=text, font_size=12, background_color=self.func_color)
            btn.bind(on_press=cmd)
            ops_row.add_widget(btn)
        
        content.add_widget(ops_row)
        content.add_widget(result_label)
        
        popup = Popup(title='矩阵运算', content=content, size_hint=(0.95, 0.75))
        popup.open()
    
    def show_convert(self):
        content = BoxLayout(orientation='vertical', padding=15, spacing=10)
        
        content.add_widget(Label(text='单位换算器', color=(0, 1, 0.8, 1), font_size=18, size_hint_y=0.1))
        
        # 类型选择
        type_row = BoxLayout(size_hint_y=0.1)
        type_row.add_widget(Label(text='类型:', color=(1,1,1,1), size_hint_x=0.3))
        type_spinner = Spinner(text='长度', values=['长度', '重量', '温度', '面积', '体积'],
                              size_hint_x=0.7)
        type_row.add_widget(type_spinner)
        content.add_widget(type_row)
        
        # 数值输入
        value_row = BoxLayout(size_hint_y=0.1)
        value_row.add_widget(Label(text='数值:', color=(1,1,1,1), size_hint_x=0.3))
        value_input = TextInput(multiline=False, input_filter='float')
        value_row.add_widget(value_input)
        content.add_widget(value_row)
        
        # 单位数据
        units_data = {
            '长度': ['米', '千米', '厘米', '毫米', '英寸', '英尺', '英里'],
            '重量': ['克', '千克', '毫克', '吨', '盎司', '磅'],
            '温度': ['摄氏度', '华氏度', '开尔文'],
            '面积': ['平方米', '平方千米', '公顷', '亩', '平方英尺'],
            '体积': ['升', '毫升', '立方米', '加仑', '品脱']
        }
        
        convert_factors = {
            '长度': {'米': 1, '千米': 1000, '厘米': 0.01, '毫米': 0.001, '英寸': 0.0254, '英尺': 0.3048, '英里': 1609.344},
            '重量': {'克': 1, '千克': 1000, '毫克': 0.001, '吨': 1000000, '盎司': 28.3495, '磅': 453.592},
            '面积': {'平方米': 1, '平方千米': 1000000, '公顷': 10000, '亩': 666.667, '平方英尺': 0.092903},
            '体积': {'升': 1, '毫升': 0.001, '立方米': 1000, '加仑': 3.78541, '品脱': 0.473176}
        }
        
        # 从/到 单位选择
        from_row = BoxLayout(size_hint_y=0.1)
        from_row.add_widget(Label(text='从:', color=(1,1,1,1), size_hint_x=0.3))
        from_spinner = Spinner(text='米', values=units_data['长度'], size_hint_x=0.7)
        from_row.add_widget(from_spinner)
        content.add_widget(from_row)
        
        to_row = BoxLayout(size_hint_y=0.1)
        to_row.add_widget(Label(text='到:', color=(1,1,1,1), size_hint_x=0.3))
        to_spinner = Spinner(text='千米', values=units_data['长度'], size_hint_x=0.7)
        to_row.add_widget(to_spinner)
        content.add_widget(to_row)
        
        def update_units(spinner, text):
            units = units_data[text]
            from_spinner.values = units
            to_spinner.values = units
            from_spinner.text = units[0]
            to_spinner.text = units[1] if len(units) > 1 else units[0]
        
        type_spinner.bind(text=update_units)
        
        result_label = Label(text='', color=(0, 1, 0.5, 1), font_size=20, size_hint_y=0.2)
        
        def do_convert(instance):
            try:
                value = float(value_input.text)
                unit_type = type_spinner.text
                from_unit = from_spinner.text
                to_unit = to_spinner.text
                
                if unit_type == '温度':
                    # 温度特殊处理
                    if from_unit == '摄氏度':
                        celsius = value
                    elif from_unit == '华氏度':
                        celsius = (value - 32) * 5/9
                    else:
                        celsius = value - 273.15
                    
                    if to_unit == '摄氏度':
                        result = celsius
                    elif to_unit == '华氏度':
                        result = celsius * 9/5 + 32
                    else:
                        result = celsius + 273.15
                else:
                    factors = convert_factors[unit_type]
                    base = value * factors[from_unit]
                    result = base / factors[to_unit]
                
                result_label.text = f'{value} {from_unit} = {result:.6g} {to_unit}'
            except:
                result_label.text = '输入错误'
        
        convert_btn = Button(text='换算', size_hint_y=0.12, background_color=self.equal_color)
        convert_btn.bind(on_press=do_convert)
        content.add_widget(convert_btn)
        content.add_widget(result_label)
        
        popup = Popup(title='单位换算', content=content, size_hint=(0.95, 0.85))
        popup.open()


class CalculatorApp(App):
    def build(self):
        Window.clearcolor = (0.15, 0.15, 0.15, 1)
        return ScientificCalculator()
    
    def get_application_config(self):
        return super().get_application_config('~/.calculator.ini')


if __name__ == '__main__':
    CalculatorApp().run()
