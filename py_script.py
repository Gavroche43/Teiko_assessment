import pandas as pd
import matplotlib.pyplot as plt
import argparse
import os

OUTPUT_DIR = "output_data"
global_filepath = None  

"""
@brief Loads a CSV file into a pandas DataFrame.
@param filepath The path to the CSV file.
@return A pandas DataFrame containing the CSV data.
@throws FileNotFoundError If the file does not exist.
@throws ValueError If the file is not a CSV.
@throws RuntimeError If there is an error loading the CSV.
"""
def load_csv(filepath: str, verbose: bool) -> pd.DataFrame:
	global global_filepath
	global_filepath = filepath 
	if verbose:
		print(f"Loading {filepath}...", end="")
	if not os.path.exists(filepath):
		raise FileNotFoundError("Error: File not found")
	if not filepath.lower().endswith(".csv"):
		raise ValueError("Error: Filetype not csv")
	try:
		df = pd.read_csv(filepath)
		if verbose:
			print("complete")
		return df
	except Exception as e:
		raise RuntimeError(f"Error loading csv: {e}")

"""
@brief Cleans the data by dropping rows with missing response and filtering out rows with invalid treatment or project.
"""
def clean_data(data: pd.DataFrame, verbose: bool) -> pd.DataFrame:
	if verbose:
		print(f"Cleaning {global_filepath}...", end="")
	data = data.dropna(subset=['response'])
	data = data[~data['treatment'].str.lower().eq('none')]
	data = data[~data['project'].str.lower().eq('none')]
	if verbose:
		print("complete")
	return data

"""
@brief Calculates relative frequencies of specified cell types.
@param data The input pandas DataFrame.
@return A DataFrame with calculated relative frequencies and additional columns needed for plotting.
"""
def relative_frequencies(data: pd.DataFrame, verbose: bool) -> pd.DataFrame:
	if verbose:
		print(f"Calculating relative frequencies for {global_filepath}...", end="")
	cell_types = ['b_cell', 'cd8_t_cell', 'cd4_t_cell', 'nk_cell', 'monocyte']
	data['total_count'] = data[cell_types].sum(axis=1)
	relative_df = data[cell_types].div(data['total_count'], axis=0)
	relative_df = relative_df.rename(columns=lambda x: f"{x}_percentage")
	columns_keep = ['sample', 'total_count', 'population', 'count', 'response', 'treatment']
	if 'sample_type' in data.columns:
		columns_keep.append('sample_type')
	if 'diagnosis' in data.columns:
		columns_keep.append('diagnosis')
	additional_columns = [col for col in columns_keep if col in data.columns]
	relative_df = pd.concat([data[additional_columns].reset_index(drop=True),
					 relative_df.reset_index(drop=True)], axis=1)
	if verbose:
		print("complete")
	return relative_df

"""
@brief Saves a pandas DataFrame to a CSV file in the output directory.
@param data The DataFrame to be saved.
@param output_path The name of the output CSV file.
"""
def save_output(data: pd.DataFrame, output_path: str, verbose: bool) -> None:
	if verbose:
		print(f"Saving processed data from {global_filepath} to {output_path}...", end="")
	if not output_path.lower().endswith(".csv"):
		output_path += ".csv"
	if not os.path.exists(OUTPUT_DIR):
		os.mkdir(OUTPUT_DIR)
	full_path = os.path.join(OUTPUT_DIR, output_path)
	data.to_csv(full_path, index=False)
	if verbose:
		print("complete")

"""
@brief Generates boxplots for each immune cell population's relative frequencies comparing responders vs non-responders.
@param data DataFrame containing relative frequencies and associated metadata.
@param output_filename The filename for the saved boxplot image.
"""
def plot_rf_boxplots(data: pd.DataFrame, output_filename: str, verbose: bool) -> None:
	if verbose:
		print("Generating boxplots for relative frequencies...", end="")
	if 'treatment' not in data.columns or 'response' not in data.columns:
		raise ValueError("Data must contain 'treatment' and 'response' columns for plotting.")
	plot_data = data[data['treatment'].str.lower() == 'tr1']
	if 'sample_type' in data.columns:
		plot_data = plot_data[plot_data['sample_type'].str.lower() == 'pbmc']
	if 'diagnosis' in data.columns:
		plot_data = plot_data[plot_data['diagnosis'].str.lower() == 'melanoma']
	cell_types = ['b_cell_percentage', 'cd8_t_cell_percentage', 'cd4_t_cell_percentage', 'nk_cell_percentage', 'monocyte_percentage']
	missing_cols = [col for col in cell_types if col not in plot_data.columns]
	if missing_cols:
		raise ValueError(f"Missing expected cell type columns: {missing_cols}")
	fig, axes = plt.subplots(1, len(cell_types), figsize=(5*len(cell_types), 6))
	for ax, cell in zip(axes, cell_types):
		responders = plot_data[plot_data['response'].str.lower() == 'y'][cell]
		non_responders = plot_data[plot_data['response'].str.lower() == 'n'][cell]
		ax.boxplot([responders, non_responders], labels=['Responder', 'Non-responder'])
		ax.set_title(cell.replace('_percentage','').replace('_',' ').title())
		ax.set_xlabel("Response")
		ax.set_ylabel("Relative Frequency")
	fig.suptitle("Relative Frequencies of Immune Cell Populations\n(Treatment: tr1, PBMC samples)" +
				 (" (Melanoma)" if 'diagnosis' in plot_data.columns else ""))
	plt.tight_layout(rect=[0, 0.03, 1, 0.95])
	output_path = os.path.join(OUTPUT_DIR,output_filename)
	plt.savefig(output_path)
	plt.close()
	if verbose:
		print("complete. Boxplot saved as", output_path)

"""
@brief Main function to process the CSV file, calculate relative frequencies on the whole dataset,
       and generate boxplots using cleaned data.
"""
def main():
	parser = argparse.ArgumentParser(description="Process a CSV file to calculate relative frequencies of cell types and generate boxplots comparing responders vs non-responders.")
	parser.add_argument("input_path", type=str, help="Path to input CSV file")
	parser.add_argument("output_path_csv", type=str, help="Output CSV file name")
	parser.add_argument("output_path_boxplot", type=str, help="Output CSV file name")
	parser.add_argument("--verbose", type=bool, default=True, help="Enable verbose output (default: True)")
	args = parser.parse_args()
	df = load_csv(args.input_path, args.verbose)
	rel_freq_df = relative_frequencies(df, args.verbose)
	save_output(rel_freq_df, args.output_path_csv, args.verbose)
	cleaned_df = clean_data(df, args.verbose)
	rel_freq_cleaned_df = relative_frequencies(cleaned_df, args.verbose)
	plot_rf_boxplots(rel_freq_cleaned_df,  args.output_path_boxplot, args.verbose)

if __name__ == "__main__":
	main()
