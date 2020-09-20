from typing import List, Tuple

import pandas as pd


def parse_coordinates_data(csv_file_name: str) -> List[Tuple[str, str, float, float]]:
    result = []
    users = pd.read_csv(csv_file_name)
    for user_data in users[["יוזר", "longitude and latitude", "שם מלא"]].itertuples():
        if not str(user_data[2]) == "nan":
            user_name, raw_coords, presentable_name = user_data[1], user_data[2], user_data[3]
            latitude, longitude = [float(x) for x in str(raw_coords).split(",")]
            result.append((user_name, presentable_name, latitude, longitude))
    return result


if __name__ == "__main__":
    for _ in parse_coordinates_data("users.csv"):
        print(_)

