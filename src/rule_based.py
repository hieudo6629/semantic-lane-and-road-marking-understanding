class RuleBasedIndication:

    def generate(self, structure):
        lane_count = structure["lanes"]["count"]
        ego = structure["lanes"]["ego_lane_index"]

        if lane_count <= 1:
            return "Single lane road. Keep lane."

        if ego == 0:
            return "Vehicle is in leftmost lane."
        elif ego == lane_count - 1:
            return "Vehicle is in rightmost lane."
        else:
            return "Vehicle is in middle lane."