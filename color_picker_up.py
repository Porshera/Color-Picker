"""
color_picker.py — Экранная пипетка с палитрой и смыслами цветов
Работает на Windows 10 и 11 без сторонних библиотек.
Зависимости: только tkinter (встроен в Python)
"""

import ctypes
import ctypes.wintypes
import colorsys
import tkinter as tk
from tkinter import ttk

try:
    ctypes.windll.shcore.SetProcessDpiAwareness(2)
except Exception:
    try:
        ctypes.windll.user32.SetProcessDPIAware()
    except Exception:
        pass


def get_pixel_color(x: int, y: int) -> tuple[int, int, int]:
    hdc = ctypes.windll.user32.GetDC(0)
    color = ctypes.windll.gdi32.GetPixel(hdc, x, y)
    ctypes.windll.user32.ReleaseDC(0, hdc)
    if color == -1:
        return (0, 0, 0)
    r = color & 0xFF
    g = (color >> 8) & 0xFF
    b = (color >> 16) & 0xFF
    return (r, g, b)


def get_cursor_pos() -> tuple[int, int]:
    pt = ctypes.wintypes.POINT()
    ctypes.windll.user32.GetCursorPos(ctypes.byref(pt))
    return (pt.x, pt.y)


def color_meaning(r: int, g: int, b: int) -> tuple[str, str]:
    """Возвращает (название, символическое значение) для цвета."""
    h, s, v = colorsys.rgb_to_hsv(r/255, g/255, b/255)
    hue = h * 360

    # Ахроматические
    if s < 0.10:
        if v < 0.15:
            return "Чёрный", "Тайна, элегантность, власть, сила воли"
        if v < 0.35:
            return "Тёмно-серый", "Сдержанность, нейтральность, строгость"
        if v < 0.65:
            return "Серый", "Равновесие, нейтралитет, практичность"
        if v < 0.85:
            return "Светло-серый", "Мягкость, спокойствие, минимализм"
        return "Белый", "Чистота, свет, начало, невинность"

    # Цветные
    if hue < 15 or hue >= 345:
        if v < 0.4:
            return "Тёмно-красный", "Страсть, опасность, сила, решимость"
        if s > 0.7:
            return "Красный", "Энергия, любовь, страсть, смелость, огонь"
        return "Розово-красный", "Романтика, нежность, привязанность"
    if hue < 30:
        if s > 0.7 and v > 0.7:
            return "Оранжевый", "Энтузиазм, творчество, радость, общение"
        return "Тёмно-оранжевый", "Уверенность, тепло, дружелюбие"
    if hue < 50:
        if v > 0.75 and s > 0.6:
            return "Золотой", "Богатство, удача, успех, благородство"
        if v < 0.5:
            return "Коричневый", "Надёжность, земля, уют, стабильность"
        return "Жёлто-оранжевый", "Оптимизм, тепло, бодрость"
    if hue < 70:
        if v > 0.85 and s > 0.5:
            return "Жёлтый", "Радость, интеллект, солнце, вдохновение"
        return "Тёмно-жёлтый", "Мудрость, осторожность, внимание"
    if hue < 150:
        if hue < 100:
            return "Жёлто-зелёный", "Рост, свежесть, молодость, весна"
        if v > 0.6:
            return "Зелёный", "Природа, гармония, здоровье, процветание"
        return "Тёмно-зелёный", "Надежда, стабильность, мудрость леса"
    if hue < 175:
        return "Изумрудный", "Роскошь, равновесие, исцеление, изобилие"
    if hue < 200:
        return "Бирюзовый", "Спокойствие, ясность, коммуникация, море"
    if hue < 240:
        if v < 0.4:
            return "Тёмно-синий", "Глубина, доверие, профессионализм"
        return "Синий", "Доверие, мудрость, спокойствие, небо и море"
    if hue < 260:
        return "Сине-фиолетовый", "Интуиция, тайна, вдохновение"
    if hue < 290:
        if v > 0.6:
            return "Фиолетовый", "Творчество, духовность, роскошь, магия"
        return "Тёмно-фиолетовый", "Мистика, власть, трансформация"
    if hue < 320:
        return "Пурпурный", "Достоинство, страсть, амбиции, сила духа"
    if hue < 345:
        if s > 0.5 and v > 0.7:
            return "Розовый", "Нежность, романтика, забота, добро"
        return "Малиновый", "Яркость, смелость, страсть, жизнелюбие"
    return "Красный", "Энергия, любовь, страсть, смелость"


BG      = "#0f0f17"
SURFACE = "#1a1a2a"
BORDER  = "#2e2e46"
ACCENT  = "#7c6af7"
TEXT    = "#e8e8f0"
MUTED   = "#6c6c8a"
SUCCESS = "#56cfb2"

PALETTE_SIZE = 16   # ячеек в палитре


