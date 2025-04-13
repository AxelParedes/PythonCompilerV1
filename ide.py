import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from lexico import test_lexer
from sintactico import test_parser
from semantico import test_semantics
from codigo_intermedio import test_intermediate_code
from tkinter import PhotoImage
from pygments import lex
from pygments.lexers import get_lexer_by_name
from pygments.token import Token
from pygments.style import Style
from pygments.util import ClassNotFound
tk._default_root = None


# Palabras reservadas (deben coincidir con las definidas en lexico.py)
reserved = {
    'if': 'IF', 'else': 'ELSE', 'end': 'END', 'do': 'DO', 'while': 'WHILE', 'switch': 'SWITCH',
    'case': 'CASE', 'int': 'INT', 'float': 'FLOAT', 'main': 'MAIN', 'cin': 'CIN', 'cout': 'COUT'
}

class TextLineNumbers(tk.Canvas):
    def __init__(self, *args, **kwargs):
        tk.Canvas.__init__(self, *args, **kwargs)
        self.textwidget = None

    def attach(self, text_widget):
        self.textwidget = text_widget

    def redraw(self, *args):
        '''Redibuja los números de línea'''
        self.delete("all")
        i = self.textwidget.index("@0,0")
        while True:
            dline = self.textwidget.dlineinfo(i)
            if dline is None:
                break
            y = dline[1]
            linenum = str(i).split(".")[0]
            self.create_text(2, y, anchor="nw", text=linenum, fill="#555")
            i = self.textwidget.index(f"{i}+1line")

class CustomText(tk.Text):
    def __init__(self, *args, **kwargs):
        kwargs["undo"] = True  # Asegurar que undo=True está en los argumentos
        super().__init__(*args, **kwargs)  # Llamar a la clase base correctamente
        tk.Text.__init__(self, *args, **kwargs)
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        self.config(undo=True)
        self.edit_reset()

        # Configurar colores para cada tipo de token
        self.tag_config("NUMBER", foreground="blue")  # Color 1 - Números enteros
        self.tag_config("REAL", foreground="blue")    # Color 1 - Números reales
        self.tag_config("ID", foreground="black")     # Color 2 - Identificadores
        self.tag_config("COMMENT", foreground="green")  # Color 3 - Comentarios
        self.tag_config("RESERVED", foreground="purple")  # Color 4 - Palabras reservadas
        self.tag_config("OPERATOR", foreground="red")   # Color 5 - Operadores aritméticos
        self.tag_config("RELATIONAL", foreground="orange")  # Color 6 - Operadores relacionales
        self.tag_config("LOGICAL", foreground="orange")  # Color 6 - Operadores lógicos
        self.tag_config("SYMBOL", foreground="brown")  # Símbolos
        self.tag_config("ASSIGN", foreground="darkgreen")  # Asignación
        self.tag_config("ERROR", foreground="magenta", underline=True)  # Errores

        # Configurar delay para el resaltado después de escribir
        self.after_id = None
        self.bind("<<Modified>>", self._on_modified)

    def _proxy(self, *args):
        cmd = (self._orig,) + args
        result = self.tk.call(cmd)
        
        if args[0] in ("insert", "replace", "delete"):
            self.after(1, self.highlight_syntax)  
        return result
        
    def _on_modified(self, event=None):
        """Maneja el evento Modified y programa el resaltado con retraso"""
        print("Evento <<Modified>> detectado")  # Depuración
        if self.after_id:
            self.after_cancel(self.after_id)
        
        # Limpiar el indicador de modificación
        self.tk.call(self._orig, "edit", "modified", 0)
        
        # Programar el resaltado con un pequeño retraso para mejorar el rendimiento
        self.after_id = self.after(10, self.highlight_syntax)

    def highlight_syntax(self):
        print("Ejecutando highlight_syntax")  # Depuración

        # Eliminar resaltado previo sin perder colores existentes
        for tag in ["NUMBER", "REAL", "ID", "COMMENT", "RESERVED", "OPERATOR",
                    "RELATIONAL", "LOGICAL", "SYMBOL", "ASSIGN", "ERROR"]:
            self.tag_remove(tag, "1.0", tk.END)

        input_text = self.get("1.0", tk.END).strip()
        if not input_text:
            return  

        try:
            tokens = test_lexer(input_text)
        except Exception as e:
            print(f"Error en test_lexer: {e}")  # Depuración
            return

        for tok in tokens:
            try:
                if not hasattr(tok, 'lineno') or not hasattr(tok, 'lexpos'):
                    continue
                
                line = int(tok.lineno)
                lexpos = int(tok.lexpos)

                # Obtener la línea de texto para calcular posiciones correctamente
                line_start_index = f"{line}.0"
                line_text = self.get(line_start_index, f"{line}.end")

                token_start = line_text.find(str(tok.value))
                if token_start == -1:
                    continue  # No se encontró el token en la línea

                start_pos = f"{line}.{token_start}"
                end_pos = f"{line}.{token_start + len(str(tok.value))}"

                # Aplicar los colores según el tipo de token
                tag_map = {
                    "NUMBER": "NUMBER",
                    "REAL": "REAL",
                    "ID": "ID",
                    "COMMENT": "COMMENT",
                    "ASSIGN": "ASSIGN",
                    "ERROR": "ERROR",
                }
                if tok.type in reserved.values():
                    tag_map[tok.type] = "RESERVED"
                elif tok.type in ("PLUS", "MINUS", "TIMES", "DIVIDE", "MODULO"):
                    tag_map[tok.type] = "OPERATOR"
                elif tok.type in ("LT", "LE", "GT", "GE", "NE", "EQ"):
                    tag_map[tok.type] = "RELATIONAL"
                elif tok.type in ("AND", "OR", "NOT"):
                    tag_map[tok.type] = "LOGICAL"
                elif tok.type in ("LPAREN", "RPAREN", "LBRACE", "RBRACE", "COMMA", "SEMICOLON"):
                    tag_map[tok.type] = "SYMBOL"

                if tok.type in tag_map:
                    self.tag_add(tag_map[tok.type], start_pos, end_pos)
            except Exception as e:
                print(f"Error resaltando token {tok}: {e}")  # Depuración


