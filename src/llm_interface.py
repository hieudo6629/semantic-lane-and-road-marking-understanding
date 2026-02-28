class SimpleLLM:

    def generate(self, structure):
        lane_count = structure["lanes"]["count"]
        ego = structure["lanes"]["ego_lane_index"]

        return (
            f"There are {lane_count} lanes detected. "
            f"The vehicle is in lane index {ego}. "
            f"It is recommended to maintain current lane and monitor traffic conditions."
        )