class ColorPickerApp:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.picking = False
        self._poll_id = None
        self._palette: list[str] = []      # список hex-цветов
        self._current_rgb = (255, 255, 255)
        self._build_window()
        self._build_ui()

    def _build_window(self) -> None:
        self.root.title("Пипетка — Color Picker")
        self.root.resizable(False, False)
        self.root.attributes("-topmost", True)
        self.root.configure(bg=BG)
        w, h = 340, 620
        sw = self.root.winfo_screenwidth()
        sh = self.root.winfo_screenheight()
        self.root.geometry(f"{w}x{h}+{(sw-w)//2}+{(sh-h)//2}")

    def _build_ui(self) -> None:
        tk.Frame(self.root, bg=ACCENT, height=4).pack(fill="x")

        tk.Label(self.root, text="🎨  Пипетка", bg=BG, fg=TEXT,
                 font=("Segoe UI", 14, "bold"), pady=10).pack()

        self.hint_var = tk.StringVar(
            value="Нажмите «Выбрать цвет», наведите\nмышку на нужное место и нажмите Пробел")
        tk.Label(self.root, textvariable=self.hint_var,
                 bg=BG, fg=MUTED, font=("Segoe UI", 9),
                 justify="center").pack(pady=(0, 8))

        # ── Превью ──────────────────────────────
        self.canvas = tk.Canvas(self.root, width=120, height=72,
                                bg="#ffffff", highlightthickness=2,
                                highlightbackground=BORDER)
        self.canvas.pack()

        self.pos_var = tk.StringVar(value="x: —   y: —")
        tk.Label(self.root, textvariable=self.pos_var,
                 bg=BG, fg=MUTED, font=("Consolas", 8)).pack(pady=(4, 0))

        # ── HEX / RGB ────────────────────────────
        tk.Label(self.root, text="HEX", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8)).pack(pady=(8, 2))
        self.hex_var = tk.StringVar(value="#FFFFFF")
        tk.Label(self.root, textvariable=self.hex_var,
                 bg=SURFACE, fg=ACCENT,
                 font=("Consolas", 20, "bold"),
                 padx=20, pady=6).pack()

        tk.Label(self.root, text="RGB", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8)).pack(pady=(6, 2))
        self.rgb_var = tk.StringVar(value="255, 255, 255")
        tk.Label(self.root, textvariable=self.rgb_var,
                 bg=BG, fg=TEXT, font=("Consolas", 11)).pack()

        # ── Смысл цвета ──────────────────────────
        meaning_frame = tk.Frame(self.root, bg=SURFACE,
                                 highlightthickness=1,
                                 highlightbackground=BORDER)
        meaning_frame.pack(fill="x", padx=20, pady=(10, 4))

        self.color_name_var = tk.StringVar(value="Белый")
        tk.Label(meaning_frame, textvariable=self.color_name_var,
                 bg=SURFACE, fg=SUCCESS,
                 font=("Segoe UI", 10, "bold"), pady=4).pack()

        self.meaning_var = tk.StringVar(value="Чистота, свет, начало, невинность")
        tk.Label(meaning_frame, textvariable=self.meaning_var,
                 bg=SURFACE, fg=MUTED,
                 font=("Segoe UI", 8),
                 wraplength=280, justify="center", pady=4).pack()

        # ── Кнопки ───────────────────────────────
        btn_frame = tk.Frame(self.root, bg=BG)
        btn_frame.pack(fill="x", padx=20, pady=8)

        self.btn = tk.Button(
            btn_frame, text="Выбрать цвет",
            command=self._toggle_picking,
            bg=ACCENT, fg="#ffffff",
            font=("Segoe UI", 11, "bold"),
            relief="flat", bd=0, cursor="hand2",
            padx=12, pady=9,
            activebackground="#6a58e0", activeforeground="#ffffff",
        )
        self.btn.pack(side="left", expand=True, fill="x", padx=(0, 6))

        self.add_btn = tk.Button(
            btn_frame, text="＋ В палитру",
            command=self._add_to_palette,
            bg=SURFACE, fg=SUCCESS,
            font=("Segoe UI", 10),
            relief="flat", bd=0, cursor="hand2",
            padx=10, pady=9,
            highlightthickness=1, highlightbackground=BORDER,
            activebackground=BORDER, activeforeground=SUCCESS,
        )
        self.add_btn.pack(side="left")

        self.copy_var = tk.StringVar(value="")
        tk.Label(self.root, textvariable=self.copy_var,
                 bg=BG, fg=MUTED, font=("Segoe UI", 8)).pack()

        # ── Палитра ──────────────────────────────
        tk.Label(self.root, text="ПАЛИТРА", bg=BG, fg=MUTED,
                 font=("Segoe UI", 8)).pack(pady=(10, 4))

        palette_outer = tk.Frame(self.root, bg=BG)
        palette_outer.pack(padx=20, fill="x")

        self.palette_frame = tk.Frame(palette_outer, bg=BG)
        self.palette_frame.pack(fill="x")

        self.palette_hint = tk.Label(self.root,
                                     text="Здесь появятся сохранённые цвета",
                                     bg=BG, fg=MUTED, font=("Segoe UI", 8))
        self.palette_hint.pack(pady=2)

        # Кнопка очистки палитры
        self.clear_btn = tk.Button(
            self.root, text="Очистить палитру",
            command=self._clear_palette,
            bg=BG, fg=MUTED,
            font=("Segoe UI", 8),
            relief="flat", bd=0, cursor="hand2",
            activebackground=BG, activeforeground=TEXT,
        )
        # покажем позже, когда будут цвета

        self.root.bind("<space>",  lambda e: self._capture())
        self.root.bind("<Return>", lambda e: self._capture())
        self.root.bind("<Escape>", lambda e: self._stop_picking())

    # ── Логика пикера ────────────────────────────────────────────────────────

    def _toggle_picking(self) -> None:
        if self.picking:
            self._stop_picking()
        else:
            self._start_picking()

    def _start_picking(self) -> None:
        self.picking = True
        self.btn.config(text="Отмена  (Esc)", bg="#c0392b",
                        activebackground="#a93226")
        self.hint_var.set("Наведите мышку на нужный пиксель\nи нажмите  Пробел  или  Enter")
        self.copy_var.set("")
        self._poll()

    def _stop_picking(self) -> None:
        self.picking = False
        if self._poll_id:
            self.root.after_cancel(self._poll_id)
            self._poll_id = None
        self.btn.config(text="Выбрать цвет", bg=ACCENT,
                        activebackground="#6a58e0")
        self.hint_var.set("Нажмите «Выбрать цвет», наведите\nмышку на нужное место и нажмите Пробел")

    def _poll(self) -> None:
        if not self.picking:
            return
        try:
            x, y = get_cursor_pos()
            r, g, b = get_pixel_color(x, y)
            self._update_display(r, g, b)
            self.pos_var.set(f"x: {x}   y: {y}")
        except Exception:
            pass
        self._poll_id = self.root.after(50, self._poll)

    def _update_display(self, r: int, g: int, b: int) -> None:
        self._current_rgb = (r, g, b)
        hex_color = f"#{r:02X}{g:02X}{b:02X}"
        self.canvas.configure(bg=hex_color)
        self.hex_var.set(hex_color)
        self.rgb_var.set(f"{r}, {g}, {b}")
        name, meaning = color_meaning(r, g, b)
        self.color_name_var.set(name)
        self.meaning_var.set(meaning)

    def _capture(self) -> None:
        if not self.picking:
            return
        hex_color = self.hex_var.get()
        self._stop_picking()
        self._copy_to_clipboard(hex_color)

    def _copy_to_clipboard(self, hex_color: str) -> None:
        self.root.clipboard_clear()
        self.root.clipboard_append(hex_color)
        self.root.update()
        self.copy_var.set(f"✓  {hex_color} скопирован в буфер обмена")
        self.btn.config(bg="#27ae60", activebackground="#219a52")
        self.root.after(600, lambda: self.btn.config(
            bg=ACCENT, activebackground="#6a58e0"))

    # ── Логика палитры ───────────────────────────────────────────────────────

    def _add_to_palette(self) -> None:
        hex_color = self.hex_var.get()
        if hex_color in self._palette:
            self.copy_var.set("Этот цвет уже в палитре")
            return
        if len(self._palette) >= PALETTE_SIZE:
            self._palette.pop(0)
        self._palette.append(hex_color)
        self._render_palette()
        self.copy_var.set(f"✓  {hex_color} добавлен в палитру")

    def _render_palette(self) -> None:
        for w in self.palette_frame.winfo_children():
            w.destroy()

        if not self._palette:
            self.palette_hint.pack(pady=2)
            self.clear_btn.pack_forget()
            return

        self.palette_hint.pack_forget()
        self.clear_btn.pack(pady=(4, 0))

        row = None
        for i, hx in enumerate(self._palette):
            if i % 8 == 0:
                row = tk.Frame(self.palette_frame, bg=BG)
                row.pack(fill="x", pady=2)
            cell = tk.Frame(row, bg=hx, width=30, height=30,
                            cursor="hand2",
                            highlightthickness=1,
                            highlightbackground=BORDER)
            cell.pack(side="left", padx=2)
            cell.pack_propagate(False)
            # Клик — выбрать цвет из палитры
            cell.bind("<Button-1>", lambda e, h=hx: self._pick_from_palette(h))
            cell.bind("<Button-3>", lambda e, h=hx: self._remove_from_palette(h))
            # Подсказка
            tip = tk.Label(cell, text="", bg=hx)
            tip.pack(expand=True)
            tip.bind("<Button-1>", lambda e, h=hx: self._pick_from_palette(h))
            tip.bind("<Button-3>", lambda e, h=hx: self._remove_from_palette(h))

    def _pick_from_palette(self, hex_color: str) -> None:
        r = int(hex_color[1:3], 16)
        g = int(hex_color[3:5], 16)
        b = int(hex_color[5:7], 16)
        self._update_display(r, g, b)
        self._copy_to_clipboard(hex_color)

    def _remove_from_palette(self, hex_color: str) -> None:
        if hex_color in self._palette:
            self._palette.remove(hex_color)
            self._render_palette()

    def _clear_palette(self) -> None:
        self._palette.clear()
        self._render_palette()


def main() -> None:
    root = tk.Tk()
    ColorPickerApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
