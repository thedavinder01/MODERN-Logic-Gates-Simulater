import tkinter as tk
from tkinter import messagebox
from functools import partial

# --- Logic functions ---
def AND(a, b): return a & b
def OR(a, b): return a | b
def NOT(a, _=0): return 0 if a else 1
def NAND(a, b): return 0 if (a & b) else 1
def NOR(a, b): return 0 if (a | b) else 1
def XOR(a, b): return a ^ b
def XNOR(a, b): return 0 if (a ^ b) else 1

GATES = [
    ("AND", AND),
    ("OR", OR),
    ("NOT", NOT),
    ("NAND", NAND),
    ("NOR", NOR),
    ("XOR", XOR),
    ("XNOR", XNOR),
]

# --- Colors ---
BG = "#D6F0FA"         # Light cyan background
CARD = "#87CEEB"       # Sky blue for input area
TEXT = "#0B3D91"       # Dark blue text
INPUT_COLOR = "#87CEEB" # Sky blue input buttons
OUTPUT_ON = "#00FF44"   # Green for output ON
OUTPUT_OFF = "#FF4444"  # Red for output OFF
HIGHLIGHT = "#1E90FF"   # Dodger blue highlight for truth table

# --- GateRow class ---
class GateRow(tk.Frame):
    def __init__(self, master, name, func, *args, **kwargs):
        super().__init__(master, bg=CARD, *args, **kwargs)
        self.name, self.func = name, func
        self.a, self.b = 0, 0
        self._blink, self._blink_job = False, None

        # Left: inputs + truth table
        left = tk.Frame(self, bg=CARD)
        left.pack(side="left", padx=10, pady=5)

        tk.Label(left, text=f"{name} Gate", fg=TEXT, bg=CARD,
                 font=("Consolas", 12, "bold")).pack(anchor="w", padx=5, pady=3)

        self.truth_labels = []
        rows = [(0,0),(0,1),(1,0),(1,1)]
        for a,b in rows:
            if name=="NOT" and b==1: continue
            y = func(a,b) if name!="NOT" else func(a)
            lbl = tk.Label(left, text=f"{a}   {b if name!='NOT' else '-'}   {y}",
                           bg=CARD, fg=TEXT, font=("Consolas",10))
            lbl.pack(anchor="w", padx=5, pady=1)
            lbl.bind("<Button-1>", partial(self._truth_click,a,b))
            self.truth_labels.append(lbl)

        # Input Buttons
        self.btn_a = tk.Button(left, text="A: 0", width=6, bg=INPUT_COLOR, fg=TEXT, command=self.toggle_a)
        self.btn_a.pack(padx=5, pady=3)
        if name!="NOT":
            self.btn_b = tk.Button(left, text="B: 0", width=6, bg=INPUT_COLOR, fg=TEXT, command=self.toggle_b)
            self.btn_b.pack(padx=5, pady=3)

        # Right: gate + output
        right = tk.Frame(self, bg=BG)
        right.pack(side="left", padx=10, pady=5)
        self.canvas = tk.Canvas(right, width=180, height=80, bg=BG, highlightthickness=0)
        self.canvas.pack()
        self._draw_gate()

        self.out_label = tk.Label(right, text="Output: 0", fg=TEXT, bg=BG,
                                  font=("Consolas",10,"bold"))
        self.out_label.pack(pady=3)

        self.bulb_canvas = tk.Canvas(right, width=40, height=40, bg=BG, highlightthickness=0)
        self.bulb_canvas.pack()
        self.bulb = self.bulb_canvas.create_oval(5,5,35,35, fill=OUTPUT_OFF, outline=TEXT, width=2)

        self.update_output()

    def _draw_gate(self):
        c = self.canvas
        c.delete("all")
        c.create_rectangle(10,10,170,70,outline=TEXT,width=2)
        c.create_text(90,40,text=self.name,fill=TEXT,font=("Consolas",16,"bold"))
        c.create_line(0,25,10,25,fill=TEXT,width=2)
        c.create_line(0,55,10,55,fill=TEXT,width=2)
        c.create_line(170,40,180,40,fill=TEXT,width=2)

    def _truth_click(self, a, b, event=None):
        self.a = a
        if hasattr(self,"btn_b"): self.b = b
        self._update_buttons()
        self.update_output()

    def toggle_a(self):
        self.a = 1 - self.a
        self._update_buttons()
        self.update_output()

    def toggle_b(self):
        self.b = 1 - self.b
        self._update_buttons()
        self.update_output()

    def _update_buttons(self):
        self.btn_a.configure(text=f"A:{self.a}")
        if hasattr(self,"btn_b"):
            self.btn_b.configure(text=f"B:{self.b}")

    def update_output(self):
        y = self.func(self.a, self.b) if self.name!="NOT" else self.func(self.a)
        self.out_label.configure(text=f"Output: {y}")
        self.bulb_canvas.itemconfig(self.bulb, fill=OUTPUT_ON if y else OUTPUT_OFF)

        # Highlight truth row
        for lbl in self.truth_labels: lbl.configure(bg=CARD)
        match = f"{self.a}   {self.b if self.name!='NOT' else '-'}   {y}"
        for lbl in self.truth_labels:
            if lbl.cget("text") == match:
                lbl.configure(bg=HIGHLIGHT)

    def reset(self):
        self.a = 0
        self.b = 0
        self._update_buttons()
        self.update_output()

    def export_truth_text(self):
        s = f"{self.name} Gate\nA B Y\n"
        rows = [(0,0),(0,1),(1,0),(1,1)]
        for a,b in rows:
            if self.name=="NOT" and b==1: continue
            y = self.func(a,b) if self.name!="NOT" else self.func(a)
            s += f"{a} {b if self.name!='NOT' else '-'} {y}\n"
        s += "\n"
        return s

