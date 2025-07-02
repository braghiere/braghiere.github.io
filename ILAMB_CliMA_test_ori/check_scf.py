import xarray as xr
import numpy as np

# Define input and output paths
input_path = "/groups/esm/renatob/ILAMB_sample/DATA/scf/MODIS/MODIS_SnowCover_0.5deg_fraction.nc"
output_path = "/groups/esm/renatob/ILAMB_sample/DATA/scf/MODIS/MODIS_SnowCover_0.5deg_fraction_fixed.nc"

# Open the dataset
ds = xr.open_dataset(input_path)

# Fix scf metadata
ds["scf"].attrs["standard_name"] = "snow_cover_fraction"
ds["scf"].attrs["long_name"] = "Monthly Snow Cover Fraction"
ds["scf"].attrs["units"] = "1"

# Drop _FillValue from lat/lon if present
for coord in ["lat", "lon"]:
    if "_FillValue" in ds[coord].attrs:
        del ds[coord].attrs["_FillValue"]

# Save to a new file
ds.to_netcdf(output_path)
ds.close()

print(f"✅ Fixed NetCDF saved to:\n{output_path}")
