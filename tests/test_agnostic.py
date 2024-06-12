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

print(fsa.identified_sample_data_peaks)
print(fsa.best_size_standard)