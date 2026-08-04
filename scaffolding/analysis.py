import matplotlib
import matplotlib.pyplot as plt
matplotlib.use("Agg")

import numpy as np

class FaultAnalysis:
    """injects pauli faults throughout the syndrome-extraction circuit,
    classifies the error on each run
    summary across all runs"""

    #distance-3 codes correct one single data qubit error
    CORRECTABLE_WEIGHT = 1

    @staticmethod
    def fault_type(result):
        """takes the simulation results and determines if the fault is correctable/detected by the flag qubit/not correctable"""
        if result.get("flag_flipped"):
            return "detected_by_flag"

        if result["data_error_weight"] <= FaultAnalysis.CORRECTABLE_WEIGHT:
            return "correctable"

        return "not_correctable"


    def sweep(self, circuit, circuit_name, builder, injector, simulator):
        "injects every pauli fault at every location in the circuit"

        results = []
        clean_state = builder.prepare_clean_state()
        locations = injector.fault_locations(circuit)

        data_qubits = set(builder.q)
        syndrome_qubit = builder.syndrome
        flag_qubit = getattr(builder, "flag", None)
        has_flag = flag_qubit is not None and flag_qubit in circuit.all_qubits()

        for moment_index, qubit in locations:
            for pauli in ("X", "Y", "Z"):
                error_pattern = injector.propagate_fault(
                    circuit, (moment_index, qubit), pauli
                )

                data_error_weight = sum(
                    1
                    for data_qubit in data_qubits
                    if error_pattern.get(data_qubit, "I") != "I"
                )

                syndrome_flipped = error_pattern.get(syndrome_qubit, "I") in ("X", "Y")

                flag_flipped = None
                if has_flag:
                    flag_flipped = error_pattern.get(flag_qubit, "I") in ("X", "Y")

                faulty_circuit = injector.inject_faults(circuit, (moment_index, qubit), pauli)
                full_circuit = clean_state + faulty_circuit
                measured = simulator.run_data(full_circuit, repetitions=1)
                measured_syndrome = int(measured["syndrome"][0][0])

                result = {
                    "circuit_name": circuit_name,
                    "moment": moment_index,
                    "qubit": str(qubit),
                    "pauli": pauli,
                    "data_error_weight": data_error_weight,
                    "syndrome_flipped": syndrome_flipped,
                    "flag_flipped": flag_flipped,
                    "measured_syndrome": measured_syndrome,
                }
                result["classification"] = self.fault_type(result)
                results.append(result)

        return results


    def compare_circuits(self, baseline_summary, flag_summary, baseline_circuit, flag_circuit):
        """compares how our different circuits corrected"""
        baseline_qubits = len(baseline_circuit.all_qubits())
        flagged_qubits = len(flag_circuit.all_qubits())
        baseline_gates = len(list(baseline_circuit.all_operations()))
        flagged_gates = len(list(flag_circuit.all_operations()))

        return {
            "baseline_percent": baseline_summary["percent"],
            "flagged_percent": flag_summary["percent"],
            "baseline_qubits": baseline_qubits,
            "flagged_qubits": flagged_qubits,
            "baseline_gates": baseline_gates,
            "flagged_gates": flagged_gates,
            "extra_qubits": flagged_qubits - baseline_qubits,
            "extra_gates": flagged_gates - baseline_gates,
        }


    def summary(self, results):
        """total number of faults, correctable faults, non correctable faults;
        in the form of percentages"""
        counts = {"correctable": 0, "detected_by_flag": 0, "not_correctable": 0}
        for result in results:
            counts[result["classification"]] += 1

        total = len(results)
        percent = {
            category: (count / total * 100 if total else 0.0)
            for category, count in counts.items()
        }

        return {"total": total, "counts": counts, "percent": percent}


###############################


class Visualization:
    """turns the summaries and circuits into tables and figures
    includes results,
    qubit/gate overheads,
    text table"""

    def plot_fault_summary(self, summaries, labels, save_path="fault_summary.png"):
        """takes in the percentages and outputs a bar chart"""
        categories = ["correctable", "detected_by_flag", "not_correctable"]
        category_labels = ["Correctable", "Detected\nby flag", "Not\ncorrectable"]
        x = np.arange(len(categories))
        width = 0.8 / max(len(summaries), 1)

        plt.rcParams.update({
            "font.size": 13,
            "axes.labelsize": 13,
        })

        fig, ax = plt.subplots(figsize=(4.5, 3.4), dpi=200)
        ax.set_title("Flag qubit catches most faults", fontsize=14, loc='left')
        for i, (summary, label) in enumerate(zip(summaries, labels)):
            values = [summary["percent"][category] for category in categories]
            bars = ax.bar(x + i * width, values, width, label=label)
            for bar in bars:
                h = bar.get_height()
                ax.annotate(f"{h:.0f}%", xy=(bar.get_x() + bar.get_width() / 2, h),
                            xytext=(0, 3), textcoords="offset points",
                            ha="center", fontsize=10)

        ax.set_xticks(x + width * (len(summaries) - 1) / 2)
        ax.set_xticklabels(category_labels)
        ax.set_ylabel("% of injected faults")
        ax.legend(fontsize=11, frameon=False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig.tight_layout()
        fig.savefig(save_path)
        plt.close(fig)
        return save_path

    def plot_overhead(self, baseline, flagged, save_path="overhead_comparison.png"):
        """ bar graph comparing qubit/gate overhead between baseline and flag circuit"""
        categories = ["Qubits", "Gates"]
        baseline_values = [len(baseline.all_qubits()), len(list(baseline.all_operations()))]
        flagged_values = [len(flagged.all_qubits()), len(list(flagged.all_operations()))]

        x = np.arange(len(categories))
        width = 0.35

        fig, ax = plt.subplots(figsize=(4.0, 3.4), dpi=200)
        ax.set_title("Overhead of adding the flag qubit", fontsize=14, loc='center')
        bars1 = ax.bar(x - width / 2, baseline_values, width, label="Baseline")
        bars2 = ax.bar(x + width / 2, flagged_values, width, label="Flagged")
        for bars in (bars1, bars2):
            for bar in bars:
                h = bar.get_height()
                ax.annotate(f"{int(h)}", xy=(bar.get_x() + bar.get_width() / 2, h),
                            xytext=(0, 3), textcoords="offset points",
                            ha="center", fontsize=11)

        ax.set_xticks(x)
        ax.set_xticklabels(categories)
        ax.set_ylabel("Count")
        ax.legend(fontsize=11, frameon=False)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        fig.tight_layout()
        fig.savefig(save_path)
        plt.close(fig)
        return save_path

    def table(self, results):
        """just a tabular representation of the results above"""
        header = f"{'Qubit':<8}{'Moment':<8}{'Pauli':<7}{'Weight':<8}{'Classification':<20}"
        lines = [header, "-" * len(header)]
        for result in results:
            lines.append(
                f"{result['qubit']:<8}{result['moment']:<8}{result['pauli']:<7}"
                f"{result['data_error_weight']:<8}{result['classification']:<20}"
            )
        return "\n".join(lines)

    table_date = table