import streamlit as st
import pandas as pd
from datetime import date, timedelta

# =========================================================
# PAGE SETTINGS
# =========================================================

st.set_page_config(
    page_title="AI Study Planner",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background: linear-gradient(
        135deg,
        #fffaff 0%,
        #f4f8ff 55%,
        #f8edff 100%
    );
}

[data-testid="stSidebar"] {
    background: linear-gradient(
        180deg,
        #112d58 0%,
        #091b38 100%
    );
}

[data-testid="stSidebar"] * {
    color: white;
}

.main-title {
    font-size: 42px;
    font-weight: 800;
    color: #18366f;
}

.subtitle {
    color: #63779e;
    font-size: 17px;
    margin-bottom: 25px;
}

.card {
    background: white;
    border: 1px solid #e1e8f5;
    border-radius: 20px;
    padding: 20px;
    text-align: center;
    box-shadow: 0 8px 25px rgba(40,70,120,0.08);
    min-height: 180px;
}

.card-icon {
    font-size: 38px;
}

.card-title {
    color: #173873;
    font-size: 17px;
    font-weight: 800;
    margin-top: 10px;
}

.card-text {
    color: #687b9e;
    font-size: 14px;
    line-height: 1.5;
    margin-top: 8px;
}

.welcome {
    background: white;
    border: 1px solid #e1e8f5;
    border-radius: 24px;
    padding: 30px;
    box-shadow: 0 8px 25px rgba(40,70,120,0.08);
}

.quote {
    background: #fff1fb;
    border: 1px solid #efd9f0;
    border-radius: 24px;
    padding: 30px;
    text-align: center;
    min-height: 200px;
}

.step {
    background: white;
    border: 1px solid #e1e8f5;
    border-radius: 18px;
    padding: 18px 10px;
    text-align: center;
    min-height: 185px;
    box-shadow: 0 6px 18px rgba(40,70,120,0.06);
}

.section-title {
    color: #18366f;
    font-size: 28px;
    font-weight: 800;
    margin-top: 30px;
    margin-bottom: 15px;
}

.stButton > button {
    border-radius: 12px;
    font-weight: 700;
    min-height: 45px;
}

/* =========================================================
   ONLY CHANGE: FIX MAIN PAGE TEXT VISIBILITY
   ========================================================= */

[data-testid="stMetric"] {
    color: #173873 !important;
}

[data-testid="stMetricLabel"] {
    color: #63779e !important;
}

[data-testid="stMetricValue"] {
    color: #173873 !important;
}

.stTabs [data-baseweb="tab"] {
    color: #173873 !important;
}

.stTabs [data-baseweb="tab"] div {
    color: #173873 !important;
}

