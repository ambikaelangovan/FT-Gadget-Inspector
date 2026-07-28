# only need to run this file
# connects to other files with circuits, simulations, data

from circuits import CircuitCreation
from faults import FaultInjection
from simulator import Simulator
from steane_code import SteaneCode
from analysis import FaultAnalysis, Visualization

def main():
    """Run the fault-injection experiment."""
    builder = CircuitCreation()
    injector = FaultInjection()
    simulator = Simulator()
    analyzer = FaultAnalysis()
    visualizer = Visualization()
    
    #display selected stabilizer
    stabilizer_name = " ".join(
    f"{stabilizer_type}{q}" for q in stabilizer_support
    )

    print("\nSelected stabilizer:", stabilizer_name)
    print("Support:", stabilizer_support)
    print("Weight:", len(stabilizer_support))
    
    #building the baseline circuit
    baseline_circuit = builder.baseline_circuit()
    print("Baseline circuit:")
    print(baseline, "\n")

    #build the flag circuit
    flag_circuit = builder.flag_circuit()
    print("\nFlag-qubit circuit:")
    print(flag_circuit)

        
    # validate fault-free baseline - check if syndrome is correct at initaization since the logical state is in |0>, the syndrome should be 0
    check = builder.encode_logical_zero() + baseline
    bits = sim.measurement_bits(check, repetitions=200)
    print("syndrome on clean logical |0>:", set(bits["syndrome"]), "(must be {0})\n")

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

