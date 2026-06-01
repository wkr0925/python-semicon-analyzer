# Semiconductor Device Analyzer

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

A Python tool for automated analysis and visualization of MOSFET semiconductor device characteristics. Designed for microelectronics students and researchers.

## Features

- **Transfer Characteristic Analysis (Id-Vgs)**: Semi-log plots showing subthreshold, linear, and saturation regions
- **Output Characteristic Curves (Id-Vds)**: Family of curves with varying Vgs, clearly marking linear and saturation regions
- **Threshold Voltage Extraction**: Automatic Vth extraction using linear extrapolation method (max transconductance point)
- **Transconductance Analysis**: gm curve with max gm point identification
- **Professional Output**: Publication-quality SVG vector graphics, ready for lab reports and papers
- **Dual Mode**: Built-in demo data for quick start, or load your own CSV measurement data

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run with built-in demo data
python semicon_analyzer.py --demo

# 3. Or analyze your own CSV data
python semicon_analyzer.py -f data/mosfet_transfer.csv
```

## Usage

```
python semicon_analyzer.py [OPTIONS]

Options:
  --demo          Use built-in n-channel enhancement MOSFET demo data
  -f, --file PATH Load data from CSV file
  -o, --output DIR Output directory for plots (default: output/)
```

## Sample Data Format

```csv
# Comment lines start with #
Vgs,Id
0.0,1.00e-12
0.5,5.30e-09
1.0,2.00e-07
...
```

Supports CSV format with headers `Vgs,Id` for transfer characteristics or `Vds,Id` for output characteristics.

## Output Examples

The tool generates 3 plots:

| Plot | Description |
|------|-------------|
| `transfer_curve.svg` | MOSFET Transfer Characteristic (Id vs Vgs, semi-log) with Vth extraction |
| `output_curves.svg` | Output Characteristic Family (Id vs Vds) showing linear & saturation regions |
| `transconductance.svg` | Transconductance gm vs Vgs with max gm point |

## Technical Background

### Threshold Voltage Extraction

The threshold voltage Vth is extracted using the **Linear Extrapolation Method**:

1. Smooth the Id-Vgs data with a sliding window
2. Calculate transconductance gm = dId/dVgs
3. Find the point of maximum gm (strong inversion point)
4. Draw a tangent line through this point
5. The intersection of the tangent with the Vgs axis gives Vth

### MOSFET Model

The built-in demo uses a simplified n-channel enhancement MOSFET model:

- **Linear Region** (Vds < Vgs - Vth): Id = K 脳 [2(Vgs-Vth)Vds - Vds虏]
- **Saturation Region** (Vds 鈮?Vgs - Vth): Id = K 脳 (Vgs-Vth)虏 脳 (1 + 位Vds)

## Project Structure

```
python-semicon-analyzer/
鈹溾攢鈹€ semicon_analyzer.py      # Main script
鈹溾攢鈹€ requirements.txt         # Python dependencies
鈹溾攢鈹€ data/
鈹?  鈹溾攢鈹€ mosfet_transfer.csv  # Sample transfer characteristic data
鈹?  鈹斺攢鈹€ mosfet_output.csv    # Sample output characteristic data
鈹溾攢鈹€ output/                  # Generated plots (SVG + PNG)
鈹斺攢鈹€ README.md
```

## Requirements

- Python 3.8+
- numpy >= 1.21.0
- matplotlib >= 3.5.0

## License

MIT License 鈥?feel free to use and modify for your coursework and research.
