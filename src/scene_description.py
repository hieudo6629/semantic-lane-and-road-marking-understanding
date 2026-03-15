class SceneDescription:

    def __init__(self):
        pass

    def generate(self, scene, road_info):

        lane_count = scene["lane_count"]
        ego_idx = scene["ego_lane"]["index"]

        road_type = road_info["road_type"]

        text = f"The vehicle is traveling in lane {ego_idx+1} of a {lane_count}-lane road. "

        if road_type == "straight":
            text += "The road ahead is straight."
        elif road_type == "left_curve":
            text += "The road ahead curves to the left."
        else:
            text += "The road ahead curves to the right."

        return text