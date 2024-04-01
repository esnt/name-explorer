import pandas as pd
import streamlit as st
import numpy as np
import plotly.express as px
import seaborn as sns
import matplotlib.pyplot as plt
import re


df = pd.read_csv('names.csv.zip')

max_count = df['n'].max()
max_prop = df['proportion'].max()

groups = df.groupby(['year', 'sex'])
most_popular_names = groups.apply(lambda x: x.loc[x['n'].idxmax()])
most_popular_names.reset_index(drop=True, inplace=True)



n_years = df['year'].nunique()

unique_names = set(df['name'])
st.title('Name Explorer')

st.markdown("""
The purpose of this app is to help answer the question “How does name popularity change over time?”  The user is able to enter a name to explore in the search below.  Regular expressions can also be used in the search to check for alternative spellings.  For example, the regular expression “All?[iy]son”  will include names “Alison”, “Allison”, “Allyson”, or “Alyson”.  (Obviously there is some user knowledge required in order to know what alternative spellings are of interest.). Other features of the app include: 
* Aggregated or separate plotting lines (when multiple names are returned in a regular expression)
* Plotting by proportion (within a year and sex) or raw count
* Local or global y-axis scaling
* Name facts and counts
* Separate tabs for males and females 
""")

pattern = st.text_input('Enter a name to search', 'John')
regex = st.checkbox('Check if your name search is a regular expression')

if regex:
    keep = {name for name in unique_names if re.match(pattern, name)}
    header_word = 'regular expression'
else:
    keep = {pattern}
    header_word = 'name'

name_df = df[df['name'].isin(keep)]
f_df = name_df[name_df['sex']=='F']
total_females = f_df['n'].sum()
m_df = name_df[name_df['sex']=='M']
total_males = m_df['n'].sum()

with st.expander("Open to see plotting options and search results (for regular expression)"):
    col1, col2 = st.columns(2)
    with col2:
        st.markdown("**Names matching regular expression**")
        st.write(', '.join(keep))

        st.divider()

        st.markdown("**Total sample size of names matching search**")
        st.write(f':orange[Female counts]: {total_females:,}')
        st.write(f':violet[Male counts]: {total_males:,}')

    with col1:
        st.markdown("**Plotting Options**")
        plot_option = st.radio('If multiple names matched the search, how should they be plotted?',
                                ['Aggregated','Separated'],
                                captions=["(One line)", "(Multiple lines)"], 
                                help='"Separated" is not recommended if many names were returned in the search',
                                horizontal=True)


        options_map = {'Count':'n', 'Proportion':'proportion'}
        user_value = st.radio('Variable to plot', options_map.keys(), horizontal=True)
        plotted_variable = options_map[user_value]

        scale = st.radio('How should the y-axis be scaled?', ['Local','Global'],
                         horizontal=True,
                         help='"Global" scaling will use the same scale for all plots, regardless of name or gender. "Local" scaling is specific to the name(s) and gender in plot')


f_tab, m_tab = st.tabs(['Females','Males'])
with f_tab:
    st.header(":orange[Females]")
    st.subheader(f'Trend of {header_word}: *:orange[{pattern}]*')

    if plot_option=='Separated':
        f_fig = px.line(data_frame=f_df, x='year', y=plotted_variable, color='name',
                        color_discrete_sequence=px.colors.qualitative.Vivid)
    else:
        f_df_plot = f_df.groupby('year')[plotted_variable].sum().reset_index()
        f_fig = px.line(data_frame=f_df_plot, x='year', y=plotted_variable,
                        color_discrete_sequence=px.colors.qualitative.Vivid)

    if scale == 'Global':
        if plotted_variable == 'n':
            f_fig.update_layout(yaxis_range=[0,max_count])
        else:
            f_fig.update_layout(yaxis_range=[0,max_prop])

    if f_df.shape[0] > 0:
        st.plotly_chart(f_fig)
    else:
        st.write("No names returned")

with m_tab:
    st.header(":violet[Males]")
    st.subheader(f'Trend of {header_word}: *:violet[{pattern}]*')
    if plot_option=='Separated':
        m_fig = px.line(data_frame=m_df, x='year', y=plotted_variable, color='name',
                        color_discrete_sequence=px.colors.qualitative.Prism)
    else:
        m_df_plot = m_df.groupby('year')[plotted_variable].sum().reset_index()
        m_fig = px.line(data_frame=m_df_plot, x='year', y=plotted_variable,
                        color_discrete_sequence=px.colors.qualitative.Prism)

    if m_df.shape[0] > 0:
        st.plotly_chart(m_fig)
    else:
        st.write("No names returned")



### Name Facts
top_names = name_df.groupby('name')['n'].sum().sort_values(ascending=False).head(5).index        

#name_count 

with st.sidebar:
    st.header('Name Facts')
    st.write('For multiple names, order is determined by overall popularity and only the top five names are shown')
    st.divider()
    if len(top_names) == 0:
        st.write("No names returned")
    else:
        for name in top_names:
            st.write(f'**NAME: {name.upper()}**')
            f_temp = f_df[f_df['name']==name]
            m_temp = m_df[m_df['name']==name]

            # Females: 
            f_first_year = f_temp['year'].min()
            f_number_years = f_temp['year'].nunique()
            f_name = f_temp.n.sum()
            f_popular = most_popular_names[(most_popular_names['name']==name) & (most_popular_names['sex']=='F')]
            if f_popular.shape[0] == 0:
                f_years = 'None'
            else:
                f_years = ', '.join(list(f_popular['year'].astype(str)))

            # Males:
            m_first_year = m_temp['year'].min()
            m_number_years = m_temp['year'].nunique()
            m_name = m_temp.n.sum()
            m_popular = most_popular_names[(most_popular_names['name']==name) & (most_popular_names['sex']=='M')]
            if m_popular.shape[0] == 0:
                m_years = 'None'
            else:
                m_years = ', '.join(list(m_popular['year'].astype(str)))

            text = f"""
            * :orange[Females:]
                * First year in data: {f_first_year}
                * Total years in data: {f_number_years} (out of {n_years})
                * Total count: {f_name:,}
                * Year(s) most popular name: {f_years}
            * :violet[Males:]
                * First year in data: {m_first_year}
                * Total years in data: {m_number_years} (out of {n_years})
                * Total count: {m_name:,}
                * Year(s) most popular name: {m_years}

            """
            st.markdown(text)
            st.divider()



