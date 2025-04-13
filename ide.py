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
        tk.Text.__init__(self, *args, **kwargs)
        self._orig = self._w + "_orig"
        self.tk.call("rename", self._w, self._orig)
        self.tk.createcommand(self._w, self._proxy)
        
        # Configuración del editor
        self.config(
            undo=True,
            wrap=tk.NONE,
            width=80,
            height=20,
            bg="white",
            fg="black",
            insertbackground="black",
            font=("Consolas", 10)
        )
        
        # Configurar colores para cada tipo de token
        self.tag_config("NUMBER", foreground="blue")
        self.tag_config("REAL", foreground="blue") 
        self.tag_config("ID", foreground="black") 
        self.tag_config("COMMENT", foreground="green")
        self.tag_config("RESERVED", foreground="purple")
        self.tag_config("OPERATOR", foreground="red")
        self.tag_config("RELATIONAL", foreground="orange")
        self.tag_config("LOGICAL", foreground="orange")
        self.tag_config("SYMBOL", foreground="brown")
        self.tag_config("ASSIGN", foreground="darkgreen")
        self.tag_config("ERROR", foreground="red", underline=True)

        # Configurar eventos
        self.bind("<<Modified>>", self._on_modified)
        self.after_id = None

    def _proxy(self, *args):
        cmd = (self._orig,) + args
        result = self.tk.call(cmd)
        
        if args[0] in ("insert", "replace", "delete"):
            self.event_generate("<<TextModified>>")
        return result
        
    def _on_modified(self, event=None):
        if self.after_id:
            self.after_cancel(self.after_id)
        self.tk.call(self._orig, "edit", "modified", 0)
        self.after_id = self.after(300, self.highlight_syntax)

    def highlight_syntax(self):
        """Resalta la sintaxis del texto en el editor"""
        # Limpiar todos los tags existentes
        for tag in self.tag_names():
            self.tag_remove(tag, "1.0", tk.END)
        
        # Obtener el texto completo
        text = self.get("1.0", tk.END)
        
        try:
            # Usar un lexer similar a C++ (ajustar según necesidades)
            lexer = get_lexer_by_name("cpp", stripall=True)
            
            # Aplicar el lexer al texto
            for token_type, value in lex(text, lexer):
                # Mapear los tokens de Pygments a nuestros tags
                if token_type in Token.Comment:
                    tag = "COMMENT"
                elif value == 'main':  # <-- CAMBIO ESPECÍFICO PARA 'main'
                    tag = "RESERVED"
                elif token_type in Token.Keyword:
                    tag = "RESERVED"
                elif token_type in Token.Name:
                    tag = "ID"
                elif token_type in Token.Literal.Number.Integer:
                    tag = "NUMBER"
                elif token_type in Token.Literal.Number.Float:
                    tag = "REAL"
                elif token_type in Token.Operator:
                    tag = "OPERATOR"
                elif token_type in Token.Operator.Word:
                    tag = "LOGICAL"
                elif token_type in Token.Punctuation:
                    tag = "SYMBOL"
                else:
                    continue  # Ignorar otros tokens
                
                # Buscar y aplicar tags a todas las ocurrencias
                start = "1.0"
                while True:
                    start = self.search(value, start, stopindex=tk.END)
                    if not start:
                        break
                    end = f"{start}+{len(value)}c"
                    self.tag_add(tag, start, end)
                    start = end
        
        except ClassNotFound:
            pass

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

        # Íconos para las operaciones del menú (usando placeholders si no existen los archivos)
        try:
            self.new_icon = PhotoImage(file="icons/new_icon.png").subsample(3,3)
            self.open_icon = PhotoImage(file="icons/open_icon.png").subsample(3,3)
            self.save_icon = PhotoImage(file="icons/save_icon.png").subsample(3,3)
            self.save_as_icon = PhotoImage(file="icons/save_as_icon.png").subsample(3,3)
            self.close_icon = PhotoImage(file="icons/close_icon.png").subsample(3,3)
            self.exit_icon = PhotoImage(file="icons/exit_icon.png").subsample(3,3)
            self.undo_icon = PhotoImage(file="icons/undo_icon.png").subsample(2,2)
            self.redo_icon = PhotoImage(file="icons/redo_icon.png").subsample(2,2)
        except:
            # Si no hay íconos, usar texto
            self.new_icon = "Nuevo"
            self.open_icon = "Abrir"
            self.save_icon = "Guardar"
            self.save_as_icon = "Guardar como"
            self.close_icon = "Cerrar"
            self.exit_icon = "Salir"
            self.undo_icon = "Deshacer"
            self.redo_icon = "Rehacer"

        btn_new = tk.Button(toolbar, image=self.new_icon if isinstance(self.new_icon, PhotoImage) else None, 
                          text=self.new_icon if not isinstance(self.new_icon, PhotoImage) else None,
                          command=self.new_file)
        btn_new.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_new, "Nuevo Archivo")

        btn_open = tk.Button(toolbar, image=self.open_icon if isinstance(self.open_icon, PhotoImage) else None,
                           text=self.open_icon if not isinstance(self.open_icon, PhotoImage) else None,
                           command=self.open_file)
        btn_open.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_open, "Abrir")

        btn_save = tk.Button(toolbar, image=self.save_icon if isinstance(self.save_icon, PhotoImage) else None,
                           text=self.save_icon if not isinstance(self.save_icon, PhotoImage) else None,
                           command=self.save_file)
        btn_save.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_save, "Guardar")

        btn_save_as = tk.Button(toolbar, image=self.save_as_icon if isinstance(self.save_as_icon, PhotoImage) else None,
                              text=self.save_as_icon if not isinstance(self.save_as_icon, PhotoImage) else None,
                              command=self.save_file_as)
        btn_save_as.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_save_as, "Guardar como")

        btn_close = tk.Button(toolbar, image=self.close_icon if isinstance(self.close_icon, PhotoImage) else None,
                            text=self.close_icon if not isinstance(self.close_icon, PhotoImage) else None,
                            command=self.close_file)
        btn_close.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_close, "Cerrar")

        btn_exit = tk.Button(toolbar, image=self.exit_icon if isinstance(self.exit_icon, PhotoImage) else None,
                           text=self.exit_icon if not isinstance(self.exit_icon, PhotoImage) else None,
                           command=self.root.quit)
        btn_exit.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_exit, "Salir")

        # Separador
        separator = ttk.Separator(toolbar, orient=tk.VERTICAL)
        separator.pack(side=tk.LEFT, padx=5, fill=tk.Y)

        # Botones de Deshacer y Rehacer
        btn_undo = tk.Button(toolbar, image=self.undo_icon if isinstance(self.undo_icon, PhotoImage) else None,
                            text=self.undo_icon if not isinstance(self.undo_icon, PhotoImage) else None,
                            command=self.undo)
        btn_undo.pack(side=tk.LEFT, padx=2, pady=2)
        self.add_tooltip(btn_undo, "Deshacer")

        btn_redo = tk.Button(toolbar, image=self.redo_icon if isinstance(self.redo_icon, PhotoImage) else None,
                            text=self.redo_icon if not isinstance(self.redo_icon, PhotoImage) else None,
                            command=self.redo)
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
        self.editor.bind("<<TextModified>>", self._on_change)
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
        self.error_frame = tk.Frame(self.root, bd=2, relief=tk.GROOVE)
        self.error_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5)
        
        # Etiqueta de título con estilo destacado
        error_label = tk.Label(self.error_frame, text="PANEL DE ERRORES", 
                            bg="#ffebeb", fg="red", 
                            font=('Arial', 10, 'bold'), padx=5, pady=2)
        error_label.pack(fill=tk.X)
        
        # Contenedor principal con borde
        error_container = tk.Frame(self.error_frame, bd=1, relief=tk.SUNKEN)
        error_container.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        # Área de texto para errores
        self.output_errores = tk.Text(error_container, 
                                    wrap=tk.WORD, 
                                    width=80, 
                                    height=8,
                                    bg="white", 
                                    fg="black", 
                                    font=('Consolas', 9),
                                    state=tk.DISABLED,  # Inicialmente en modo solo lectura
                                    padx=5, pady=5)
        
        # Scrollbar vertical
        scrollbar = ttk.Scrollbar(error_container, command=self.output_errores.yview)
        self.output_errores.config(yscrollcommand=scrollbar.set)
        
        # Diseño con grid para mejor ajuste
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.output_errores.pack(fill=tk.BOTH, expand=True)
        
        # Configurar tags para formato de texto
        self.output_errores.tag_config("error_header", foreground="red", font=('Arial', 10, 'bold'))
        self.output_errores.tag_config("error_detail", foreground="black", font=('Consolas', 9))
        self.output_errores.tag_config("no_errors", foreground="green", font=('Arial', 9, 'italic'))
    
    # Bloquear completamente la edición del panel
        def block_event(event):
            return "break"
    
        for event in ["<Key>", "<Button-1>", "<Button-2>", "<Button-3>", "<B1-Motion>"]:
            self.output_errores.bind(event, block_event)
    def new_file(self):
        self.editor.delete(1.0, tk.END)
        self.output_errores.delete(1.0, tk.END)
        self.filepath = None
        self.editor.highlight_syntax()

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
            with open(self.filepath, "w") as file:
                file.write(self.editor.get(1.0, tk.END))
        else:
            self.save_file_as()

    def save_file_as(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")]
        )
        if filepath:
            self.filepath = filepath
            self.save_file()

    def close_file(self):
        self.new_file()

    def undo(self):
        try:
            self.editor.edit_undo()
        except tk.TclError:
            pass

    def redo(self):
        try:
            self.editor.edit_redo()
        except tk.TclError:
            pass

    def compile_lexico(self):
        try:
            print("\n=== INICIANDO COMPILACIÓN LÉXICA ===")  # Depuración
            
            self.output_lexico.delete(1.0, tk.END)
            self.output_errores.config(state=tk.NORMAL)
            self.output_errores.delete(1.0, tk.END)
            
            input_text = self.editor.get(1.0, tk.END)
            print(f"Texto obtenido del editor (primeros 100 chars):\n{input_text[:100]}")  # Depuración
            
            # Dividir el texto en líneas para cálculo de columnas
            lines = input_text.split('\n')
            print(f"Número de líneas: {len(lines)}")  # Depuración
            
            tokens = test_lexer(input_text)
            print(f"Tokens obtenidos ({len(tokens)}):")  # Depuración
            for i, tok in enumerate(tokens[:10]):  # Mostrar solo los primeros 10 para depuración
                print(f"{i}: {tok}")
            
            error_count = 0
            self.output_errores.insert(tk.END, "=== ERRORES LÉXICOS ===\n", "error_header")
            
            for tok in tokens:
                self.output_lexico.insert(tk.END, f"Token: {tok}\n")
                
                if tok.type == 'ERROR':
                    error_count += 1
                    line_num = tok.lineno
                    
                    # Cálculo preciso de la columna
                    if line_num > len(lines):
                        print(f"¡ADVERTENCIA! Número de línea {line_num} excede el total de líneas ({len(lines)})")
                        continue
                    
                    line_text = lines[line_num-1] if (line_num-1) < len(lines) else ""
                    print(f"Procesando error en línea {line_num}: '{line_text}'")  # Depuración
                    
                    # Calcular posición en la línea actual
                    try:
                        prev_lines_length = sum(len(lines[i]) + 1 for i in range(line_num - 1))  # cuenta \n
                        col_num = tok.lexpos - prev_lines_length + 1
                    except:
                        col_num = 1  # fallback en caso de error
                    
                    print(f"Posición calculada: línea {line_num}, col {col_num}")  # Depuración
                    
                    # Mostrar información del error
                    error_msg = (f"Error {error_count}:\n"
                            f"Línea: {line_num}, Columna: {col_num}\n"
                            f"Token inválido: '{tok.value}'\n"
                            f"Contexto: {line_text.strip()}\n"
                            f"{' '*(col_num-1)}^\n\n")
                    
                    print("Mensaje de error a mostrar:\n" + error_msg)  # Depuración
                    
                    self.output_errores.insert(tk.END, error_msg, "error_detail")
                    self.editor.tag_add("ERROR", f"{line_num}.{col_num-1}", f"{line_num}.{col_num}")
            
            if error_count == 0:
                self.output_errores.insert(tk.END, "No se encontraron errores léxicos.\n", "no_errors")
                print("No se encontraron errores léxicos")  # Depuración
            
            self.output_errores.config(state=tk.DISABLED)
            print(f"=== FINALIZADA COMPILACIÓN LÉXICA. Errores encontrados: {error_count} ===")  # Depuración
            
        except Exception as e:
            print(f"EXCEPCIÓN durante compilación léxica: {str(e)}")  # Depuración
            self.output_errores.config(state=tk.NORMAL)
            self.output_errores.insert(tk.END, f"Error durante análisis léxico: {str(e)}\n", "error_detail")
            self.output_errores.config(state=tk.DISABLED)
            raise
    
    
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
        self.output_hash.insert(tk.END, "Hash generado.\n")

    def compile_ejecucion(self):
        self.output_ejecucion.delete(1.0, tk.END)
        input_text = self.editor.get(1.0, tk.END)
        self.output_ejecucion.insert(tk.END, "Ejecución completada.\n")

if __name__ == "__main__":
    root = tk.Tk()
    ide = IDE(root)
    root.mainloop()