## 🧩 What “Build Your Own” Actually Looks Like

A DIY Geiger counter consists of several essential subsystems. Each subsystem is simple on its own, and together they form a clean, Pi‑friendly, open‑source detector.

### 1. GM Tube (Alpha‑capable or Beta/Gamma‑only)
Tube selection determines the radiation types detected.

**Alpha/Beta/Gamma (mica‑window tubes):**
- LND 712 (end‑window, premium, compact)
- LND 7317 (pancake, “universal” survey‑meter style)
- SBT‑9 (budget alpha tube when available)

These tubes provide:
- Alpha sensitivity through the mica window
- Strong beta response
- Usable gamma response

**Beta/Gamma‑only (metal‑jacket tubes):**
- **SBM‑20** (widely available, stable, excellent for background monitoring)
- STS‑5 (similar to SBM‑20)
- M4011 (common in low‑cost counters)

These tubes provide:
- Strong beta response
- Good gamma response
- No alpha sensitivity due to metal walls

### 2. High‑Voltage Supply (350–500V)
A stable HV source is required to bias the tube:
- Flyback converter or boost converter
- Adjustable output (typically 350–500V)
- Low ripple to avoid false pulses

Possible implementations:
- DIY HV board
- Ready‑made HV module
- Open‑source HV design

### 3. Pulse Detection + Shaping
The tube produces small, fast pulses that require conditioning:
- Resistor network
- Coupling capacitor
- Transistor or comparator stage
- Clean digital pulses at 3.3V or 5V

This stage ensures:
- No double‑counting
- No noise spikes
- A clean rising edge for the Pi or MCU

### 4. Microcontroller (Optional but Recommended)
A microcontroller improves timing accuracy and provides a clean interface:
- Arduino Nano
- ESP32
- ATtiny85
- RP2040

Typical responsibilities:
- Pulse counting
- CPS/CPM calculation
- Debouncing
- Dose‑rate estimation
- Serial output formatting

### 5. Output Protocol
The detector’s output format defines how pi‑log ingests data. Common patterns include:

**Simple serial text:**
```
CPS: 12
CPM: 720
uSv/h: 0.18
```

**JSON:**
```
{"device":"GC-DEV-01","cpm":720,"usvh":0.18}
```

**Raw pulses:**
- Pi counts GPIO edges directly
- MCU not required

### Summary
A DIY Geiger counter typically includes:
- A GM tube (mica‑window for alpha detection, or metal‑jacket for beta/gamma only)
- A stable HV supply
- A pulse‑shaping stage
- An optional microcontroller for clean serial output

This configuration produces a fully open, fully hackable detector suitable for integration with pi‑log and LogExp.
