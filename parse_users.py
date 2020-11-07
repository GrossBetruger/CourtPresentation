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


def generate_metabase_map_query(user_data: List[Tuple[str, str, float, float]]) -> str:
    def generate_line(user_name: str, full_name: str, latitude: float, longitude: float) -> str:
        hebrew_field_name = "שם"
        return f"""select '{user_name}' as user_name, {latitude} as latitude, {longitude} as longitude, '{full_name}' as \"{hebrew_field_name}\""""
    lines = []

    for item in user_data:
        user, name, lat, long = item
        lines.append(generate_line(user, name, lat, long))

    return "\nunion\n".join(lines)


if __name__ == "__main__":
    data = parse_coordinates_data("users.csv")
    print(generate_metabase_map_query(data))



