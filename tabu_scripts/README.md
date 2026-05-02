# tabu_scripts

This directory contains the numerical, data, and non-GUI workflow scripts for the Tabu project.

## testing.py

This is the simplest script to run directly when a quick non-GUI test is needed.

It is intended as a small manual test harness:
- defines one set of spans and height differences
- runs one temperature case through the current solver workflow
- prints the main numerical outputs
- builds the result dataframe and prints it in formatted form

Recommended run command from the repository root:

```bash
python -m tabu_scripts.testing

## data.py

Stores the conductor catalog and the fixed temperature vector.

Main responsibilities:

define the built-in conductors
store conductor constants such as weight, area, modulus, and reference tensions
return the conductor data for one selected BA class

## formulas.py

Contains the mathematical formulas used by the solver workflow.

Main responsibilities:

calculate the ruling span and BA classification
calculate span lengths
calculate sag values
calculate correction terms used in the output tables

This file should remain purely numerical.

## forward_sweep.py

Contains the forward propagation logic that starts from an assumed first horizontal tension H0 and calculates the horizontal tensions of the following spans.

Main responsibilities:

equivalent same-height span estimate
equivalent sag estimate
propagation of the next-span horizontal tension

This is the mechanical core of the current solver approach.

## solvers.py

Contains the outer solver logic.

Main responsibilities:

calculate total-length error for a trial H0
run the legacy outer iteration that adjusts H0 until the target length is matched

This file should remain focused on solving rather than presentation.

## engine.py

High-level orchestration for one solved case.

Main responsibilities:

receive spans, heights, conductor name, and temperature
calculate the ruling span
select the correct conductor data
select the correct reference tension for the chosen temperature
call the solver
return the full result dictionary

This is the cleanest entry point for both GUI and non-GUI use.

## output.py

Presentation/output layer for solver results.

Main responsibilities:

build pandas dataframes from the result dictionary
format dataframes for display or export

This file should contain formatting and tabular presentation work, not solver logic.