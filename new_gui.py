import tkinter as tk
from tkinter import ttk
import threading
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import talib
from data import BtcGraphData


class CryptoTraderApp(tk.Tk):
    def __init__(self):
        super().__init__()

        self.title("CryptoTrader")
        self.geometry("1200x630")
        self.minsize(980, 560)
        self.configure(bg="#070b16")

        self.colors = {
            "window": "#070b16",
            "topbar": "#1b2038",
            "sidebar": "#171d32",
            "panel": "#1b2038",
            "panel_border": "#40506e",
            "muted": "#a9b8d3",
            "text": "#ffffff",
            "blue": "#2f82ff",
            "blue_dark": "#243d71",
            "button": "#39445b",
            "button_hover": "#48546f",
            "green": "#00e18f",
        }

        self.selected_coin = tk.StringVar(value="BTC")
        self.selected_range = tk.StringVar(value="1h")
        self.selected_indicators = set()

        self.drawing_mode = False
        self.drawings = []
        self.current_stroke = None

        self._setup_style()
        self._build_layout()

    def _setup_style(self):
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure(
            "Crypto.TFrame",
            background=self.colors["window"],
            borderwidth=0,
        )
        style.configure(
            "Top.TFrame",
            background=self.colors["topbar"],
            borderwidth=0,
        )
        style.configure(
            "Sidebar.TFrame",
            background=self.colors["sidebar"],
            borderwidth=0,
        )
        style.configure(
            "Title.TLabel",
            background=self.colors["topbar"],
            foreground=self.colors["text"],
            font=("Segoe UI", 15, "bold"),
        )
        style.configure(
            "Small.TLabel",
            background=self.colors["sidebar"],
            foreground=self.colors["muted"],
            font=("Segoe UI", 8, "bold"),
        )
        style.configure(
            "Header.TLabel",
            background=self.colors["window"],
            foreground=self.colors["text"],
            font=("Segoe UI", 22, "bold"),
        )
        style.configure(
            "Price.TLabel",
            background=self.colors["window"],
            foreground="#28a0ff",
            font=("Segoe UI", 16),
        )
        style.configure(
            "Positive.TLabel",
            background=self.colors["window"],
            foreground=self.colors["green"],
            font=("Segoe UI", 10, "bold"),
        )
        style.configure(
            "Negative.TLabel",
            background=self.colors["window"],
            foreground="#e84142",
            font=("Segoe UI", 10, "bold"),
        )

    def _build_layout(self):
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self._build_topbar()
        self._build_sidebar()
        self._build_main()

    def _build_topbar(self):
        topbar = ttk.Frame(self, style="Top.TFrame", height=55)
        topbar.grid(row=0, column=0, columnspan=2, sticky="nsew")
        topbar.grid_propagate(False)
        topbar.grid_columnconfigure(10, weight=1)

        logo = tk.Label(
            topbar,
            text="↗ CryptoTrader",
            bg=self.colors["topbar"],
            fg=self.colors["text"],
            font=("Segoe UI", 16, "bold"),
        )
        logo.grid(row=0, column=0, padx=(18, 12), pady=13, sticky="w")

        for index, item in enumerate(["5m", "15m", "1h", "4h", "1D"], start=1):
            button = tk.Button(
                topbar,
                text=item,
                command=lambda value=item: self._select_range(value),
                relief="flat",
                bd=0,
                cursor="hand2",
                font=("Segoe UI", 10, "bold"),
                padx=14,
                pady=6,
            )
            button.grid(row=0, column=index, padx=3, pady=13)
            button.bind("<Enter>", lambda event, b=button: self._hover_button(b, True))
            button.bind("<Leave>", lambda event, b=button: self._hover_button(b, False))
            setattr(self, f"range_button_{item}", button)

        self.draw_button = tk.Button(
            topbar,
            text="✐ Çizim",
            command=self._toggle_drawing_mode,
            relief="flat",
            bd=0,
            cursor="hand2",
            bg=self.colors["button"],
            fg=self.colors["text"],
            activebackground=self.colors["button_hover"],
            activeforeground=self.colors["text"],
            font=("Segoe UI", 9, "bold"),
            padx=14,
            pady=7,
        )
        self.draw_button.grid(row=0, column=8, padx=(0, 5), pady=13, sticky="e")

        self.btn_undo = tk.Button(
            topbar, text="↶ Geri Al", command=self._undo_drawing,
            relief="flat", bd=0, cursor="hand2", bg=self.colors["button"], fg=self.colors["text"],
            font=("Segoe UI", 9, "bold"), padx=10, pady=7,
        )

        self.btn_clear = tk.Button(
            topbar, text="Sil", command=self._clear_drawings,
            relief="flat", bd=0, cursor="hand2", bg="#e84142", fg="#ffffff",
            font=("Segoe UI", 9, "bold"), padx=10, pady=7,
        )

        self._refresh_range_buttons()

    def _build_sidebar(self):
        sidebar = ttk.Frame(self, style="Sidebar.TFrame", width=190)
        sidebar.grid(row=1, column=0, sticky="nsew")
        sidebar.grid_propagate(False)

        tk.Label(
            sidebar,
            text="KRİPTO PARALAR",
            bg=self.colors["sidebar"],
            fg=self.colors["muted"],
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=14, pady=(16, 8))

        self.coin_buttons = {}
        coins = [
            ("BTC", "Bitcoin"),
            ("ETH", "Ethereum"),
            ("BNB", "Binance Coin"),
            ("SOL", "Solana"),
            ("XRP", "Ripple"),
        ]
        for symbol, name in coins:
            self.coin_buttons[symbol] = self._nav_card(
                sidebar,
                title=symbol,
                subtitle=name,
                command=lambda value=symbol: self._select_coin(value),
            )

        tk.Label(
            sidebar,
            text="İNDİKATÖRLER",
            bg=self.colors["sidebar"],
            fg=self.colors["muted"],
            font=("Segoe UI", 8, "bold"),
        ).pack(anchor="w", padx=14, pady=(18, 8))

        self.indicator_buttons = {}
        for indicator in ["EMA 10", "EMA 30", "SMA 20", "RSI", "MACD", "Bollinger Bands"]:
            self.indicator_buttons[indicator] = self._indicator_button(sidebar, indicator)

        self._refresh_coin_buttons()

    def _build_main(self):
        main = ttk.Frame(self, style="Crypto.TFrame")
        main.grid(row=1, column=1, sticky="nsew")
        main.grid_columnconfigure(0, weight=1)
        main.grid_rowconfigure(1, weight=1)

        header = ttk.Frame(main, style="Crypto.TFrame")
        header.grid(row=0, column=0, sticky="ew", padx=18, pady=(18, 10))

        self.lbl_coin_name = ttk.Label(header, text="Bitcoin", style="Header.TLabel")
        self.lbl_coin_name.pack(side="left")
        
        self.lbl_coin_price = ttk.Label(header, text="$--", style="Price.TLabel")
        self.lbl_coin_price.pack(side="left", padx=(12, 10), pady=(6, 0))
        
        self.lbl_coin_change = ttk.Label(header, text="--%", style="Positive.TLabel")
        self.lbl_coin_change.pack(side="left", pady=(9, 0))

        chart_frame = tk.Frame(
            main,
            bg=self.colors["panel"],
            highlightbackground=self.colors["panel_border"],
            highlightthickness=1,
        )
        chart_frame.grid(row=1, column=0, sticky="nsew", padx=18, pady=(0, 18))
        chart_frame.grid_columnconfigure(0, weight=1)
        chart_frame.grid_rowconfigure(0, weight=1)

        self.fig = plt.figure(figsize=(8, 6))
        self.fig.patch.set_facecolor(self.colors["panel"])

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_frame)
        self.chart = self.canvas.get_tk_widget()
        self.chart.configure(bg=self.colors["panel"], highlightthickness=0, bd=0)
        self.chart.grid(row=0, column=0, sticky="nsew")
        
        self.chart.bind("<ButtonPress-1>", self._on_draw_start)
        self.chart.bind("<B1-Motion>", self._on_draw_motion)
        self.chart.bind("<ButtonRelease-1>", self._on_draw_release)
        
        self.prices = np.array([])
        self.is_loading = False
        
        self.after(500, self._fetch_and_plot)

    def _nav_card(self, parent, title, subtitle, command):
        frame = tk.Frame(
            parent,
            bg="#1c243a",
            cursor="hand2",
            height=50,
            bd=0,
        )
        frame.pack(fill="x", padx=14, pady=2)
        frame.pack_propagate(False)

        title_label = tk.Label(
            frame,
            text=title,
            bg=frame["bg"],
            fg=self.colors["text"],
            font=("Segoe UI", 9, "bold"),
            anchor="w",
        )
        title_label.pack(anchor="w", padx=14, pady=(8, 0))

        subtitle_label = tk.Label(
            frame,
            text=subtitle,
            bg=frame["bg"],
            fg=self.colors["muted"],
            font=("Segoe UI", 7),
            anchor="w",
        )
        subtitle_label.pack(anchor="w", padx=14)

        for widget in (frame, title_label, subtitle_label):
            widget.bind("<Button-1>", lambda event: command())

        frame.title_label = title_label
        frame.subtitle_label = subtitle_label
        return frame

    def _indicator_button(self, parent, text):
        button = tk.Button(
            parent,
            text=text,
            command=lambda: self._toggle_indicator(text),
            anchor="w",
            relief="flat",
            bd=0,
            cursor="hand2",
            bg="#1c243a",
            fg=self.colors["text"],
            activebackground=self.colors["blue_dark"],
            activeforeground=self.colors["text"],
            font=("Segoe UI", 8, "bold"),
            padx=24,
            pady=8,
        )
        button.pack(fill="x", padx=14, pady=3)
        return button

    def _select_coin(self, symbol):
        self.selected_coin.set(symbol)
        self._refresh_coin_buttons()
        self._fetch_and_plot()

    def _select_range(self, value):
        self.selected_range.set(value)
        self._refresh_range_buttons()
        self._fetch_and_plot()

    def _toggle_indicator(self, indicator):
        if indicator in self.selected_indicators:
            self.selected_indicators.remove(indicator)
        else:
            self.selected_indicators.add(indicator)
        self._refresh_indicator_buttons()
        self._render_plot()

    def _hover_button(self, button, is_hovered):
        if button["text"] == self.selected_range.get():
            return
        button.configure(bg=self.colors["button_hover"] if is_hovered else self.colors["button"])

    def _refresh_range_buttons(self):
        for item in ["5m", "15m", "1h", "4h", "1D"]:
            button = getattr(self, f"range_button_{item}", None)
            if button is None:
                continue
            selected = item == self.selected_range.get()
            button.configure(
                bg=self.colors["blue"] if selected else self.colors["button"],
                fg=self.colors["text"],
                activebackground=self.colors["blue"] if selected else self.colors["button_hover"],
                activeforeground=self.colors["text"],
            )

    def _refresh_coin_buttons(self):
        for symbol, frame in self.coin_buttons.items():
            selected = symbol == self.selected_coin.get()
            bg = self.colors["blue_dark"] if selected else "#1c243a"
            frame.configure(bg=bg, highlightthickness=1 if selected else 0)
            frame.configure(highlightbackground=self.colors["blue"])
            frame.title_label.configure(bg=bg)
            frame.subtitle_label.configure(bg=bg)

    def _refresh_indicator_buttons(self):
        for indicator, button in self.indicator_buttons.items():
            selected = indicator in self.selected_indicators
            button.configure(bg=self.colors["blue_dark"] if selected else "#1c243a")

    def _fetch_and_plot(self):
        if self.is_loading: return
        self.is_loading = True
        
        # Grafik yükleniyor ekranı
        self.fig.clf()
        ax = self.fig.add_subplot(111)
        ax.set_facecolor(self.colors["panel"])
        ax.axis('off')
        ax.text(0.5, 0.5, "Grafik Yükleniyor...", color=self.colors["muted"], 
                ha='center', va='center', transform=ax.transAxes, fontdict={'size': 14})
        self.canvas.draw_idle()
        self.update()
        
        coin = f"{self.selected_coin.get()}/USDT"
        period = self.selected_range.get()
        
        def task():
            try:
                data_fetcher = BtcGraphData(symbol=coin, timeframe=period)
                prices = data_fetcher.run()
                if len(prices) > 0:
                    self.prices = prices
            except Exception as e:
                print("Veri çekme hatası:", e)
            finally:
                self.is_loading = False
                # Call render_plot from main thread
                self.after(0, self._render_plot)

        threading.Thread(target=task, daemon=True).start()

    def _render_plot(self):
        if len(self.prices) == 0: return
        
        current_price = self.prices[-1]
        start_price = self.prices[0]
        change_pct = ((current_price - start_price) / start_price) * 100
        
        self.lbl_coin_name.config(text=f"{self.selected_coin.get()}/USDT")
        if current_price < 10:
            self.lbl_coin_price.config(text=f"${current_price:,.4f}")
        else:
            self.lbl_coin_price.config(text=f"${current_price:,.2f}")
            
        if change_pct >= 0:
            self.lbl_coin_change.config(text=f"+{change_pct:.2f}%", style="Positive.TLabel")
        else:
            self.lbl_coin_change.config(text=f"{change_pct:.2f}%", style="Negative.TLabel")
        
        has_macd = "MACD" in self.selected_indicators
        has_rsi = "RSI" in self.selected_indicators
        
        subplots = 1
        height_ratios = [4]
        if has_macd:
            subplots += 1
            height_ratios.append(1)
        if has_rsi:
            subplots += 1
            height_ratios.append(1)
            
        self.fig.clf()
        axes = self.fig.subplots(subplots, 1, gridspec_kw={'height_ratios': height_ratios})
        
        if subplots == 1:
            axes = [axes]
            
        for ax in axes:
            ax.set_facecolor(self.colors["panel"])
            ax.grid(True, color=self.colors["panel_border"], linestyle='--', alpha=0.5)
            ax.tick_params(axis='x', colors=self.colors["muted"])
            ax.tick_params(axis='y', colors=self.colors["muted"])
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_color(self.colors["panel_border"])
            ax.spines['bottom'].set_color(self.colors["panel_border"])

        main_ax = axes[0]
        main_ax.plot(self.prices, color=self.colors["blue"], label="Fiyat")
        
        if "EMA 10" in self.selected_indicators:
            ema10 = talib.EMA(self.prices, timeperiod=10)
            main_ax.plot(ema10, color='orange', label='EMA 10')
        if "EMA 30" in self.selected_indicators:
            ema30 = talib.EMA(self.prices, timeperiod=30)
            main_ax.plot(ema30, color='red', label='EMA 30')
        if "SMA 20" in self.selected_indicators:
            sma20 = talib.SMA(self.prices, timeperiod=20)
            main_ax.plot(sma20, color='yellow', label='SMA 20')
        if "Bollinger Bands" in self.selected_indicators:
            upper, middle, lower = talib.BBANDS(self.prices, timeperiod=20)
            main_ax.plot(upper, color='cyan', linestyle='dashed', alpha=0.5)
            main_ax.plot(lower, color='cyan', linestyle='dashed', alpha=0.5)
            main_ax.fill_between(range(len(self.prices)), lower, upper, color='cyan', alpha=0.1, label='Bollinger')
            
        main_ax.legend(facecolor=self.colors["panel"], edgecolor=self.colors["panel_border"], labelcolor=self.colors["text"], loc='upper left')
        
        current_idx = 1
        if has_macd:
            macd_ax = axes[current_idx]
            current_idx += 1
            macd, macdsignal, macdhist = talib.MACD(self.prices)
            macd_ax.plot(macd, color=self.colors["blue"], label='MACD')
            macd_ax.plot(macdsignal, color='magenta', label='Signal')
            macd_ax.bar(np.arange(len(macdhist)), macdhist, color='gray', alpha=0.5)
            macd_ax.legend(facecolor=self.colors["panel"], edgecolor=self.colors["panel_border"], labelcolor=self.colors["text"], loc='upper left')

        if has_rsi:
            rsi_ax = axes[current_idx]
            rsi = talib.RSI(self.prices, timeperiod=14)
            rsi_ax.plot(rsi, color='purple', label='RSI')
            rsi_ax.axhline(70, color='red', linestyle='--', alpha=0.5)
            rsi_ax.axhline(30, color='green', linestyle='--', alpha=0.5)
            rsi_ax.legend(facecolor=self.colors["panel"], edgecolor=self.colors["panel_border"], labelcolor=self.colors["text"], loc='upper left')

        self.fig.tight_layout(pad=1.0)
        self.canvas.draw_idle()

    def _toggle_drawing_mode(self):
        self.drawing_mode = not self.drawing_mode
        if self.drawing_mode:
            self.draw_button.configure(bg=self.colors["blue"], activebackground=self.colors["blue"])
            self.btn_undo.grid(row=0, column=9, padx=5, pady=13, sticky="e")
            self.btn_clear.grid(row=0, column=10, padx=(5, 20), pady=13, sticky="e")
            self.chart.config(cursor="crosshair")
        else:
            self.draw_button.configure(bg=self.colors["button"], activebackground=self.colors["button_hover"])
            self.btn_undo.grid_remove()
            self.btn_clear.grid_remove()
            self.chart.config(cursor="")

    def _undo_drawing(self):
        if self.drawings:
            last_stroke = self.drawings.pop()
            for item in last_stroke:
                self.chart.delete(item)

    def _clear_drawings(self):
        for stroke in self.drawings:
            for item in stroke:
                self.chart.delete(item)
        self.drawings.clear()

    def _on_draw_start(self, event):
        if not self.drawing_mode: return
        self.current_stroke = []
        self._last_x = event.x
        self._last_y = event.y

    def _on_draw_motion(self, event):
        if not self.drawing_mode or self.current_stroke is None: return
        line = self.chart.create_line(self._last_x, self._last_y, event.x, event.y, fill="yellow", width=2)
        self.current_stroke.append(line)
        self._last_x = event.x
        self._last_y = event.y

    def _on_draw_release(self, event):
        if not self.drawing_mode or not self.current_stroke: return
        self.drawings.append(self.current_stroke)
        self.current_stroke = None


if __name__ == "__main__":
    app = CryptoTraderApp()
    app.mainloop()