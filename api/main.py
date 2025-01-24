from nicegui import ui
import pandas as pd
from ipywidgets import interact, Dropdown
from IPython.display import display, HTML
import numpy as np
import ssl

ssl._create_default_https_context = ssl._create_unverified_context

try:
    data = pd.read_csv('https://docs.google.com/spreadsheets/d/' + 
                   '1M4VT4eXXPj5UL7Xn8s5B1yu_taULnGQ3jHKzmG14rIA' +
                   '/export?gid=0&format=csv',
                   # Set first column as rownames in data frame
                   index_col=0
                  )
except:
    None

data = data.reset_index().values.tolist()

courses = []
for round in data:
    if round[1] not in courses:
        courses += [round[1]]

course_layouts = {"All":"-"}

for course in courses:
    layouts = []
    for round in data:
        if round[1] == course:
             if round[2] not in layouts:
                layouts += [round[2]]
    if len(layouts)>1:
        layouts = ["All"] + layouts
    course_layouts[course] = layouts

# Variables to hold the selected course and layout
Course = None
Layout = None


# Function to update the second select input based on the first selection
def update_values(selected):
    global Course, Layout
    if selected is not None:
        # If "All" is selected, the layout dropdown will only have "-"
        if selected == "All":
            options = ["-"]
        else:
            # Get the layouts for the selected course
            options = course_layouts.get(selected, [])
        
        # Update the layout dropdown options
        values_select.options = options
        values_select.value = options[0]  # Default to the first value in the list
        values_select.update()  # Force the UI to refresh the options
        Course = selected
        Layout = options[0]  # Set the layout to the first option (either "-" or a layout)
        rest(Course, Layout)  # Call the rest function whenever selection changes

# Function to update the selected layout value
def update_selected_value(event):
    global Layout
    if event.value is not None:
        Layout = event.value
        rest(Course, Layout)  # Call the rest function whenever selection changes


