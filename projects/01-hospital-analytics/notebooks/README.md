# Notebooks

Reserved for exploratory analysis, development support, and validation notebooks related to the hospital analytics project.

Notebook exploration should reuse the project modules in `src/` instead of copying pipeline logic into notebooks.

For Bronze profiling, import and call:

```python
from ingestion.raw_inventory import get_raw_data_dir, list_supported_data_files
from processing.bronze.profiling import profile_csv_file, select_main_csv_file

csv_files = list_supported_data_files(get_raw_data_dir())
main_csv = select_main_csv_file(csv_files)
profile = profile_csv_file(main_csv)
profile
```
