from datetime import date

from attribute_finder.type import *

def parse_hypen(date: date) -> str:
    return f"{date.year}-{date.month}-{date.day}"

def revert_scale(input: Input_Data, output: Output_Data, meta_scaler: Scaler_Meta) -> tuple[Input_Data, Output_Data]:
    input.day_data = input.day_data * meta_scaler.day_data_std + meta_scaler.day_data_mean
    input.month_data = input.month_data * meta_scaler.month_data_std + meta_scaler.month_data_mean
    input.quarter_data = input.quarter_data * meta_scaler.quarter_data_std + meta_scaler.quarter_data_mean
    input.flat_data = input.flat_data * meta_scaler.flat_data_std + meta_scaler.flat_data_mean
    output.short_term_result = output.short_term_result * meta_scaler.result_std + meta_scaler.result_mean
    output.mid_term_result = output.mid_term_result * meta_scaler.result_std + meta_scaler.result_mean
    output.long_term_result = output.long_term_result * meta_scaler.result_std + meta_scaler.result_mean
    return input, output