import tkinter as tk

class Constantes:
    TITLE = "Conjunto"
    DEFAULT_SIZE = (1500, 900)
    RESIZABLE = True
    DELAY = 15

class PlayerActor:
    window: tk.Tk
    canvas: tk.Canvas
    counter: int

    def __init__(self):
        width, height = Constantes.DEFAULT_SIZE

        self.window = tk.Tk()
        self.window.title(Constantes.TITLE)
        self.window.geometry(f"{width}x{height}")
        self.window.resizable(Constantes.RESIZABLE, Constantes.RESIZABLE)

        self.canvas = tk.Canvas(self.window, width=width, height=height)
        self.canvas.pack()

        self.counter = 0
    
    def loop(self):
        def callback():
            self.update()
            self.window.after(Constantes.DELAY, callback)

        self.window.after(1, callback)
        self.window.mainloop()
    
    @property
    def window_size(self) -> tuple[int, int]:
        return (self.window.winfo_width(), self.window.winfo_height())
    
    def update(self):
        print(f"updated {self.counter} {self.window_size}")
        self.counter += 1
