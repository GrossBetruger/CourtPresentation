import pandas as pd
import json

if __name__ == "__main__":
    for i, row in pd.read_csv("users_control_table.csv").iterrows():
        name, user, = row[0], row[1]
        print(f"insert into user_meta(user_name, full_name) values ('{user}', '{name}');")