[data-testid="stMarkdownContainer"] h3 {
    color: #173873 !important;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE
# =========================================================

if "plan" not in st.session_state:
    st.session_state.plan = None

if "count" not in st.session_state:
    st.session_state.count = 0


# =========================================================
# FUNCTIONS
# =========================================================

def get_items(text):
    if not text:
        return []

    result = []

    text = text.replace("\n", ",")

    for item in text.split(","):
        item = item.strip()

        if item and item not in result:
            result.append(item)

    return result


def make_tasks(subject):
    return [
        f"{subject} - Concept Review",
        f"{subject} - Important Topics",
        f"{subject} - Practice Questions",
        f"{subject} - Revision"
    ]


def priority_score(subject, priority_topics, weak_subjects):

    score = 1

    subject_lower = subject.lower()

    for topic in priority_topics:

        if (
            topic.lower() in subject_lower
            or subject_lower in topic.lower()
        ):
            score += 3

    for weak in weak_subjects:

        if (
            weak.lower() in subject_lower
            or subject_lower in weak.lower()
        ):
            score += 2

    return score


def generate_plan(
    start_date,
    exam_date,
    hours_per_day,
    subjects,
    priority_topics,
    weak_subjects,
    strategy,
    study_days,
    revision,
    mock_test
):

    if not subjects:
        return pd.DataFrame()

    # Arrange subjects according to strategy

    if strategy == "Priority First":

        subjects = sorted(
            subjects,
            key=lambda x: priority_score(
                x,
                priority_topics,
                weak_subjects
            ),
            reverse=True
        )

    elif strategy == "Easy First":

        subjects = sorted(
            subjects,
            key=lambda x: priority_score(
                x,
                priority_topics,
                weak_subjects
            )
        )

    all_tasks = []

    for subject in subjects:
        all_tasks.extend(make_tasks(subject))

    rows = []

    task_index = 0

    current_date = start_date

    last_date = exam_date - timedelta(days=1)

    while current_date <= last_date:

        day_name = current_date.strftime("%A")

        if day_name in study_days:

            remaining_hours = float(hours_per_day)

            # Revision uses available time
            revision_hours = 0.5 if revision and remaining_hours >= 1 else 0

            # Mini mock test on Sunday
            mock_hours = 0

            if (
                mock_test
                and day_name == "Sunday"
                and remaining_hours - revision_hours >= 1
            ):
                mock_hours = 1

            study_hours = (
                remaining_hours
                - revision_hours
                - mock_hours
            )

            if study_hours > 0 and all_tasks:

                task = all_tasks[
                    task_index % len(all_tasks)
                ]

                task_index += 1

                rows.append({
                    "Date": current_date,
                    "Day": day_name,
                    "Task": task,
                    "Hours": round(study_hours, 1),
                    "Type": "Study"
                })

            if revision_hours > 0:

                rows.append({
                    "Date": current_date,
                    "Day": day_name,
                    "Task": "Daily Revision",
                    "Hours": revision_hours,
                    "Type": "Revision"
                })

            if mock_hours > 0:

                rows.append({
                    "Date": current_date,
                    "Day": day_name,
                    "Task": "Mini Mock Test",
                    "Hours": mock_hours,
                    "Type": "Mock Test"
                })

        current_date += timedelta(days=1)

    return pd.DataFrame(rows)


def evaluate_plan(plan, hours_per_day, priority_topics):

    if plan.empty:
        return 0, "No plan generated."

    daily_hours = plan.groupby("Date")["Hours"].sum()

    time_ok = bool(
        (daily_hours <= hours_per_day + 0.01).all()
    )

    priority_ok = True

    if priority_topics:

        all_text = " ".join(
            plan["Task"].astype(str)
        ).lower()

        priority_ok = any(
            topic.lower() in all_text
            for topic in priority_topics
        )

    score = 100 if time_ok and priority_ok else 50

    if score == 100:

        return score, (
            "All time and priority constraints "
            "are satisfied."
        )

    return score, (
        "Some constraints need improvement."
    )


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    # IMPORTANT:
    # HTML is rendered using st.html().
    # It will NOT appear as text/code.

    st.html("""
    <div style="
        font-size:25px;
        font-weight:800;
        color:white;
        margin-bottom:5px;
    ">
        📚 AI Study Planner 
    </div>

    <div style="
        color:#73D7FF;
        font-size:15px;
        margin-bottom:20px;
    ">
        Plan • Learn • Achieve
    </div>
    """)

    st.markdown("---")

    st.markdown("### 📌 Study Constraints")

    start_date = st.date_input(
        "Start Date",
        value=date.today()
    )

    exam_date = st.date_input(
        "Exam Date",
        value=date.today() + timedelta(days=14)
    )

    hours_per_day = st.number_input(
        "Available Study Hours Per Day",
        min_value=1.0,
        max_value=12.0,
        value=4.0,
        step=0.5
    )

    subjects_text = st.text_area(
        "Subjects",
        value="Python, Database, AI, Blockchain"
    )

    priority_text = st.text_area(
        "Priority Topics",
        value="AI, Python"
    )

    st.markdown("### ⚙️ Advanced Features")

    weak_text = st.text_area(
        "Difficult / Weak Subjects",
        value="Database"
    )

    strategy = st.selectbox(
        "Planning Strategy",
        [
            "Priority First",
            "Balanced",
            "Easy First"
        ]
    )

    st.markdown("### 📅 Study Days")

    study_days = []

    day_list = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday"
    ]

    default_days = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday"
    ]

    for day in day_list:

        selected = st.checkbox(
            day,
            value=day in default_days
        )

        if selected:
            study_days.append(day)

    revision = st.checkbox(
        "Add Revision Sessions",
        value=True
    )

    mock_test = st.checkbox(
        "Add Mini Mock Tests",
        value=True
    )

    # =====================================================
    # IMPORTANT BUTTON
    # =====================================================

    generate = st.button(
        "🚀 Generate Study Plan",
        use_container_width=True
    )