class IDE:
    def __init__(self, root):
        self.root = root
        self.root.title("IDE para Compilador")
        self.filepath = None  # Variable para almacenar la ruta del archivo
        self.create_menu()
        self.create_toolbar()
        self.create_editor_and_execution()
        self.create_cursor_indicator()
        self.create_error_window()

    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Menú Archivo
        filemenu = tk.Menu(menubar, tearoff=0)
        filemenu.add_command(label="Nuevo Archivo", command=self.new_file)
        filemenu.add_command(label="Abrir", command=self.open_file)
        filemenu.add_command(label="Guardar", command=self.save_file)
        filemenu.add_command(label="Guardar como", command=self.save_file_as)
        filemenu.add_command(label="Cerrar", command=self.close_file)
        filemenu.add_separator()
        filemenu.add_command(label="Salir", command=self.root.quit)
        menubar.add_cascade(label="Archivo", menu=filemenu)

        # Menú Compilar
        compilemenu = tk.Menu(menubar, tearoff=0)
        compilemenu.add_command(label="Compilar Léxico", command=self.compile_lexico)
        compilemenu.add_command(label="Compilar Sintáctico", command=self.compile_sintactico)
        compilemenu.add_command(label="Compilar Semántico", command=self.compile_semantico)
        compilemenu.add_command(label="Generar Intermedio", command=self.compile_intermedio)
        compilemenu.add_command(label="Ejecutar", command=self.compile_ejecucion)
        menubar.add_cascade(label="Compilar", menu=compilemenu)

        self.root.config(menu=menubar)

    def create_toolbar(self):
        toolbar = tk.Frame(self.root, bd=1, relief=tk.RAISED)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        # Íconos para las operaciones del menú
        self.new_icon = PhotoImage(file="icons/new_icon.png").subsample(3,3)
        self.open_icon = PhotoImage(file="icons/open_icon.png").subsample(3,3)
        self.save_icon = PhotoImage(file="icons/save_icon.png").subsample(3,3)
        self.save_as_icon = PhotoImage(file="icons/save_as_icon.png").subsample(3,3)
        self.close_icon = PhotoImage(file="icons/close_icon.png").subsample(3,3)
        self.exit_icon = PhotoImage(file="icons/exit_icon.png").subsample(3,3)
        self.undo_icon = PhotoImage(file="icons/undo_icon.png").subsample(2,2)
        self.redo_icon = PhotoImage(file="icons/redo_icon.png").subsample(2,2)

        btn_new = tk.Button(toolbar, image=self.new_icon, command=self.new_file)
        btn_new.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_new, "Nuevo Archivo")

        btn_open = tk.Button(toolbar, image=self.open_icon, command=self.open_file)
        btn_open.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_open, "Abrir")

        btn_save = tk.Button(toolbar, image=self.save_icon, command=self.save_file)
        btn_save.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_save, "Guardar")

        btn_save_as = tk.Button(toolbar, image=self.save_as_icon, command=self.save_file_as)
        btn_save_as.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_save_as, "Guardar como")

        btn_close = tk.Button(toolbar, image=self.close_icon, command=self.close_file)
        btn_close.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_close, "Cerrar")

        btn_exit = tk.Button(toolbar, image=self.exit_icon, command=self.root.quit)
        btn_exit.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_exit, "Salir")

        # Separador
        separator = ttk.Separator(toolbar, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Botones de Deshacer y Rehacer
        btn_undo = tk.Button(toolbar, image=self.undo_icon, command=self.undo)
        btn_undo.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_undo, "Deshacer")

        btn_redo = tk.Button(toolbar, image=self.redo_icon, command=self.redo)
        btn_redo.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_redo, "Rehacer")

        # Separador
        separator = ttk.Separator(toolbar, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Botones de compilación y ejecución
        btn_lexico = tk.Button(toolbar, text="Compilar Léxico", command=self.compile_lexico)
        btn_lexico.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_lexico, "Compilar Léxico")

        btn_sintactico = tk.Button(toolbar, text="Compilar Sintáctico", command=self.compile_sintactico)
        btn_sintactico.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_sintactico, "Compilar Sintáctico")

        btn_semantico = tk.Button(toolbar, text="Compilar Semántico", command=self.compile_semantico)
        btn_semantico.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_semantico, "Compilar Semántico")

        btn_intermedio = tk.Button(toolbar, text="Generar Intermedio", command=self.compile_intermedio)
        btn_intermedio.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_intermedio, "Generar Código Intermedio")

        btn_ejecucion = tk.Button(toolbar, text="Ejecutar", command=self.compile_ejecucion)
        btn_ejecucion.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_ejecucion, "Ejecutar")

    def add_tooltip(self, widget, text):
        '''Agrega un tooltip (hover) a un widget'''
        def enter(event):
            self.tooltip = tk.Toplevel(widget)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            label = tk.Label(self.tooltip, text=text, background="#ffffe0", relief="solid", borderwidth=1)
            label.pack()

        def leave(event):
            if hasattr(self, 'tooltip'):
                self.tooltip.destroy()

        widget.bind("<Enter>", enter)
        widget.bind("<Leave>", leave)

    def create_editor_and_execution(self):
        # Frame principal para el editor y la ejecución
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Frame para el editor de texto
        self.editor_frame = tk.Frame(self.main_frame)
        self.editor_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Canvas para los números de línea
        self.linenumbers = TextLineNumbers(self.editor_frame, width=40, bg="#f0f0f0")
        self.linenumbers.pack(side=tk.LEFT, fill=tk.Y)

        # Editor de texto
        self.editor = CustomText(self.editor_frame, wrap=tk.NONE, width=80, height=20, bg="white", fg="black", insertbackground="black")
        self.editor.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Barra de desplazamiento vertical
        scrollbar = ttk.Scrollbar(self.editor_frame, orient=tk.VERTICAL, command=self.editor.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.editor.config(yscrollcommand=scrollbar.set)

        # Asociar el editor con los números de línea
        self.linenumbers.attach(self.editor)

        # Configurar eventos para redibujar los números de línea
        self.editor.bind("<<Modified>>", self._on_change)
        self.editor.bind("<Configure>", self._on_change)
        

        # Frame para la ventana de ejecución
        self.execution_frame = tk.Frame(self.main_frame)
        self.execution_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # Pestañas de ejecución
        self.execution_tabs = ttk.Notebook(self.execution_frame)
        self.tab_lexico = ttk.Frame(self.execution_tabs)
        self.tab_sintactico = ttk.Frame(self.execution_tabs)
        self.tab_semantico = ttk.Frame(self.execution_tabs)
        self.tab_intermedio = ttk.Frame(self.execution_tabs)
        self.tab_ejecucion = ttk.Frame(self.execution_tabs)
        self.tab_hash = ttk.Frame(self.execution_tabs)

        self.execution_tabs.add(self.tab_lexico, text="Léxico")
        self.execution_tabs.add(self.tab_sintactico, text="Sintáctico")
        self.execution_tabs.add(self.tab_semantico, text="Semántico")
        self.execution_tabs.add(self.tab_intermedio, text="Intermedio")
        self.execution_tabs.add(self.tab_ejecucion, text="Ejecución")
        self.execution_tabs.add(self.tab_hash, text="Hash")

        self.execution_tabs.pack(fill=tk.BOTH, expand=True)

        # Ventanas de salida para cada pestaña
        self.output_lexico = tk.Text(self.tab_lexico, wrap=tk.WORD, width=80, height=10)
        self.output_lexico.pack(fill=tk.BOTH, expand=True)

        self.output_sintactico = tk.Text(self.tab_sintactico, wrap=tk.WORD, width=80, height=10)
        self.output_sintactico.pack(fill=tk.BOTH, expand=True)

        self.output_semantico = tk.Text(self.tab_semantico, wrap=tk.WORD, width=80, height=10)
        self.output_semantico.pack(fill=tk.BOTH, expand=True)

        self.output_intermedio = tk.Text(self.tab_intermedio, wrap=tk.WORD, width=80, height=10)
        self.output_intermedio.pack(fill=tk.BOTH, expand=True)

        self.output_ejecucion = tk.Text(self.tab_ejecucion, wrap=tk.WORD, width=80, height=10)
        self.output_ejecucion.pack(fill=tk.BOTH, expand=True)
        
        self.output_hash = tk.Text(self.tab_hash, wrap=tk.WORD, width=80, height=10)
        self.output_hash.pack(fill=tk.BOTH, expand=True)

    def _on_change(self, event=None):
        self.linenumbers.redraw()
        
        self.editor.highlight_syntax()
        

    def create_cursor_indicator(self):
        # Frame para el indicador de cursor
        self.cursor_frame = tk.Frame(self.root)
        self.cursor_frame.pack(fill=tk.X)

        # Etiqueta para mostrar la posición del cursor
        self.cursor_label = tk.Label(self.cursor_frame, text="Línea: 1, Columna: 1", anchor="w")
        self.cursor_label.pack(side=tk.LEFT, padx=5, pady=2)

        # Actualizar la posición del cursor cuando se mueve
        self.editor.bind("<KeyRelease>", self.update_cursor_position)
        self.editor.bind("<ButtonRelease>", self.update_cursor_position)

    def update_cursor_position(self, event=None):
        '''Actualiza la etiqueta con la posición actual del cursor'''
        cursor_index = self.editor.index(tk.INSERT)
        line, column = cursor_index.split(".")
        self.cursor_label.config(text=f"Línea: {line}, Columna: {column}")
        

    def create_error_window(self):
        # Frame para la ventana de errores
        self.error_frame = tk.Frame(self.root)
        self.error_frame.pack(fill=tk.BOTH, expand=False)

        # Ventana de errores
        self.output_errores = tk.Text(self.error_frame, wrap=tk.WORD, width=80, height=10)
        self.output_errores.pack(fill=tk.BOTH, expand=True)

    def new_file(self):
        self.editor.delete(1.0, tk.END)
        self.output_errores.delete(1.0, tk.END)
        self.filepath = None  # Al crear un nuevo archivo, no tiene ruta asignada
        self.editor.highlight_syntax()  # Resaltar sintaxis en un nuevo archivo

    def open_file(self):
        filepath = filedialog.askopenfilename(
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if filepath:
            with open(filepath, "r") as file:
                self.editor.delete(1.0, tk.END)
                self.editor.insert(tk.END, file.read())
            
            self.filepath = filepath  
            self.editor.highlight_syntax() 



    def save_file(self):
        if self.filepath:
            # Si ya tiene un nombre, sobreescribe sin preguntar
            with open(self.filepath, "w") as file:
                file.write(self.editor.get(1.0, tk.END))
        else:
            self.save_file_as()  

    def save_file_as(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            initialfile="nuevo_documento.txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if filepath:
            self.filepath = filepath  # Guarda la nueva ruta
            with open(filepath, "w") as file:
                file.write(self.editor.get(1.0, tk.END))

    def close_file(self):
        self.editor.delete(1.0, tk.END)
        self.output_errores.delete(1.0, tk.END)
        self.filepath = None  # Restablecer la ruta al cerrar el archivo

    def undo(self):
        '''Deshacer la última acción en el editor'''
        try:
            self.editor.edit_undo()
        except tk.TclError:
            pass  # No hay más acciones para deshacer

    def redo(self):
        '''Rehacer la última acción en el editor'''
        try:
            self.editor.edit_redo()
        except tk.TclError:
            pass  # No hay más acciones para rehacer

    def compile_lexico(self):
        self.output_lexico.delete(1.0, tk.END)
        self.output_errores.delete(1.0, tk.END)
        input_text = self.editor.get(1.0, tk.END)
        tokens = test_lexer(input_text)
        for tok in tokens:
            self.output_lexico.insert(tk.END, f"Token: {tok}\n")
            if tok.type == 'ERROR':
                self.output_errores.insert(tk.END, f"Error léxico: {tok.value} en línea {tok.lineno}\n")

    def compile_sintactico(self):
        self.output_sintactico.delete(1.0, tk.END)
        self.output_errores.delete(1.0, tk.END)
        input_text = self.editor.get(1.0, tk.END)
        try:
            result = test_parser(input_text)
            self.output_sintactico.insert(tk.END, f"Resultado: {result}\n")
        except Exception as e:
            self.output_errores.insert(tk.END, f"Error sintáctico: {e}\n")

    def compile_semantico(self):
        self.output_semantico.delete(1.0, tk.END)
        self.output_errores.delete(1.0, tk.END)
        input_text = self.editor.get(1.0, tk.END)
        errors = test_semantics(input_text)
        for error in errors:
            self.output_semantico.insert(tk.END, f"{error}\n")
            self.output_errores.insert(tk.END, f"Error semántico: {error}\n")

    def compile_intermedio(self):
        self.output_intermedio.delete(1.0, tk.END)
        input_text = self.editor.get(1.0, tk.END)
        ast = test_intermediate_code(input_text)
        self.output_intermedio.insert(tk.END, f"Código intermedio generado: {ast}\n")
        
    def compile_hash(self):
        self.output_hash.delete(1.0, tk.END)
        input_text = self.editor.get(1.0, tk.END)
        # Aquí iría la lógica para compilar el código a hash
        self.output_hash.insert(tk.END, "Hash generado.\n")

    def compile_ejecucion(self):
        self.output_ejecucion.delete(1.0, tk.END)
        input_text = self.editor.get(1.0, tk.END)
        # Aquí iría la lógica para ejecutar el código
        self.output_ejecucion.insert(tk.END, "Ejecución completada.\n")

if __name__ == "__main__":
    root = tk.Tk()
    ide = IDE(root)
    root.mainloop()