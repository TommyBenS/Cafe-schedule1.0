import streamlit as st
import itertools
import pandas as pd

# Check that no employee works more than one shift a day.
def is_valid_schedule(schedule):
    daily_assignments = {}
    for shift, employees in schedule.items():
        day = shift.split()[0]  # e.g., "Sun", "Mon", etc.
        daily_assignments.setdefault(day, []).extend(employees)
    for day, assigned in daily_assignments.items():
        if len(assigned) != len(set(assigned)):
            return False
    return True

# Generate up to max_options valid schedules.
def generate_possible_schedules(shifts, shift_requirements, availability, max_options=5):
    shift_candidates = {}
    for shift in shifts:
        required = shift_requirements[shift]
        available_emps = [emp for emp, avail in availability.items() if shift in avail]
        if len(available_emps) < required:
            shift_candidates[shift] = []
        else:
            shift_candidates[shift] = list(itertools.combinations(available_emps, required))
    for shift, candidates in shift_candidates.items():
        if not candidates:
            st.write(f"No available employees for shift: {shift}")
            return []
    valid_schedules = []
    candidate_lists = [shift_candidates[s] for s in shifts]
    for assignment in itertools.product(*candidate_lists):
        schedule = dict(zip(shifts, assignment))
        if is_valid_schedule(schedule):
            valid_schedules.append(schedule)
            if len(valid_schedules) >= max_options:
                break
    return valid_schedules

# --- App Interface ---
st.title("Weekly Schedule Dashboard")

# Define the shifts and their employee requirements.
shifts = [
    "Sun Morning", "Sun Evening",
    "Mon Morning", "Mon Evening",
    "Tue Morning", "Tue Evening",
    "Wed Morning", "Wed Evening",
    "Thu Morning", "Thu Evening",
    "Fri Morning",  # Only one shift on Friday
    "Sat Morning", "Sat Evening"
]
shift_requirements = {
    "Sun Morning": 2,
    "Sun Evening": 2,
    "Mon Morning": 2,
    "Mon Evening": 2,
    "Tue Morning": 2,
    "Tue Evening": 2,
    "Wed Morning": 2,
    "Wed Evening": 2,
    "Thu Morning": 2,
    "Thu Evening": 2,
    "Fri Morning": 4,
    "Sat Morning": 4,
    "Sat Evening": 3
}
shift_times = {
    "Sun Morning": ("09:30", "16:30"),
    "Sun Evening": ("15:30", "22:30"),
    "Mon Morning": ("09:30", "16:30"),
    "Mon Evening": ("15:30", "22:30"),
    "Tue Morning": ("09:30", "16:30"),
    "Tue Evening": ("15:30", "22:30"),
    "Wed Morning": ("09:30", "16:30"),
    "Wed Evening": ("15:30", "22:30"),
    "Thu Morning": ("09:30", "16:30"),
    "Thu Evening": ("15:30", "22:30"),
    "Fri Morning": ("09:30", "15:30"),
    "Sat Morning": ("09:30", "16:30"),
    "Sat Evening": ("15:30", "22:30")
}

# Define employee availability.
availability = {
    "Alice":   ["Sun Morning", "Mon Morning", "Tue Morning", "Wed Morning", "Thu Morning", "Fri Morning", "Sat Morning"],
    "Bob":     ["Sun Evening", "Mon Evening", "Tue Evening", "Wed Evening", "Thu Evening", "Sat Evening"],
    "Charlie": ["Sun Morning", "Sun Evening", "Mon Morning", "Mon Evening", "Tue Morning", "Tue Evening",
                "Wed Morning", "Wed Evening", "Thu Morning", "Thu Evening", "Fri Morning", "Sat Morning", "Sat Evening"],
    "David":   ["Sun Morning", "Mon Morning", "Tue Morning", "Wed Morning", "Thu Morning", "Fri Morning", "Sat Morning"],
    "Eva":     ["Sun Evening", "Mon Evening", "Tue Evening", "Wed Evening", "Thu Evening", "Sat Evening"],
    "Frank":   ["Sun Morning", "Mon Morning", "Tue Morning", "Wed Morning", "Thu Morning", "Fri Morning", "Sat Morning"],
    "Grace":   ["Sun Evening", "Mon Evening", "Tue Evening", "Wed Evening", "Thu Evening", "Sat Evening"],
}

# Generate up to 5 schedule options.
schedules = generate_possible_schedules(shifts, shift_requirements, availability, max_options=5)

if not schedules:
    st.write("No valid schedules could be generated. Please check employee availability or shift requirements.")
else:
    option_labels = [f"Option {i+1}" for i in range(len(schedules))]
    selected_option = st.sidebar.selectbox("Select Schedule Option", options=option_labels)
    selected_schedule = schedules[option_labels.index(selected_option)]
    
    st.subheader(f"Schedule {selected_option}")
    
    # Prepare a table where days are columns and shift types are rows.
    days = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"]
    shift_types = ["Morning", "Evening"]
    data = {}
    for day in days:
        day_data = {}
        for shift_type in shift_types:
            shift_name = f"{day} {shift_type}"
            if shift_name in selected_schedule:
                start, end = shift_times[shift_name]
                employees = ", ".join(selected_schedule[shift_name])
                day_data[shift_type] = f"{start} - {end}\n{employees}"
            else:
                day_data[shift_type] = "N/A"
        data[day] = day_data
    
    # Create a DataFrame to display the schedule.
    df = pd.DataFrame(data, index=shift_types)
    st.table(df)