# =========================================================
# MAIN HEADER
# =========================================================

st.markdown(
    '<div class="main-title">'
    '📚 AI Study Planner'
    '</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Smart Study Planning • Priority Management • '
    'Task Decomposition • Analytics • Progress Tracking'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# FEATURE CARDS
# =========================================================

features = [
    (
        "📝",
        "Task Decomposition",
        "Divide subjects into smaller tasks"
    ),
    (
        "🧩",
        "Priority Handling",
        "Give extra time to priority topics"
    ),
    (
        "👥",
        "Difficulty Analysis",
        "Consider difficult subjects"
    ),
    (
        "🗓️",
        "Schedule Generation",
        "Create timetable within time limits"
    ),
    (
        "✅",
        "Evaluation",
        "Check time and priority constraints"
    )
]

columns = st.columns(5)

for column, feature in zip(columns, features):

    icon, title, description = feature

    with column:

        st.html(f"""
        <div class="card">

            <div class="card-icon">
                {icon}
            </div>

            <div class="card-title">
                {title}
            </div>

            <div class="card-text">
                {description}
            </div>

        </div>
        """)


# =========================================================
# WELCOME
# =========================================================

st.write("")

left, right = st.columns([1.6, 1])

with left:

    st.html("""
    <div class="welcome">

        <h2 style="color:#18366f;">
            👋 Welcome to your Smart Study Planner
        </h2>

        <p style="
            color:#63779e;
            font-size:16px;
            line-height:1.7;
        ">
            Fill in the details from the sidebar and click
            <b>Generate Study Plan</b> to create your
            personalized study schedule.
        </p>

        <div style="
            background:#eef8ff;
            border:1px solid #d2eaff;
            border-radius:15px;
            padding:15px;
            color:#1769aa;
            font-weight:800;
        ">
            💡 Your goals + Smart planning = Success
        </div>

    </div>
    """)

with right:

    st.html("""
    <div class="quote">

        <div style="font-size:42px;">
            🌱
        </div>

        <h3 style="color:#5a2d91;">
            “Small progress every day leads
            to big results.”
        </h3>

        <p style="color:#687694;">
            Keep going! 💪
        </p>

    </div>
    """)


# =========================================================
# HOW IT WORKS
# =========================================================

st.markdown(
    '<div class="section-title">'
    '✨ How It Works?'
    '</div>',
    unsafe_allow_html=True
)

steps = [
    (
        "📄",
        "1. Input Constraints",
        "Subjects, hours, exam date and priority topics"
    ),
    (
        "🧩",
        "2. Task Decomposition",
        "Divide subjects into smaller tasks"
    ),
    (
        "👥",
        "3. Priority Handling",
        "Give extra attention to priority topics"
    ),
    (
        "🗓️",
        "4. Schedule Generation",
        "Create timetable within time limits"
    ),
    (
        "✅",
        "5. Evaluation",
        "Check time and priority constraints"
    ),
    (
        "🔄",
        "6. Regeneration",
        "Update inputs and create a new plan"
    )
]

columns = st.columns(6)

for column, step in zip(columns, steps):

    icon, title, description = step

    with column:

        st.html(f"""
        <div class="step">

            <div style="font-size:38px;">
                {icon}
            </div>

            <div style="
                color:#173873;
                font-weight:800;
                font-size:16px;
            ">
                {title}
            </div>

            <div style="
                color:#667b9e;
                font-size:14px;
                margin-top:10px;
                line-height:1.5;
            ">
                {description}
            </div>

        </div>
        """)


# =========================================================
# GENERATE BUTTON ACTION
# =========================================================

# VERY IMPORTANT:
#
# The button above is:
#
# generate = st.button(...)
#
# Therefore we use:
#
# if generate:
#
# NOT:
# if generate_clicked:
#
# NOT:
# if generate_button:

if generate:

    subjects = get_items(subjects_text)

    priority_topics = get_items(
        priority_text
    )

    weak_subjects = get_items(
        weak_text
    )

    if not subjects:

        st.error(
            "Please enter at least one subject."
        )

    elif exam_date <= start_date:

        st.error(
            "Exam Date must be after Start Date."
        )

    elif not study_days:

        st.error(
            "Please select at least one Study Day."
        )

    else:

        with st.spinner(
            "Creating your smart study plan..."
        ):

            plan = generate_plan(
                start_date,
                exam_date,
                hours_per_day,
                subjects,
                priority_topics,
                weak_subjects,
                strategy,
                study_days,
                revision,
                mock_test
            )

            st.session_state.plan = plan

            st.session_state.count += 1

        st.success(
            "🎉 Study Plan Generated Successfully!"
        )


# =========================================================
# DISPLAY PLAN
# =========================================================

if st.session_state.plan is not None:

    plan = st.session_state.plan

    st.markdown(
        '<div class="section-title">'
        '📊 Your Study Dashboard'
        '</div>',
        unsafe_allow_html=True
    )

    total_hours = (
        plan["Hours"].sum()
        if not plan.empty
        else 0
    )

    number_of_days = (
        plan["Date"].nunique()
        if not plan.empty
        else 0
    )

    number_of_tasks = len(plan)

    score, message = evaluate_plan(
        plan,
        hours_per_day,
        get_items(priority_text)
    )

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "📚 Total Hours",
        f"{total_hours:.1f}"
    )

    col2.metric(
        "📅 Study Days",
        number_of_days
    )

    col3.metric(
        "📝 Tasks",
        number_of_tasks
    )

    col4.metric(
        "🎯 Score",
        f"{score}%"
    )

    if score == 100:

        st.success(
            "✅ " + message
        )

    else:

        st.warning(
            "⚠️ " + message
        )

    # =====================================================
    # TABS
    # =====================================================

    tab1, tab2, tab3, tab4 = st.tabs(
        [
            "📅 Study Schedule",
            "🧩 Task Decomposition",
            "📈 Analytics",
            "🔄 Refinement"
        ]
    )

    # =====================================================
    # TAB 1
    # =====================================================

    with tab1:

        st.subheader(
            "📅 Your Personalized Study Schedule"
        )

        if plan.empty:

            st.info(
                "No schedule was generated."
            )

        else:

            display_plan = plan.copy()

            display_plan["Date"] = (
                display_plan["Date"]
                .astype(str)
            )

            st.dataframe(
                display_plan,
                use_container_width=True,
                hide_index=True
            )

            csv = display_plan.to_csv(
                index=False
            ).encode("utf-8")

            st.download_button(
                "⬇️ Download Study Plan",
                csv,
                "AI_Study_Plan.csv",
                "text/csv"
            )

    # =====================================================
    # TAB 2
    # =====================================================

    with tab2:

        st.subheader(
            "🧩 Task Decomposition"
        )

        decomposition = []

        for subject in get_items(
            subjects_text
        ):

            tasks = make_tasks(subject)

            for task in tasks:

                decomposition.append({
                    "Subject": subject,
                    "Sub Task": task.split(
                        " - ",
                        1
                    )[1],
                    "Priority Score": priority_score(
                        subject,
                        get_items(
                            priority_text
                        ),
                        get_items(
                            weak_text
                        )
                    )
                })

        decomposition_df = pd.DataFrame(
            decomposition
        )

        st.dataframe(
            decomposition_df,
            use_container_width=True,
            hide_index=True
        )

    # =====================================================
    # TAB 3
    # =====================================================

    with tab3:

        st.subheader(
            "📈 Study Analytics"
        )

        if not plan.empty:

            task_hours = (
                plan.groupby("Task")["Hours"]
                .sum()
                .sort_values(
                    ascending=False
                )
            )

            st.bar_chart(task_hours)

            daily_hours = (
                plan.groupby("Date")["Hours"]
                .sum()
            )

            st.subheader(
                "Daily Study Hours"
            )

            st.line_chart(
                daily_hours
            )

    # =====================================================
    # TAB 4
    # =====================================================

    with tab4:

        st.subheader(
            "🔄 Iterative Refinement"
        )

        st.write(
            "Change any input in the sidebar "
            "and click Generate Study Plan again."
        )

        st.info(
            "The planner will create a new plan "
            "using the updated constraints."
        )

        st.write(
            f"Plans generated in this session: "
            f"**{st.session_state.count}**"
        )


# =========================================================
# FOOTER
# =========================================================

st.markdown("""
<div style="
    text-align:center;
    color:#7a8bab;
    padding:30px;
    font-size:14px;
">
    📚 AI Study Planner  •
    Plan Smart • Learn Better • Achieve More
</div>
""", unsafe_allow_html=True)