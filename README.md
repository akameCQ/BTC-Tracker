# 📈 CryptoTrader (BTC Tracker)

CryptoTrader is a modern and dynamic cryptocurrency technical analysis interface built with Python. It fetches asynchronous real-time data via the **Binance API** and provides investors with a quick market analysis using popular indicators.

<img width="1509" height="831" alt="Ekran görüntüsü 2026-05-07 204857" src="https://github.com/user-attachments/assets/6ce6c225-ca4a-4801-8374-1569466588a6" />

## ✨ Features

- **⚡ Real-Time Data:** Asynchronous data fetching from Binance via the CCXT library.
- **🎨 Modern Dark Theme:** An eye-friendly Tkinter interface designed with sleek color palettes.
- **📊 Dynamic Chart Layout:** 
  - Clean main price chart powered by Matplotlib.
  - Overlay indicators such as **EMA, SMA, Bollinger Bands** are integrated directly onto the main price chart.
  - Oscillators like **MACD, RSI** open as dynamic new panes at the bottom of the chart when selected, keeping the layout clean when not in use.
- **🪙 Quick Toggles:** 1-click switching between cryptocurrencies (BTC, ETH, BNB, SOL, XRP) and timeframes (5m, 15m, 1h, 4h, 1D).
- **📝 Drawing Tool:** Interactive pen tool to draw freehand lines (support/resistance, etc.) directly on the chart, complete with Undo and Clear All functions.
- **📉 Dynamic Header:** Smart top menu displaying the live price and percentage change of the selected cryptocurrency with dynamic colors (green/red).

## 🚀 Installation

To run the project locally, follow these steps:

1. Clone or download this repository to your computer.
2. Ensure Python is installed (Python 3.8+ recommended).
3. Open your terminal in the project directory and run the following command to install required dependencies:
   ```bash
   pip install -r requirements.txt
   ```
   *(If the requirements file is missing, install the core modules: `pip install ccxt pandas numpy matplotlib nest_asyncio TA-Lib`)*

## 💻 Usage

To start the system, run the project from your terminal/command prompt:

```bash
python new_gui.py
```
> **Note:** If you are using an IDE (Spyder, Jupyter, etc.) and encounter errors due to background processes not closing properly (e.g., _RuntimeError_), restarting the console/kernel (`Restart Kernel`) will resolve the issue.

## 🛠️ Technologies Used

- **GUI:** Tkinter (modified with `ttk` elements)
- **Data Provider:** CCXT (Asynchronous Binance API)
- **Charting:** Matplotlib (integrated with Tkinter via `FigureCanvasTkAgg`)
- **Technical Analysis:** TA-Lib
- **Data Manipulation:** Pandas, NumPy
