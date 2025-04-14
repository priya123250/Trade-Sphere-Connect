import streamlit as st
import pandas as pd
import os
import plotly.express as px
from datetime import datetime

def calculate_decision(rating, needed, interaction, history_years, recommendation=""):
    score = 0
    score += rating * 8
    score += 30 if needed == "Yes" else 0

    if interaction == "Existing Supplier":
        score += 15
    elif interaction == "New Supplier":
        if history_years >= 2:
            score += 10
        elif recommendation:
            score += 5

    if score >= 70:
        return "Approve", score
    elif score >= 50:
        return "Approve with Conditions", score
    else:
        return "Reject", score

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = True
        st.session_state.username = "Admin"

    st.set_page_config(page_title="TradeSphere Connect", layout="wide", page_icon="🌐")
    st.title("🌐 TradeSphere Connect - Supplier Evaluation Tool")

    st.sidebar.header("Navigation")
    st.sidebar.markdown(f"👤 Logged in as: `{st.session_state.username}`")
    st.sidebar.info("🔓 Auto-login enabled for demo mode")
    section = st.sidebar.radio("Go to:", ["🏠 Dashboard", "📋 Applications", "📄 Review Application", "📊 Analytics"])

    CSV_FILE = "supplier_data2.csv"
    columns = [
        "Supplier Name", "Country", "Rating", "Decision", "Score", "Comments",
        "Supplier Offers", "Currently Needed", "Company Needs", "Past Interaction",
        "Trading History", "Recommendation", "Reviewed By", "Submission Time"
    ]

    if not os.path.exists(CSV_FILE):
        demo_data = pd.DataFrame([
            {
                "Supplier Name": "Global Tex Co.",
                "Country": "India",
                "Rating": 4.5,
                "Decision": "Approve",
                "Score": 82,
                "Comments": "Strong supplier history and good communication.",
                "Supplier Offers": "Textiles",
                "Currently Needed": "Yes",
                "Company Needs": "",
                "Past Interaction": "Existing Supplier",
                "Trading History": "3",
                "Recommendation": "",
                "Reviewed By": "Admin",
                "Submission Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "Supplier Name": "FreshMart Ltd.",
                "Country": "Germany",
                "Rating": 2.0,
                "Decision": "Reject",
                "Score": 35,
                "Comments": "Not offering what we currently need.",
                "Supplier Offers": "Fresh Produce",
                "Currently Needed": "No",
                "Company Needs": "Electronics, Machinery",
                "Past Interaction": "New Supplier",
                "Trading History": "0",
                "Recommendation": "Has recommendation from TechMart",
                "Reviewed By": "Admin",
                "Submission Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "Supplier Name": "IronForge Pvt.",
                "Country": "China",
                "Rating": 3.8,
                "Decision": "Approve with Conditions",
                "Score": 63,
                "Comments": "Has potential but needs to improve logistics.",
                "Supplier Offers": "Machinery",
                "Currently Needed": "Yes",
                "Company Needs": "",
                "Past Interaction": "New Supplier",
                "Trading History": "1",
                "Recommendation": "Referred by SteelWorks",
                "Reviewed By": "Admin",
                "Submission Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            },
            {
                "Supplier Name": "GreenCrop Traders",
                "Country": "USA",
                "Rating": 4.2,
                "Decision": "Approve",
                "Score": 77,
                "Comments": "Meets all sourcing needs and compliance.",
                "Supplier Offers": "Food Products",
                "Currently Needed": "Yes",
                "Company Needs": "",
                "Past Interaction": "Existing Supplier",
                "Trading History": "4",
                "Recommendation": "",
                "Reviewed By": "Admin",
                "Submission Time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        ])
        demo_data.to_csv(CSV_FILE, index=False)

    df = pd.read_csv(CSV_FILE) if os.path.exists(CSV_FILE) else pd.DataFrame(columns=columns)

    if section == "🏠 Dashboard":
        st.subheader("🏠 Supplier Evaluation Dashboard")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Applications", len(df))
        col2.metric("Approval Rate",
                    f"{round(len(df[df['Decision'] == 'Approve']) / len(df) * 100, 1)}%" if len(df) > 0 else "0%")
        col3.metric("Avg. Rating",
                    f"{round(df['Rating'].mean(), 1)} ⭐" if len(df) > 0 else "N/A")
        col4.metric("Pending Reviews",
                    len(df[df['Decision'] == 'Pending']) if 'Pending' in df['Decision'].unique() else 0)

        st.markdown("---")
        st.subheader("Recent Applications")
        if not df.empty:
            st.dataframe(df.sort_values("Submission Time", ascending=False).head(5))
        else:
            st.info("No applications submitted yet.")

    elif section == "📋 Applications":
        st.subheader("📋 Supplier Applications")
        col1, col2, col3 = st.columns(3)
        with col1:
            country_filter = st.multiselect("Filter by Country", df['Country'].unique())
        with col2:
            decision_filter = st.multiselect("Filter by Decision", df['Decision'].unique())
        with col3:
            rating_filter = st.slider("Filter by Minimum Rating", 1.0, 5.0, 1.0)

        filtered_df = df.copy()
        if country_filter:
            filtered_df = filtered_df[filtered_df['Country'].isin(country_filter)]
        if decision_filter:
            filtered_df = filtered_df[filtered_df['Decision'].isin(decision_filter)]
        filtered_df = filtered_df[filtered_df['Rating'] >= rating_filter]

        if not filtered_df.empty:
            for _, row in filtered_df.iterrows():
                with st.expander(f"{row['Supplier Name']} ({row['Country']}) - {row['Decision']}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"**Rating:** {row['Rating']} ⭐")
                        st.markdown(f"**Offers:** {row['Supplier Offers']}")
                        st.markdown(f"**Needed:** {row['Currently Needed']}")
                    with col2:
                        st.markdown(f"**Score:** {row['Score']}/100")
                        st.markdown(f"**Reviewed By:** {row['Reviewed By']}")
                        st.markdown(f"**Submitted:** {row['Submission Time']}")
                    st.markdown("**Comments:**")
                    st.info(row['Comments'])
        else:
            st.info("No applications match the selected filters.")

    elif section == "📄 Review Application":
        st.subheader("📄 Supplier Application Review")
        with st.form("review_form", clear_on_submit=True):
            st.markdown("### Supplier Information")
            name = st.text_input("Supplier Name*", help="Required field")
            country = st.selectbox("Country*", ["", "India", "USA", "Germany", "China", "UK", "Japan", "Other"])

            st.markdown("### Evaluation Criteria")
            rating = st.slider("Supplier Rating (1-5)*", 1.0, 5.0, 3.0, 0.5)
            offer = st.selectbox("What does the supplier offer?*",
                                 ["", "Textiles", "Electronics", "Machinery",
                                  "Raw Materials", "Chemicals", "Food Products", "Other"])
            needed = st.radio("Is this product currently needed by our company?*", ["Yes", "No"])
            company_needs = st.text_input("What does the company need instead?") if needed == "No" else ""
            interaction = st.radio("Past interaction with this supplier?*", ["New Supplier", "Existing Supplier"])
            history = "0"
            recommendation = ""
            if interaction == "New Supplier":
                has_history = st.radio("Does the supplier have verifiable trading history?", ["Yes", "No", "Don't Know"])
                if has_history == "Yes":
                    history = st.text_input("Years of verifiable history with other companies", value="0")
                recommendation = st.text_input("Recommendations or references (if any)")
            else:
                history = st.text_input("Years of trading history with our company*", value="0")

            if st.form_submit_button("Calculate Preliminary Decision"):
                if not name or not country or not offer:
                    st.error("Please fill in all required fields (marked with *)")
                else:
                    try:
                        history_years = float(history) if history else 0
                        decision, score = calculate_decision(
                            rating, needed, interaction, history_years, recommendation
                        )
                        st.session_state.prelim_decision = decision
                        st.session_state.prelim_score = score
                        st.success(f"Preliminary Decision: {decision} (Score: {score}/100)")
                    except ValueError:
                        st.error("Please enter valid numbers for years of history")

            comments = st.text_area("Additional Comments")

            if 'prelim_decision' in st.session_state:
                st.markdown(f"### Final Decision: {st.session_state.prelim_decision}")
                final_decision = st.radio("Confirm or override decision:",
                                          [st.session_state.prelim_decision,
                                           "Approve" if st.session_state.prelim_decision != "Approve" else "Approve with Conditions",
                                           "Reject"])
                submitted = st.form_submit_button("Submit Final Decision")
                if submitted:
                    if not name or not country or not offer:
                        st.error("Please fill in all required fields (marked with *)")
                    else:
                        new_row = pd.DataFrame([[name, country, rating, final_decision, st.session_state.prelim_score,
                                                 comments, offer, needed, company_needs, interaction,
                                                 history, recommendation, st.session_state.username,
                                                 datetime.now().strftime("%Y-%m-%d %H:%M:%S")]],
                                               columns=columns)

                        if os.path.exists(CSV_FILE):
                            new_row.to_csv(CSV_FILE, mode='a', header=False, index=False)
                        else:
                            new_row.to_csv(CSV_FILE, index=False)

                        st.success(f"✅ Decision submitted for {name}!")
                        del st.session_state.prelim_decision
                        del st.session_state.prelim_score

    elif section == "📊 Analytics":
        st.subheader("📊 Supplier Evaluation Analytics")
        if not df.empty:
            st.markdown("### Approval Metrics")
            col1, col2 = st.columns(2)
            with col1:
                fig = px.pie(df, names='Decision', title='Decision Distribution')
                st.plotly_chart(fig, use_container_width=True)
            with col2:
                fig = px.histogram(df, x='Rating', nbins=10, title='Rating Distribution')
                st.plotly_chart(fig, use_container_width=True)

            st.markdown("### Geographic Analysis")
            country_df = df.groupby('Country').agg({
                'Supplier Name': 'count',
                'Rating': 'mean',
                'Score': 'mean'
            }).reset_index()
            country_df.columns = ['Country', 'Applications', 'Avg Rating', 'Avg Score']
            st.dataframe(country_df.sort_values('Applications', ascending=False))

            st.markdown("### Decision Score Analysis")
            fig = px.box(df, x='Decision', y='Score', points="all", title='Score Distribution by Decision')
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available yet. Submit applications to view analytics.")

if __name__ == "__main__":
    main()
