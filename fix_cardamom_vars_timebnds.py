import os
import xarray as xr

# Define paths
base_path = "/groups/esm/renatob/ILAMB_sample/DATA_CARDAMOM"
updated_path = "/groups/esm/renatob/ILAMB_sample/DATA_CARDAMOM_UPDATED"
os.makedirs(updated_path, exist_ok=True)

# Mapping of variable names
varname_mapping = {
    "ABGB": "cVeg", "D_LAI": "lai", "C_som": "cSoil", "NBP": "nbp", "NPP": "npp",
    "tasmin": "tasmin", "tasmax": "tasmax", "reco": "reco", "gpp": "gpp", "npp": "npp",
    "rsds": "rsds", "pr": "pr", "et": "et", "lai": "lai", "resp_auto": "ra", "R_het": "rh",
    "runoff": "runoff", "swe": "swe", "twsa": "twsa", "tas": "tas", "tsl": "tsl",
    "mrsos": "mrsos", "hfdsl": "hfdsl", "ch4": "ch4"
}

# Unit conversion logic
def convert_units(data, varname, old_unit):
    if varname == "et" and old_unit == "mm day-1":
        return data, "mm d-1"
    elif varname == "pr" and old_unit == "mm day-1":
        return data, "mm d-1"
    elif varname == "cVeg" and old_unit == "Mg ha-1":
        return data / 10, "kg m-2"
    elif varname == "cSoil" and old_unit == "gC m-2":
        return data / 1000.0, "kg m-2"
    elif varname == "swe" and old_unit == "cm":
        return data / 100.0, "m"
    elif varname == "twsa" and old_unit == "mm":
        return data / 1000.0, "m"
    elif varname in ["tas", "tasmax", "tasmin"] and old_unit == "deg C":
        return data + 273.15, "K"
    elif varname == "lai" and old_unit == "m2 m-2":
        return data, "1"
    elif varname == "mrsos" and old_unit == "kgH2O m-2":
        return data, "kg m-2"
    elif varname in ["ra", "rh"] and old_unit == "kg m-2 s-1":
        return data * -1., "kg m-2 s-1"
    elif varname == "tsl" and old_unit == "C":
        return data + 273.15, "K"
    #elif varname in ["gpp", "npp", "reco", "nbp"] and old_unit == "kg m-2 s-1":
    #    return data * 1e3 * 86400, "g m-2 d-1"
    else:
        return data, old_unit

# Walk through files
for root, dirs, files in os.walk(base_path):
    for file in files:
        if not file.endswith(".nc"):
            continue

        original_path = os.path.join(root, file)
        relative_path = os.path.relpath(original_path, base_path)
        output_path = os.path.join(updated_path, relative_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        try:
            ds = xr.open_dataset(original_path)
            var_names = list(ds.data_vars.keys())
            original_name = var_names[0]
            standard_name = varname_mapping.get(original_name, original_name)

            da = ds[original_name]

            # Rename if needed
            if original_name != standard_name:
                da.name = standard_name

            # Convert units
            old_unit = da.attrs.get("units", "")
            new_data, new_unit = convert_units(da, standard_name, old_unit)
            new_data.attrs.update(da.attrs)
            new_data.attrs["units"] = new_unit

            # Create output dataset preserving all coords and variables
            ds_out = ds.copy()
            ds_out = ds_out.drop_vars(original_name)
            ds_out[standard_name] = new_data

            # Save to new file
            ds_out.to_netcdf(output_path)
            print(f"✅ {file}: {original_name} → {standard_name}, {old_unit} → {new_unit}")

        except Exception as e:
            print(f"❌ {file} failed: {e}")
