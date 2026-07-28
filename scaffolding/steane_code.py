class Steane:

    def __init__(self):
        "initializing the steane stabilizer generators"
        self.stabilizers = {
            "X" : [[3,4,5,6]]
        }


    def stabilizers(self):
        "returns the steane stabilizer generator, form of a dictionary"
        return self.stabilizers

    def decode(self, syndrome):
        "takes in the measured syndrome returns which corrections needs to be applied to which qubit"\

        if syndrome == 0:
            return {
                "detected" : False,
                "corrections" : None,
                "message" : "No error detected"
            }

        elif syndrome == 1:
            return {
                "detected" : True,
                "corrections" : "Unknown",
                "message" : "Error detected"
            }

        else:
            raise ValueError("Invalid syndrome: must be 0 or 1")


    def correctable(self, error):
        "is the error fixable by steane code or not?"

        if error is None:
            return True

        if not isinstance(error, dict):
            raise TypeError("Invalid syndrome: must be a dictionary")

        qubit = error.get("qubit")

        if qubit is not None and 0<=qubit<=6 :
            return True

        return False
    