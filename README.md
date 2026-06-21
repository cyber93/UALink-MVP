# UALink 200 Prototype

Python prototype for UALink Rev 1.0 Spec. Includes UPLI, TL, DL, Switch, and System models.

## Setup

1. Run `setup.bat`.
   - Creates `venv`.
   - Installs `pytest`.

## Verify

```powershell
venv\Scripts\activate
pytest
```

## Run Simulation

Deep trace simulation output to `simulation.log`:
```powershell
python -m ualink.simulation.testbench
```
