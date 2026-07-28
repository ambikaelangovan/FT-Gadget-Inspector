import cirq
# only need to run this file
# connects to other files with circuits, simulations, data

from circuits import CircuitCreation
from faults import FaultInjection
from simulator import Simulator
from steane_code import Steane
from analysis import FaultAnalysis, Visualization

def main():
    """Run the fault-injection experiment."""
    builder = CircuitCreation()
    injector = FaultInjection()
    simulator = Simulator()
    analyzer = FaultAnalysis()
    visualizer = Visualization()
    
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
    print(visualizer.table(baseline_results))

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
        print(visualizer.table(flag_results))

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

    else:
        print(
            "\nComparison skipped because the flag circuit "
            "Flag circuit is not implemented yet."
        )

    #create the summary chart
    summaries = [baseline_summary]
    labels = ["Baseline"]

    if flag_summary is not None:
        summaries.append(flag_summary)
        labels.append("Flagged")

    visualizer.plot_fault_summary(
        summaries,
        labels,
    )

    print("\nExperiment complete.")

#run main() only when this file is executed directly.
if __name__ == "__main__":
    main()