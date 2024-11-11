import tkinter as tk
from tkinter import ttk
from decimal import Decimal, InvalidOperation
import os
import sys

class Calculator:
    """A nice calculator app with basic stuff"""

    def __init__(self):
        # Window
        self.window = tk.Tk()
        self.window.title("Calculator")
        self.window.geometry("320x500")
        self.window.resizable(False, False)

        # app icon
        try:
            if getattr(sys, 'frozen', False):
                application_path = sys._MEIPASS
            else:
                # If running as script
                application_path = os.path.dirname(os.path.abspath(__file__))

            assets_path = os.path.join(application_path, 'assets')

            # icon formats based on platform
            if sys.platform.startswith('win'):
                icon_file = 'calculator.ico'
            else:
                icon_file = 'calculator.png'

            icon_path = os.path.join(assets_path, icon_file)

            if os.path.exists(icon_path):
                if sys.platform.startswith('win'):
                    self.window.iconbitmap(icon_path)
                else:
                    self.window.tk.call('wm', 'iconphoto', self.window._w, tk.PhotoImage(file=icon_path))
            else:
                print(f"Warning: Icon file not found at {icon_path}")
        except Exception as e:
            print(f"Could not load application icon: {e}")

        # Display
        self.default_font_size = 36
        self.min_font_size = 16

        # Calculator state
        self.current = ""
        self.expression = ""
        self.last_operation = None
        self.last_number = None
        self.display_val = tk.StringVar(value="0")
        self.memory_val = tk.StringVar(value="")
        self.just_calculated = False
        self.max_digits = 16

        # Colors
        self.colors = {
            'bg': "#1a1f25",
            'display_bg': "#1a1f25",
            'digit_bg': "#272d36",
            'op_bg': "#272d36",
            'equal_bg': "#3498db",
            'special_bg': "#272d36",
            'text': "#ffffff",
            'hover_digit': "#323842",
            'hover_op': "#323842",
            'hover_equal': "#2980b9",
            'hover_special': "#323842"
        }

        self.window.configure(bg=self.colors['bg'])
        self.window.protocol("WM_DELETE_WINDOW", self._on_closing)
        self._init_calculator()

    def _init_calculator(self):
        self._create_styles()
        self._create_display()
        self._create_buttons()
        self._bind_keys()

    def _create_styles(self):
        style = ttk.Style()
        style.configure("Display.TLabel",
                       background=self.colors['display_bg'],
                       foreground=self.colors['text'],
                       font=('Helvetica', self.default_font_size, 'bold'),
                       anchor="e",
                       padding=10)

        style.configure("Memory.TLabel",
                       background=self.colors['display_bg'],
                       foreground="#8e98a7",
                       font=('Helvetica', 14),
                       anchor="e",
                       padding=5)

    def _create_display(self):
        display_frame = tk.Frame(self.window, bg=self.colors['display_bg'])
        display_frame.pack(fill="x", padx=2, pady=2)

        memory_label = ttk.Label(display_frame,
                               textvariable=self.memory_val,
                               style="Memory.TLabel",
                               wraplength=300)
        memory_label.pack(fill="x")

        display_label = ttk.Label(display_frame,
                                textvariable=self.display_val,
                                style="Display.TLabel",
                                wraplength=300)
        display_label.pack(fill="x")

    def _create_button(self, parent, text, row, col, color_type, colspan=1):
        bg_color = self.colors[f'{color_type}_bg']
        hover_color = self.colors[f'hover_{color_type}']

        btn = tk.Button(parent,
                       text=text,
                       font=('Helvetica', 16, 'bold'),
                       bg=bg_color,
                       fg=self.colors['text'],
                       activebackground=hover_color,
                       activeforeground=self.colors['text'],
                       relief="flat",
                       bd=0)
        btn.grid(row=row, column=col, columnspan=colspan,
                padx=4, pady=4,
                sticky="nsew",
                ipadx=10, ipady=15)
        return btn

    def _create_buttons(self):
        buttons_frame = tk.Frame(self.window, bg=self.colors['bg'])
        buttons_frame.pack(fill="both", expand=True, padx=8, pady=8)

        # Configure grid
        for i in range(5): buttons_frame.grid_rowconfigure(i, weight=1)
        for i in range(4): buttons_frame.grid_columnconfigure(i, weight=1)

        # Button layout
        buttons = [
            ('C', 0, 0, 'special'), ('⌫', 0, 1, 'special'), ('%', 0, 2, 'op'), ('/', 0, 3, 'op'),
            ('7', 1, 0, 'digit'), ('8', 1, 1, 'digit'), ('9', 1, 2, 'digit'), ('*', 1, 3, 'op'),
            ('4', 2, 0, 'digit'), ('5', 2, 1, 'digit'), ('6', 2, 2, 'digit'), ('-', 2, 3, 'op'),
            ('1', 3, 0, 'digit'), ('2', 3, 1, 'digit'), ('3', 3, 2, 'digit'), ('+', 3, 3, 'op'),
            ('0', 4, 0, 'digit', 2), ('.', 4, 2, 'digit'), ('=', 4, 3, 'equal')
        ]

        for btn in buttons:
            colspan = btn[4] if len(btn) > 4 else 1
            button = self._create_button(buttons_frame, btn[0], btn[1], btn[2], btn[3], colspan)
            button.configure(command=lambda x=btn[0]: self._button_click(x))

    def _format_number(self, number):
        """Format number with proper decimal places and comma separators."""
        try:
            num = Decimal(str(number))

            # Handle integer numbers
            if num == num.to_integral():
                return "{:,}".format(int(num))

            decimal_str = "{:.10f}".format(float(num))
            decimal_str = decimal_str.rstrip('0').rstrip('.')
            parts = decimal_str.split('.')
            parts[0] = "{:,}".format(int(parts[0]))
            return '.'.join(parts) if len(parts) > 1 else parts[0]
        except (InvalidOperation, ValueError):
            return number

    def _adjust_font_size(self, text):
        length = len(text)
        if length <= 12:
            font_size = self.default_font_size
        else:
            font_size = max(self.default_font_size - (length - 12) * 1.5, self.min_font_size)

        ttk.Style().configure("Display.TLabel", font=('Helvetica', int(font_size), 'bold'))

    def _update_display(self):
        # Format current number
        display_text = self._format_number(self.current if self.current else "0")
        self._adjust_font_size(display_text)
        self.display_val.set(display_text)

        #  memory display
        if self.last_number is not None and self.last_operation:
            memory_text = f"{self._format_number(self.last_number)} {self.last_operation}"
            if self.current:
                memory_text += f" {self._format_number(self.current)}"
            self.memory_val.set(memory_text)
        else:
            self.memory_val.set("")

    def _button_click(self, value):
        if not self._validate_input(value):
            return

        if value == 'C':
            self._clear_all()
        elif value == '⌫':
            if self.just_calculated:
                self._clear_all()
            self.current = self.current[:-1] or "0"
            self._update_display()
        elif value == '=':
            self._handle_equals()
        elif value in '+-*/%':
            self._handle_operation(value)
        else:
            if self.just_calculated:
                self._clear_all()
            self.current = (self.current if self.current != "0" else "") + value
            self.expression = (self.expression if self.expression != "0" else "") + value
            self._update_display()
            self.just_calculated = False

    def _clear_all(self):
        """Reset calculator"""
        self.current = ""
        self.expression = ""
        self.last_operation = None
        self.last_number = None
        self.display_val.set("0")
        self.memory_val.set("")
        self.just_calculated = False

    def _handle_equals(self):
        """Calculate result with proper error handling."""
        try:
            if not self.expression:
                return

            safe_expr = self.expression.replace('÷', '/').replace('×', '*')

            result = str(eval(safe_expr))

            if "division by zero" in str(result).lower():
                raise ZeroDivisionError

            self.memory_val.set(f"{self._format_number(self.expression)} = ")
            self.current = result
            self.expression = result
            self.last_operation = None
            self.last_number = None
            self._update_display()
            self.just_calculated = True

        except ZeroDivisionError:
            self._show_error("Cannot divide by zero")
        except:
            self._show_error("Invalid expression")

    def _handle_operation(self, value):
        """Handle mathematical operations with proper error checking."""
        if self.just_calculated:
            self.expression = self.current
            self.just_calculated = False

        if value == '%':
            try:
                if not self.current:
                    return

                current_val = Decimal(self.current)

                if self.last_number and self.last_operation:
                    base = Decimal(self.last_number)
                    if self.last_operation in '+-':
                        percentage_value = base * (current_val / Decimal('100'))
                        self.current = str(percentage_value)
                    else:
                        self.current = str(current_val / Decimal('100'))
                else:
                    self.current = str(current_val / Decimal('100'))

                self.expression = self.current
                self._update_display()
                return
            except (InvalidOperation, ValueError):
                self._show_error("Invalid percentage")
                return

        if self.current or self.expression:
            if self.current:
                self.last_number = self.current
                self.expression = self.current
            self.last_operation = value
            self.expression += value
            self.current = ""
            self._update_display()

    def _show_error(self, message):
        """Display error message and reset calculator state."""
        self.display_val.set("Error")
        self.memory_val.set(message)
        self._clear_all()

    def _validate_input(self, value):
        """Validate numeric input to prevent overflow."""
        if len(self.current) >= self.max_digits and value not in ['⌫', 'C', '=']:
            return False
        return True

    def _bind_keys(self):
        self.window.bind('<Key>', self._handle_keypress)

    def _handle_keypress(self, event):
        key = event.char
        if key in '0123456789.+-*/%':
            self._button_click(key)
        elif event.keysym == 'Return':
            self._button_click('=')
        elif event.keysym == 'BackSpace':
            self._button_click('⌫')
        elif event.keysym == 'Escape':
            self._button_click('C')

    def _on_closing(self):
        """Clean up and close the calculator."""
        self.window.quit()

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    calc = Calculator()
    calc.run()