def rest(Course, Layout):
    container.clear()
    dates = []
    for rounds in data:
        if Course == "All":
            date = rounds[3]
        elif Layout == "All":
            if rounds[1] == Course:
                date = rounds[3]
        elif rounds[1] == Course and rounds[2] == Layout:
            date = rounds[3]
        try:
            if date not in dates:
                dates += [date]
        except:
            None
    dates.sort(reverse=True)

    rounds = {}

    for date in dates:
        ting = []
        for go in data:
            if go[3] == date:
                ting += [go]
        rounds[date] = ting
    rounds_data = {}
    for key in rounds.keys():
        pars = []
        for hole in rounds[key][0][8:]:
            if not np.isnan(hole):
                pars += [int(hole)]
        holes = len(pars)

        kavs = []
        nethidus = []
        mahiths = []
        rounds_data[key] = []
        for go in rounds[key]:
            if go[0] == "Kav":
                kav_total = go[5]
                kav_score = go[6]
                for hole in go[8:]:
                    if not np.isnan(hole):
                        if hole != 0:
                            kavs += [int(hole)]
                        else:
                            kavs += ["-"]
            if go[0] == "Nethidu":
                net_total = go[5]
                net_score = go[6]
                for hole in go[8:]:
                    if not np.isnan(hole):
                        if hole != 0:
                            nethidus += [int(hole)]
                        else:
                            nethidus += ["-"]
            if go[0] == "Mahith":
                mah_total = go[5]
                mah_score = go[6]
                for hole in go[8:]:
                    if not np.isnan(hole):
                        if hole != 0:
                            mahiths += [int(hole)]
                        else:
                            mahiths += ["-"]
        if len(kavs) == 0:
            kavs = ["Kav"] + ["-"] * (len(pars) + 2)
        else:
            kavs = ["Kav"] + kavs + [int(kav_total), int(kav_score)]
        if len(nethidus) == 0:
            nethidus = ["Nethidu"] + ["-"] * (len(pars) + 2)
        else:
            nethidus = ["Nethidu"] + nethidus + [int(net_total), int(net_score)]
        if len(mahiths) == 0:
            mahiths = ["Mahith"] + ["-"] * (len(pars) + 2)
        else:
            mahiths = ["Mahith"] + mahiths + [int(mah_total), int(mah_score)]

        header = ["Hole"] + list(range(1, len(pars) + 1)) + ["Total", "+/-"]
        pars = ["Par"] + pars + [sum(pars), "-"]
        round_data = [header, pars, kavs, nethidus, mahiths]
        rounds_data[key] = round_data

    try:
        if not (Course == "All" or Layout == "All"):
            kav_datas = []
            net_datas = []
            mah_datas = []
            for key in rounds_data.keys():
                kav_score = rounds_data[key][2][-1]
                net_score = rounds_data[key][3][-1]
                mah_score = rounds_data[key][4][-1]

                if kav_score == "-":
                    kav_datas += [[key, "-", "-"]]
                else:
                    kav_datas += [[key, kav_score, rounds_data[key][2][-2] - kav_score]]
                if net_score == "-":
                    net_datas += [[key, "-", "-"]]
                else:
                    net_datas += [[key, net_score, rounds_data[key][3][-2] - net_score]]
                if mah_score == "-":
                    mah_datas += [[key, "-", "-"]]
                else:
                    mah_datas += [[key, mah_score, rounds_data[key][4][-2] - mah_score]]

            header = rounds_data[list(rounds_data.keys())[0]][0]
            pars = rounds_data[list(rounds_data.keys())[0]][1]

            kav_valid = False
            for plays in kav_datas:
                if plays[-1] != "-":
                    kav_valid = True

            net_valid = False
            for plays in net_datas:
                if plays[-1] != "-":
                    net_valid = True

            mah_valid = False
            for plays in mah_datas:
                if plays[-1] != "-":
                    mah_valid = True

            if kav_valid:
                max_kav_total = 0
                for plays in kav_datas:
                    if plays[-1] != "-":
                        max_kav_total = max(max_kav_total, plays[-1])
                valid_kav_scores = []
                for plays in kav_datas:
                    if plays[-1] == max_kav_total:
                        valid_kav_scores += [plays[-2]]
                best_kav = float("inf")
                kav_key = ""
                for valid_score in valid_kav_scores:
                    best_kav = min(best_kav, valid_score)
                for plays in kav_datas:
                    if plays[-2] == best_kav:
                        kav_key = plays[0]
            else:
                kav_key = list(rounds_data.keys())[0]

            if net_valid:
                max_net_total = 0
                for plays in net_datas:
                    if plays[-1] != "-":
                        max_net_total = max(max_net_total, plays[-1])
                valid_net_scores = []
                for plays in net_datas:
                    if plays[-1] == max_net_total:
                        valid_net_scores += [plays[-2]]
                best_net = float("inf")
                net_key = ""
                for valid_score in valid_net_scores:
                    best_net = min(best_net, valid_score)
                for plays in net_datas:
                    if plays[-2] == best_net:
                        net_key = plays[0]
            else:
                net_key = list(rounds_data.keys())[0]

            if mah_valid:
                max_mah_total = 0
                for plays in mah_datas:
                    if plays[-1] != "-":
                        max_mah_total = max(max_mah_total, plays[-1])
                valid_mah_scores = []
                for plays in mah_datas:
                    if plays[-1] == max_mah_total:
                        valid_mah_scores += [plays[-2]]
                best_mah = float("inf")
                mah_key = ""
                for valid_score in valid_mah_scores:
                    best_mah = min(best_mah, valid_score)
                for plays in mah_datas:
                    if plays[-2] == best_mah:
                        mah_key = plays[0]
            else:
                mah_key = list(rounds_data.keys())[0]

            # Display personal bests as NiceGUI table
            with container:
                ui.label("Personal Bests")

            columns = []
            rows = [{},{},{},{}]
            for index,item in enumerate(header):
                columns += [{"name":item, "label":item, "field":item, "align": "center"}]
                rows[0][item] = pars[index]
                rows[1][item] = rounds_data[kav_key][2][index]
                rows[2][item] = rounds_data[net_key][3][index]
                rows[3][item] = rounds_data[mah_key][4][index]
                
            with container:
                ui.table(columns=columns, rows=rows)
                ui.label("")

        else:
            None

    except:
        None

    # Display previous rounds as NiceGUI table
    with container:
        ui.label("Previous Rounds")
    for key in rounds_data.keys():
        kav_score = rounds_data[key][2][-1]
        net_score = rounds_data[key][3][-1]
        mah_score = rounds_data[key][4][-1]

        winners = []
        valid_scores = []

        if kav_score != "-":
            valid_scores.append(("Kav", kav_score))
        if net_score != "-":
            valid_scores.append(("Nethidu", net_score))
        if mah_score != "-":
            valid_scores.append(("Mahith", mah_score))

        if len(valid_scores) == 1:
            winner = "-"
        else:
            if valid_scores:
                min_score = min(score for name, score in valid_scores)

                for name, score in valid_scores:
                    if score == min_score:
                        winners.append(name)

            winner = " and ".join(winners)

        if not (Course == "All" or Layout == "All"):
            head_ting = [["Winner", winner]]
        elif Layout == "All":
            head_ting = [["Layout", rounds[key][0][2]], ["Winner", winner]]
        else:
            head_ting = [["Course", rounds[key][0][1]], ["Layout", rounds[key][0][2]], ["Winner", winner]]

 
        # Call the function to display the table
        with container:
            ui.label(key)
            for ting in head_ting:
                ui.label(ting[0] + ": " + ting[1])

        round_data = rounds_data[key]
        columns = []
        rows = [{},{},{},{}]
        for index,item in enumerate(round_data[0]):
            columns += [{"name":item, "label":item, "field":item, "align": "center"}]
            rows[0][item] = round_data[1][index]
            rows[1][item] = round_data[2][index]
            rows[2][item] = round_data[3][index]
            rows[3][item] = round_data[4][index]
                
        with container:
            ui.table(columns=columns, rows=rows)
            ui.label("")

        

def course_dropdown():
    global Course
    dropdown = ui.select(options=["All"] + courses, value="All", label="Course", on_change=lambda e: update_values(e.value)).classes('min-w-40')
    return dropdown

# Dropdown for selecting layout
def layout_dropdown():
    global Layout
    # Initialize with "-" as the only option, since the layout options will depend on the course selected
    dropdown = ui.select(options=["-"],value="-", label="Layout", on_change=lambda e: update_selected_value(e)).classes('min-w-40')
    return dropdown

# Display the dropdowns
course_select = course_dropdown()
values_select = layout_dropdown()

container = ui.column()

update_values(course_select.value)
update_selected_value(values_select)

ui.run()
