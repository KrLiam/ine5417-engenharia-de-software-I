import tkinter as tk
from constants import Constants as c

class PlayerActor:
    window: tk.Tk
    canvas: tk.Canvas
    counter: int
    cell_map: list

    def __init__(self):
        width, height = c.DEFAULT_SIZE

        self.window = tk.Tk()
        self.window.title(c.TITLE)
        self.window.geometry(f"{width}x{height}")
        self.window.resizable(c.RESIZABLE, c.RESIZABLE)
        self.window.configure(bg=c.BACKGROUND_COLOR)

        self.canvas = tk.Canvas(self.window, width=width, height=height, background=c.BACKGROUND_COLOR)
        self.canvas.pack()

        self.counter = 0
        self.cell_map = []

    def loop(self):
        def callback():
            self.update()
            self.window.after(c.DELAY, callback)

        self.window.after(1, callback)
        self.canvas.bind('<Button-1>', self.handle_click)
        self.window.mainloop()


    def rect(x, y, width, height, centered=True):
        if centered:
            x -= width // 2
            y -= height // 2
        return (x, y, x + width, y + height)
    
    def draw_interface(self):
        cell_width = c.BOARD_WIDTH // c.NUM_COLS
        cell_height = c.BOARD_HEIGHT // c.NUM_ROWS

        for row in range(c.NUM_ROWS):
            for col in range(c.NUM_COLS):
                x = col * cell_width + c.BOARD_LEFT
                y = row * cell_height + c.BOARD_TOP
                rect = PlayerActor.rect(x, y, cell_width, cell_height, centered=False)
                self.cell_map.append({'x': x, 'y': y, 'width': cell_width, 'height': cell_height})
                self.canvas.create_rectangle(*rect, outline='black')

    def handle_click(self, event):
        print(f"Posição do clique: {event.x}, {event.y}")
        

    def update(self):
        self.counter += 1

    @property
    def window_size(self) -> tuple[int, int]:
        return (self.window.winfo_width(), self.window.winfo_height())