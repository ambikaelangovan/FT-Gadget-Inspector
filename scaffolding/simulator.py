import cirq


class Simulator:
#executes the circuit and collects the data
    def __init__(self):
        self.simulator = cirq.Simulator()

    def run(self, circuit, repetitions=1000):
        """runs the specific chosen circuit"""
        return self.simulator.run(
            circuit,
            repetitions=repetitions,
        )

    def run_data(self, circuit, repetitions):
        """collecting the data from the run"""
        result = self.run(
            circuit,
            repetitions=repetitions,
        )

        return result.measurements

    def detector_occurrences(self, results):
        """gives the detector information (flag, syndrome, etc)"""

        occurances = {}

        for key, measurements in results.items():
            total = len(measurements)
            triggered = sum(1 for measurement in measurements if int(measurement[0]) == 1)

            occurances[key] = {
                "total": total,
                "triggered": triggered,
                "rate" : (triggered/ total) if total else 0
            }

        return occurances
