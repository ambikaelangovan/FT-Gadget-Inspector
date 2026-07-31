import cirq

class FaultInjection:

    PAULI_GATES = {"X": cirq.X, "Y": cirq.Y, "Z": cirq.Z}

    # Symplectic (x_bit, z_bit) representation of each single-qubit Pauli.
    _TO_BITS = {"I": (0, 0), "X": (1, 0), "Z": (0, 1), "Y": (1, 1)}
    _TO_LABEL = {bits: label for label, bits in _TO_BITS.items()}


    def fault_locations(self, circuit):
        """returns possible locations the fualt is in the circuit"""
        locations = []
        for moment_index, moment in enumerate(circuit):
            for op in moment.operations:
                if cirq.is_measurement(op):
                    continue
                for qubit in op.qubits:
                    locations.append((moment_index, qubit))
        return locations

    def inject_faults(self, circuit, location, pauli_fault):
        if pauli_fault not in self.PAULI_GATES:
            raise ValueError("pauli_fault must be 'X', 'Y', or 'Z'")

        moment_index, qubit = location
        gate = self.PAULI_GATES[pauli_fault]

        faulty_circuit = circuit.copy()
        faulty_circuit.insert(
            moment_index + 1,
            gate(qubit),
            strategy=cirq.InsertStrategy.NEW_THEN_INLINE,
        )
        return faulty_circuit


    def all_faults(self, circuit):
        """each combination of the faults and where they are """
        return [
            (location, pauli)
            for location in self.fault_locations(circuit)
            for pauli in ("X", "Y", "Z")
        ]


    def propagate_fault(self, circuit, location, pauli_fault):
        moment_index, fault_qubit = location

        frame = {qubit: self._TO_BITS["I"] for qubit in circuit.all_qubits()}
        frame[fault_qubit] = self._TO_BITS[pauli_fault]

        for moment in list(circuit)[moment_index + 1:]:
            for op in moment.operations:
                if cirq.is_measurement(op):
                    continue
                self._apply_gate(op, frame)

        return {qubit: self._TO_LABEL[bits] for qubit, bits in frame.items()}


    def _apply_gate(self, op, frame):
        gate = op.gate
        qubits = op.qubits

        if isinstance(gate, cirq.HPowGate) and gate.exponent % 2 == 1:
            q = qubits[0]
            x, z = frame[q]
            frame[q] = (z, x)  # H swaps the X and Z components

        elif isinstance(gate, cirq.CXPowGate) and gate.exponent % 2 == 1:
            control, target = qubits
            xc, zc = frame[control]
            xt, zt = frame[target]
            # CNOT: X on control spreads to the target; Z on target
            # spreads back to the control.
            frame[control] = (xc, zc ^ zt)
            frame[target] = (xt ^ xc, zt)

        elif isinstance(gate, (cirq.XPowGate, cirq.YPowGate, cirq.ZPowGate)):
            # A Pauli gate commutes with itself, so it doesn't change the
            # propagating error frame (this is what lets us insert the
            # fault itself as a Pauli gate without disturbing the model).
            pass

        else:
            raise NotImplementedError(
                f"Fault propagation isn't implemented for gate: {gate!r}. "
                "Extend FaultInjection._apply_gate if a new circuit "
                "(e.g. the flag circuit) introduces additional gate types."
            )

