class FaultAnalysis:

    def fault_type(result):
        """takes the simulation results and determines if the fault is correctable/detected by the flag qubit/not correctable"""
        pass

    def compare_circuits(self, baseline_results, flag_results):
        """compares how our different circuits corrected"""
        pass

    def summary(self, results):
        """ would include the total number of faults, correctable faults, non correctable faults; in the form of percentages"""
        pass


class Visualization:

    def plot_summary(self, data):
        """takes in the percentages and outputs a bar chart"""
        pass

    def plot_overhead(self, baseline, flagged):
        """ bar graph of the extra qubits and gates required"""
        pass

    def table_data(self, results):
        """just a tabular representation of the results above"""
        pass