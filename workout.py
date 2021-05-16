import matplotlib.pyplot as plt
import sqlite3
from datetime import datetime, timedelta

db = "workout.db"
reference_date = datetime(1993, 10, 12)


def interpolate(x1, x2, x3, y1, y3):
    return ((x2 - x1) / (x3 - x1)) * (y3 - y1) + y1


def convert_duration(duration):
    dur = duration.split(":")
    if len(dur) == 1:
        return timedelta(seconds=int(dur[0]))
    elif len(dur) == 2:
        return timedelta(minutes=int(dur[0]), seconds=int(dur[1]))
    elif len(dur) == 3:
        return timedelta(
            hours=int(dur[0]), minutes=int(dur[1]), seconds=int(dur[2])
        )
    else:
        return duration


def convert_date(date):
    date = date.split("/")
    date = datetime(int(date[0]), int(date[1]), int(date[2]))
    return (date - reference_date).days


def main_menu():
    while True:
        x = input("[P]lot, [V]iew records, [A]dd record, or [Q]uit: ").lower()
        if x in ["p", "plot"]:
            plot_workout()
        elif x in ["v", "view"]:
            view_records()
        elif x in ["a", "add"]:
            add_record()
        elif x in ["q", "quit", "exit"]:
            break
        else:
            print("Command not found.")


def transpose(data):
    new_data = [[], [], [], [], []]
    for row in data:
        for id, column in enumerate(row):
            new_data[id].append(column)
    return new_data


def plot_workout():
    conn = sqlite3.connect(db)
    with conn:
        c = conn.cursor()
        c.execute("""SELECT * FROM workout ORDER BY date ASC""")
        rows = c.fetchall()
    conn.close()
    conn = None
    data = transpose(rows)

    dates = []
    for date in data[0]:
        this_date = reference_date + timedelta(days=date)
        dates.append(this_date)

    weights = []
    for index, weight in enumerate(data[1]):
        if weight == 0:
            prev_weight_index = index - 1
            prev_weight = weights[prev_weight_index]
            next_weight_index = index + next(
                (i for i, x in enumerate(data[1][index:]) if x), None
            )
            next_weight = data[1][next_weight_index]
            this_weight = interpolate(
                prev_weight_index,
                index,
                next_weight_index,
                prev_weight,
                next_weight,
            )
            weights.append(this_weight)
        else:
            weights.append(weight)

    avg_weights_dates = dates[6:]
    avg_weights = []
    for index, weight in enumerate(weights[6:]):
        # if index < 6:
        #     continue
        sub_weights = weights[index : index + 6]
        avg_weights.append(sum(sub_weights) / len(sub_weights))

    fig, axs = plt.subplots(2, sharex=True)
    fig.suptitle("Kenny's Workouts")
    daily_weight = axs[0].plot(
        dates, weights, color="gray", linewidth=1, label="Daily Weight"
    )
    average_weight = axs[0].plot(
        avg_weights_dates,
        avg_weights,
        color="black",
        linewidth=4,
        label="7-Day Moving Average Weight",
    )
    axs[0].set_title("Weight")
    axs[0].set(ylabel="Weight (Pounds)")
    axs[0].legend(
        # bbox_to_anchor=(0.0, 2.5, 1.0, 0.102),
        handles=[daily_weight[0], average_weight[0]],
        loc="lower left",
        # ncol=2,
    )
    # axs[1] = ax1.twinx()
    axs[1].bar(dates, data[3])
    axs[1].set_title("Calories Burned")
    axs[1].set(xlabel="Date", ylabel="Calories")
    plt.show()


def view_records():
    conn = sqlite3.connect(db)
    with conn:
        c = conn.cursor()
        c.execute("""SELECT * FROM workout ORDER BY date ASC""")
        rows = c.fetchall()
        for row in rows:
            print(row)
    conn.close()
    conn = None


def add_record():
    date = convert_date(input("Date: "))
    weight = input("Weight: ")
    duration = convert_duration(input("Duration: ")).total_seconds()
    calories = input("Calories: ")
    distance = input("Distance: ")
    conn = sqlite3.connect(db)
    with conn:
        c = conn.cursor()
        c.execute(
            f"""INSERT INTO workout VALUES
                ({date}, {weight}, {duration}, {calories}, {distance})"""
        )
    conn.close()
    conn = None


def initial_db():
    conn = sqlite3.connect(db)
    with conn:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE workout
               (date INT,
               weight REAL,
               duration INT,
               calories REAL,
               distance REAL)"""
        )
    conn.close()
    conn = None


# initial_db()
main_menu()
