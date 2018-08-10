# Barra_CNE5
Provide risk forecasts by Barra China Equity Model

## Code Usage

1. `data.py` Extract data from Wind database.

2. `style_factor.py` Build style factors.

3. `factor_exposure.py` Prepare factor exposures data for regression: truncate, winsorize and normalize style factors, build industry factors.Return a dataframe with hierarchy index (datetime, code) and columns containing: industry factors, 10 style factors, daily return and weight.

4. `regression.py` Calculate factor returns by weighted linear regression. Predict risk by factor returns.

5. `utility.py` Some utility functions.
