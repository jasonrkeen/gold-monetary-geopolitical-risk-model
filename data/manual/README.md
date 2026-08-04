# Optional manual data

`central_bank_demand.csv` accepts quarterly or monthly net official-sector gold
purchases. Leave it header-only if no licensed or manually reviewed series is
available. The model then assigns a neutral value of 50 to that component and
records the limitation in its data-status output.

Required columns:

- `date`
- `net_purchases_tonnes`
- `source`
- `notes`

Do not paste data into this file unless its licensing and citation requirements
permit reuse.

