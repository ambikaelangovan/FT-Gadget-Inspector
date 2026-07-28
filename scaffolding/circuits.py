import cirq
class CircuitCreation:
    
    def __init__(self):
        self.q = cirq.LineQubit.range(7)
        self.syndrome = cirq.LineQubit(7)
        self.flag = cirq.LineQubit(8)
        #stabilizer measured in this project
        self.stabilizer_type = "X"
        self.stabilizer_support = [3, 4, 5, 6]


    def baseline_circuit(self):
        """ standard ancilla stabilizer measurement circuit"""
        circuit = cirq.Circuit()

        #prepare the syndrome ancilla in the |+> state
        circuit.append(cirq.H(self.syndrome))

        #couple the syndrome ancilla to each data qubit
        for index in self.stabilizer_support:
            circuit.append(
                cirq.CNOT(self.syndrome, self.q[index])
            )

        #return the syndrome ancilla to the Z basis
        circuit.append(cirq.H(self.syndrome))

        circuit.append(
            cirq.measure(self.syndrome, key="syndrome")
        )

        return circuit

    def prepare_clean_state(self):
        """Prepare the data qubits for a clean X-stabilizer test."""
        circuit = cirq.Circuit()

        data_qubits = [2,4,5,6]
        for index in data_qubits:
            circuit.append(cirq.H(self.q[index]))

        circuit.append(cirq.CNOT(self.q[2], self.q[0]))
        circuit.append(cirq.CNOT(self.q[4], self.q[0]))
        circuit.append(cirq.CNOT(self.q[6], self.q[0]))

        circuit.append(cirq.CNOT(self.q[2], self.q[1]))
        circuit.append(cirq.CNOT(self.q[5], self.q[1]))
        circuit.append(cirq.CNOT(self.q[6], self.q[1]))

        circuit.append(cirq.CNOT(self.q[4], self.q[3]))
        circuit.append(cirq.CNOT(self.q[5], self.q[3]))
        circuit.append(cirq.CNOT(self.q[6], self.q[3]))

        return circuit



    
    def flag_circuit(self):
        """flag-qubit stabilizer measurement circuit"""
        raise NotImplementedError(
            "Flag circuit will be added after confirming the circuit diagram."
        )


    def get_circuit(self, circuit_type):
        """either baseline or flag qubit"""
        if circuit_type == "baseline":
            return self.baseline_circuit()

        if circuit_type == "flag":
            return self.flag_circuit()

        raise ValueError(
            "circuit_type must be either 'baseline' or 'flag'"
        )
if __name__ == "__main__":
    builder = CircuitCreation()
    baseline = builder.baseline_circuit()
    print(baseline)