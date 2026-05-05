"""
    HOW TO RUN: 
        python -m tabu_scripts.testing

"""

def main():
    from tabu_scripts.engine import solve_one_temperature
    from tabu_scripts.output import build_one_temperature_dataframe, format_dataframe_for_export

    spans = [422.9, 387.1, 320, 395, 360, 225, 295.93]            #sample from THA (I) in validation_files
    heights = [-38.28, 2.97, 7.18, 34.2, 36.41, -7.68, -13.31]

    result = solve_one_temperature(
        spans=spans,
        heights=heights,
        conductor_name="Cardinal",
        temperature_C=40,
    )

    print("Ruling span:", result["ruling_span_m"])
    print("BA label:", result["ba_label"])
    print("T_ref:", result["T_ref"])
    print("H_solution:", result["H_solution"])
    print("Solver info:", result["info"])

    df = build_one_temperature_dataframe(result)
    print(format_dataframe_for_export(df))

if __name__ == "__main__":
    main()