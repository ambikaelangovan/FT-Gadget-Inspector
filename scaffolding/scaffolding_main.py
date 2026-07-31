# connects to other files with circuits, simulations, data

import cirq
import csv
import json
import os

from circuits import CircuitCreation
from faults import FaultInjection
from simulator import Simulator
from steane_code import Steane
from analysis import FaultAnalysis, Visualization


#all results/figures/data:
RESULTS_DIR = "results"


def save_results_csv(results, path):
    """fault-sweep results list (made in FaultAnalysis) to csv file"""
    if not results:
        return
    fieldnames = list(results[0].keys())
    with open(path, "w", newline="") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(results)



def save_table_txt(table_text, path):
    """plain text results table (from Visualizatinos) to text file"""
    with open(path, "w") as text_file:
        text_file.write(table_text)


def main():
    """Run the whole fault-injection experiment
    includes builidng both circuits,
    checking them against a clean slate,
    sweepign every single-qubit pauli fault throguh each circuit,
    saving results"""
    builder = CircuitCreation()
    injector = FaultInjection()
    simulator = Simulator()
    analyzer = FaultAnalysis()
    visualizer = Visualization()

    os.makedirs(RESULTS_DIR, exist_ok=True)
    
    #display selected stabilizer
    stabilizer_type = builder.stabilizer_type
    stabilizer_support = builder.stabilizer_support
    stabilizer_name = " ".join(
        f"{stabilizer_type}{q}" for q in stabilizer_support

    )

    print("\nSelected stabilizer:", stabilizer_name)
    print("Support:", stabilizer_support)
    print("Weight:", len(stabilizer_support))
    
    #building the baseline circuit
    baseline_circuit = builder.baseline_circuit()
    print("Baseline circuit:")
    print(baseline_circuit, "\n")

    #build the flag circuit
    try:
        flag_circuit = builder.flag_circuit()
    except NotImplementedError:
        flag_circuit = None

        
    # validate fault-free baseline - check if the syndrome is correct for the prepared clean test state
    # Check the baseline circuit before injecting faults.
    clean_state = builder.prepare_clean_state()
    clean_circuit = clean_state + baseline_circuit

    clean_result = simulator.run_data(
        clean_circuit,
        repetitions=200,
    )

    clean_syndrome = {
        int(measurement[0])
        for measurement in clean_result["syndrome"]
    }

    print("Clean syndrome:", clean_syndrome)
    print("Expected syndrome: {0}")

    if clean_syndrome == {0}:
         print("Baseline circuit passed the clean-state check.")
    else:
         print("Baseline circuit produced the wrong clean syndrome.")

    #find baseline fault locations - places to insert faults 
    baseline_locations = injector.fault_locations(
        baseline_circuit
    )

    print("\nBaseline fault sweep:")
    print(f"Fault locations: {len(baseline_locations)}")
    print("Fault types: X, Y, Z")

    print(f"Total baseline tests: {len(baseline_locations) * 3}")

    #run the baseline fault sweep
    baseline_results = analyzer.sweep(
        circuit=baseline_circuit,
        circuit_name="baseline",
        builder=builder,
        injector=injector,
        simulator=simulator,
    )

    print("\nBaseline results:")
    baseline_table_text = visualizer.table(baseline_results)
    print(baseline_table_text)
    save_table_txt(baseline_table_text, os.path.join(RESULTS_DIR, "baseline_table.txt"))
    save_results_csv(baseline_results, os.path.join(RESULTS_DIR, "baseline_results.csv"))

    baseline_summary = analyzer.summary(
        baseline_results
    )

    print("\nBaseline summary:")

    for category, count in baseline_summary["counts"].items():

        percentage = baseline_summary["percent"][category]

        print(f"{category}: {count} faults ({percentage:.1f}%)")
        
    #run the flag-circuit fault sweep
    flag_summary = None

    if flag_circuit is not None:

        flag_locations = injector.fault_locations(
            flag_circuit
        )

        print("\nFlag-circuit fault sweep:")
        print(f"Fault locations: {len(flag_locations)}")
        print("Fault types: X, Y, Z")
        
        print(f"Total flag tests: {len(flag_locations) * 3}")

        flag_results = analyzer.sweep(
            circuit=flag_circuit,
            circuit_name="flagged",
            builder=builder,
            injector=injector,
            simulator=simulator,
        )

        print("\nFlag-circuit results:")
        flag_table_text = visualizer.table(flag_results)
        print(flag_table_text)
        save_table_txt(flag_table_text, os.path.join(RESULTS_DIR, "flag_table.txt"))
        save_results_csv(flag_results, os.path.join(RESULTS_DIR, "flag_results.csv"))

        flag_summary = analyzer.summary(
            flag_results
        )

        print("\nFlag-circuit summary:")

        for category, count in flag_summary["counts"].items():

            percentage = flag_summary["percent"][category]

            print(f"{category}: {count} faults ({percentage:.1f}%)")

    #compare the two circuits
    if flag_summary is not None:

        print("\nCircuit comparison:")

        comparison = analyzer.compare_circuits(
            baseline_summary,
            flag_summary,
            baseline_circuit,
            flag_circuit,
        )

        print(comparison)

        with open(os.path.join(RESULTS_DIR, "circuit_comparison.json"), "w") as comparison_file:
            json.dump(comparison, comparison_file, indent=2)

    else:
        print(
            "\nComparison skipped because the flag circuit "
            "Flag circuit is not implemented yet."
        )

    # create the summary chart
    summaries = [baseline_summary]
    labels = ["Baseline"]

    if flag_summary is not None:
        summaries.append(flag_summary)
        labels.append("Flagged")

    fault_summary_path = visualizer.plot_fault_summary(
        summaries,
        labels,
        save_path=os.path.join(RESULTS_DIR, "fault_summary.png"),
    )
    print(f"\nSaved fault-outcome comparison figure to {fault_summary_path}")

    # create the overhead chart
    if flag_circuit is not None:
        overhead_path = visualizer.plot_overhead(
            baseline_circuit,
            flag_circuit,
            save_path=os.path.join(RESULTS_DIR, "overhead_comparison.png"),
        )
        print(f"Saved qubit/gate overhead figure to {overhead_path}")

    print(f"\nAll results, tables, and figures were saved to the '{RESULTS_DIR}/' directory.")
    print("\nExperiment complete.")



#run main() only when this file is executed directly.
if __name__ == "__main__":
    main()