# --- Main App ---
class LogicSimulatorApp:
    def __init__(self, root):
        self.root = root
        root.title("Modern Logic G@tes  Simul@tor")
        root.configure(bg=BG)
        root.geometry("1000x800")

        # Header
        header = tk.Frame(root, bg=BG)
        header.pack(fill="x", pady=5)
        tk.Label(header, text="⚡ Modern Logic G@tes  Simul@tor", bg=BG, fg=TEXT,
                 font=("Consolas", 18, "bold")).pack(pady=5)
        button_frame = tk.Frame(header, bg=BG)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Reset All", command=self.reset_all,
                  bg=INPUT_COLOR, fg=TEXT).pack(side="left", padx=5)
        tk.Button(button_frame, text="Export TruthTables", command=self.export_truth_tables,
                  bg=INPUT_COLOR, fg=TEXT).pack(side="left", padx=5)

        # Scrollable area
        body = tk.Frame(root, bg=BG)
        body.pack(fill="both", expand=True, padx=5, pady=5)
        canvas = tk.Canvas(body, bg=BG, highlightthickness=0)
        scrollbar = tk.Scrollbar(body, orient="vertical", command=canvas.yview)
        self.scrollable_area = tk.Frame(canvas, bg=BG)
        self.scrollable_area.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0,0), window=self.scrollable_area, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # 3x2 grid of gates
        self.gate_rows = []
        for r in range(3):
            frame_row = tk.Frame(self.scrollable_area, bg=BG)
            frame_row.pack(fill="x", pady=10)
            frame_row.grid_columnconfigure(0, weight=1)
            frame_row.grid_columnconfigure(1, weight=1)
            for c in range(2):
                idx = r*2 + c
                if idx >= len(GATES): break
                name, func = GATES[idx]
                gate = GateRow(frame_row, name, func)
                gate.grid(row=0, column=c, padx=50, sticky="nsew")
                self.gate_rows.append(gate)

    def reset_all(self):
        for row in self.gate_rows: row.reset()

    def export_truth_tables(self):
        content = ""
        for row in self.gate_rows:
            content += row.export_truth_text()
        try:
            with open("truth_tables.txt","w") as f: f.write(content)
            messagebox.showinfo("Export Complete","Truth tables saved as truth_tables.txt")
        except Exception as e:
            messagebox.showerror("Error", str(e))

# --- Run App ---
if __name__ == "__main__":
    root = tk.Tk()
    app = LogicSimulatorApp(root)
    root.mainloop()
