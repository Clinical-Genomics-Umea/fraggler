from fraggler import fraggler
import pandas as pd

pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)

file = "../demo/multiplex.fsa"
fsa_file = fraggler.get_files(file)[0]


fsa = fraggler.parse_fsa(
    fsa_file,
    "LIZ",
    sample_channel="DATA1",
    min_distance_between_peaks=30,
    min_size_standard_height=300,
)
fsa = fraggler.find_size_standard_peaks(fsa)
fsa = fraggler.return_maxium_allowed_distance_between_size_standard_peaks(
    fsa, multiplier=2
)
fsa = fraggler.generate_combinations(fsa)
fsa = fraggler.calculate_best_combination_of_size_standard_peaks(fsa)
fsa = fraggler.fit_size_standard_to_ladder(fsa)
fsa = fraggler.find_peaks_agnostic(
    fsa,
    peak_height_sample_data=300,
    min_ratio=0.15,
    distance_between_assays=15,
    search_peaks_start=115,
)
fsa = fraggler.find_peak_widths(fsa)
fsa = fraggler.find_peaks_with_padding(fsa)
fsa = fraggler.fit_lmfit_model_to_area(fsa, "gauss")
fsa = fraggler.calculate_quotients(fsa)
fsa = fraggler.update_identified_sample_data_peaks(fsa)

# plotting
fraggler.plot_all_found_peaks(fsa).savefig("all_founds_peak.png")
with open("all_founds_peak.png", "rb") as f:
    print(f.read())
    
fraggler.plot_size_standard_peaks(fsa).savefig("plot_size_standard_peaks.png")
with open("plot_size_standard_peaks.png", "rb") as f:
    print(f.read())
    
fraggler.plot_model_fit(fsa).savefig("model_fit.png")
with open("model_fit.png", "rb") as f:
    print(f.read())
    
for i,p in enumerate(fraggler.plot_areas(fsa)):
    name = f"area_plot_{i}.png"
    p.savefig(name)
    
    with open(name, "rb") as f:
        print(f.read())
