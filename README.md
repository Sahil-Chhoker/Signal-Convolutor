# Signal Convolutor

I wanted to visualize the actual "flip and slide" mechanics of convolution, so I built this interactive environment.

It runs on Streamlit and lets you define two signals (Square, Triangle, Sine, etc.) to see how they interact mathematically without just staring at formulas.


**What can you do?**

- **Signal Controls:** You can set the frequency, amplitude, and offsets for two independent signals.

- **Animation:** Hit 'Start' to watch the second signal flip and slide across the first one.

- **Visual Math:** It highlights the overlapping area (the product) and draws the resulting convolution graph step-by-step so you can see how the integral accumulates.

Good for getting a better intuition of why certain shapes produce specific outputs (like why two square waves make a triangle).

# How to run
1. Install dependencies
```python
pip install -r requirements.txt
```

2. Run streamlit app
```python
streamlit run app.py
```