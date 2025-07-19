import dash
from dash import dcc, html, Input, Output, State
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import os
import dash_bootstrap_components as dbc

# Initialize the Dash app with a Bootstrap theme for enhanced visual appeal
app = dash.Dash(__name__, external_stylesheets=[dbc.themes.CYBORG])
server = app.server  # For deploying on a server

# Load and preprocess the data
def load_and_process_data():
    data_frames = []
    years = [2015, 2016, 2017, 2018, 2019]
    for year in years:
        filename = f'dataset/{year}.csv'
        df = pd.read_csv(filename)
        if year == 2015:
            df = df.rename(columns={
                'Country': 'Country',
                'Region': 'Region',
                'Happiness Rank': 'Rank',
                'Happiness Score': 'Score',
                'Economy (GDP per Capita)': 'GDP per Capita',
                'Family': 'Social support',
                'Health (Life Expectancy)': 'Healthy life expectancy',
                'Freedom': 'Freedom',
                'Trust (Government Corruption)': 'Perceptions of corruption',
                'Generosity': 'Generosity'
            })
        elif year == 2016:
            df = df.rename(columns={
                'Country': 'Country',
                'Region': 'Region',
                'Happiness Rank': 'Rank',
                'Happiness Score': 'Score',
                'Economy (GDP per Capita)': 'GDP per Capita',
                'Family': 'Social support',
                'Health (Life Expectancy)': 'Healthy life expectancy',
                'Freedom': 'Freedom',
                'Trust (Government Corruption)': 'Perceptions of corruption',
                'Generosity': 'Generosity'
            })
        elif year == 2017:
            df = df.rename(columns={
                'Country': 'Country',
                'Happiness.Rank': 'Rank',
                'Happiness.Score': 'Score',
                'Economy..GDP.per.Capita.': 'GDP per Capita',
                'Family': 'Social support',
                'Health..Life.Expectancy.': 'Healthy life expectancy',
                'Freedom': 'Freedom',
                'Trust..Government.Corruption.': 'Perceptions of corruption',
                'Generosity': 'Generosity'
            })
            df['Region'] = None  # No region data in 2017
        elif year in [2018, 2019]:
            df = df.rename(columns={
                'Country or region': 'Country',
                'Overall rank': 'Rank',
                'Score': 'Score',
                'GDP per capita': 'GDP per Capita',
                'Social support': 'Social support',
                'Healthy life expectancy': 'Healthy life expectancy',
                'Freedom to make life choices': 'Freedom',
                'Perceptions of corruption': 'Perceptions of corruption',
                'Generosity': 'Generosity'
            })
            df['Region'] = None  # No region data
        # Add Year column
        df['Year'] = year
        data_frames.append(df)
    # Concatenate all dataframes
    all_data = pd.concat(data_frames, ignore_index=True)
    # Fill missing regions with 'Unknown'
    all_data['Region'] = all_data['Region'].fillna('Unknown')
    # Ensure Year is integer
    all_data['Year'] = all_data['Year'].astype(int)
    return all_data

# Load the data
df = load_and_process_data()

# App layout
app.layout = dbc.Container([
    dbc.Row([
        dbc.Col(html.H1("World Happiness Report Dashboard", className='text-center text-primary, mb-4'), width=12)
    ], style={'marginTop': 20}),
    dbc.Row([
        dbc.Col([
            html.Label("Select Year:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='year-dropdown',
                options=[{'label': str(year), 'value': year} for year in sorted(df['Year'].unique())],
                value=2019,
                clearable=False,
                style={'color': 'black'}
            )
        ], width={'size': 4}),
        dbc.Col([
            html.Label("Select Countries:", style={'fontWeight': 'bold'}),
            dcc.Dropdown(
                id='country-dropdown',
                options=[{'label': country, 'value': country} for country in sorted(df['Country'].unique())],
                multi=True,
                value=['Finland'],
                style={'color': 'black'}
            )
        ], width={'size': 8})
    ], style={'margin-bottom': '25px'}),
    dbc.Row([
        dbc.Col([
            html.Label("Select Top N Countries:", style={'fontWeight': 'bold'}),
            dcc.Slider(
                id='top-n-slider',
                min=1,
                max=20,
                step=1,
                value=10,
                marks={i: str(i) for i in range(1, 21)},
                tooltip={"always_visible": False, "placement": "bottom"}
            ),
        ], width=12)
    ], style={'margin-bottom': '25px'}),
    dcc.Tabs(id='tabs', value='tab-overview', children=[
        dcc.Tab(label='Overview', value='tab-overview'),
        dcc.Tab(label='Economic Factors', value='tab-economic'),
        dcc.Tab(label='Social Factors', value='tab-social'),
        dcc.Tab(label='Health Factors', value='tab-health'),
        dcc.Tab(label='Trust and Generosity', value='tab-trust'),
    ]),
    html.Div(id='tabs-content')
], fluid=True, style={'backgroundColor': 'black'})

# Callbacks to update the content based on selected tab
@app.callback(
    Output('tabs-content', 'children'),
    [Input('tabs', 'value'),
     Input('year-dropdown', 'value'),
     Input('country-dropdown', 'value'),
     Input('top-n-slider', 'value')]
)
def render_content(tab, selected_year, selected_countries, top_n):
    if tab == 'tab-overview':
        return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=generate_line_chart(selected_countries)), width=12),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=generate_choropleth_map(selected_year)), width=12),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=generate_bar_chart(selected_year, top_n)), width=6),
                dbc.Col(dcc.Graph(figure=generate_radar_chart(selected_year, selected_countries)), width=6),
            ]),
        ])
    elif tab == 'tab-economic':
        return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=generate_gdp_line_chart(selected_countries)), width=12),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=generate_gdp_bar(selected_year, top_n)), width=6),
                dbc.Col(dcc.Graph(figure=generate_gdp_boxplot(selected_year)), width=6),
            ]),
        ])
    elif tab == 'tab-social':
        return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=generate_social_line_chart(selected_countries)), width=12),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=generate_social_support_bar(selected_year, top_n)), width=6),
                dbc.Col(dcc.Graph(figure=generate_social_violin_plot(selected_year)), width=6),
            ]),
        ])
    elif tab == 'tab-health':
        return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=generate_health_line_chart(selected_countries)), width=12),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=generate_health_bar(selected_year, top_n)), width=6),
                dbc.Col(dcc.Graph(figure=generate_health_violin_plot(selected_year)), width=6),
            ]),
        ])
    elif tab == 'tab-trust':
        return dbc.Container([
            dbc.Row([
                dbc.Col(dcc.Graph(figure=generate_corruption_map(selected_year)), width=12),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=generate_generosity_bar(selected_year, top_n)), width=6),
                dbc.Col(dcc.Graph(figure=generate_corruption_vs_score(selected_year)), width=6),
            ]),
            dbc.Row([
                dbc.Col(dcc.Graph(figure=generate_generosity_line_chart(selected_countries)), width=12),
            ]),
        ])

# Functions to generate graphs

# Overview Tab
def generate_line_chart(selected_countries):
    if not selected_countries:
        selected_countries = ['Finland']
    filtered_df = df[df['Country'].isin(selected_countries)]
    fig = px.line(filtered_df, x='Year', y='Score', color='Country', markers=True, template='plotly_dark')
    fig.update_layout(title='Happiness Score over Years', height=500)
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=filtered_df['Year'].min(), dtick=1))
    return fig

def generate_bar_chart(selected_year, top_n):
    filtered_df = df[df['Year'] == selected_year]
    filtered_df = filtered_df.sort_values('Score', ascending=False).head(top_n)
    fig = px.bar(filtered_df, x='Country', y='Score', color='Country', template='plotly_dark')
    fig.update_layout(title=f'Top {top_n} Happiest Countries in {selected_year}', showlegend=False)
    return fig

def generate_choropleth_map(selected_year):
    filtered_df = df[df['Year'] == selected_year]
    fig = px.choropleth(filtered_df, locations='Country', locationmode="country names", color='Score',
                        hover_name='Country', color_continuous_scale=px.colors.sequential.Plasma,
                        title=f'World Happiness Score in {selected_year}', template='plotly_dark', height=500)
    return fig

def generate_radar_chart(selected_year, selected_countries):
    if not selected_countries:
        selected_countries = ['Finland']
    factors = ['GDP per Capita', 'Social support', 'Healthy life expectancy', 'Freedom',
               'Perceptions of corruption', 'Generosity']
    filtered_df = df[df['Year'] == selected_year]
    filtered_df = filtered_df[filtered_df['Country'].isin(selected_countries)]
    data = []
    for country in selected_countries:
        country_data = filtered_df[filtered_df['Country'] == country]
        if not country_data.empty:
            values = country_data[factors].values.flatten().tolist()
            data.append(go.Scatterpolar(
                r=values,
                theta=factors,
                fill='toself',
                name=country
            ))
    fig = go.Figure(data=data)
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True)
        ),
        showlegend=True,
        title=f'Factors Contributing to Happiness Score in {selected_year}',
        template='plotly_dark',
        height=500
    )
    return fig

# Economic Factors Tab
def generate_gdp_line_chart(selected_countries):
    if not selected_countries:
        selected_countries = ['Finland']
    filtered_df = df[df['Country'].isin(selected_countries)]
    fig = px.line(filtered_df, x='Year', y='GDP per Capita', color='Country', markers=True, template='plotly_dark')
    fig.update_layout(title='GDP per Capita over Years', height=500)
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=filtered_df['Year'].min(), dtick=1))
    return fig

def generate_gdp_bar(selected_year, top_n):
    filtered_df = df[df['Year'] == selected_year]
    filtered_df = filtered_df.sort_values('GDP per Capita', ascending=False).head(top_n)
    fig = px.bar(filtered_df, x='Country', y='GDP per Capita', color='Country', template='plotly_dark')
    fig.update_layout(title=f'Top {top_n} Countries by GDP per Capita in {selected_year}', showlegend=False)
    return fig

def generate_gdp_boxplot(selected_year):
    filtered_df = df[df['Year'] == selected_year]
    fig = px.box(filtered_df, y='GDP per Capita', points="all", template='plotly_dark')
    fig.update_layout(title=f'GDP per Capita Distribution in {selected_year}')
    return fig

# Social Factors Tab
def generate_social_line_chart(selected_countries):
    if not selected_countries:
        selected_countries = ['Finland']
    filtered_df = df[df['Country'].isin(selected_countries)]
    fig = px.line(filtered_df, x='Year', y='Social support', color='Country', markers=True, template='plotly_dark')
    fig.update_layout(title='Social Support over Years', height=500)
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=filtered_df['Year'].min(), dtick=1))
    return fig

def generate_social_support_bar(selected_year, top_n):
    filtered_df = df[df['Year'] == selected_year]
    filtered_df = filtered_df.sort_values('Social support', ascending=False).head(top_n)
    fig = px.bar(filtered_df, x='Country', y='Social support', color='Country', template='plotly_dark')
    fig.update_layout(title=f'Top {top_n} Countries by Social Support in {selected_year}', showlegend=False)
    return fig

def generate_social_violin_plot(selected_year):
    filtered_df = df[df['Year'] == selected_year]
    fig = px.violin(filtered_df, y='Social support', box=True, points='all', template='plotly_dark')
    fig.update_layout(title=f'Social Support Distribution in {selected_year}')
    return fig

# Health Factors Tab
def generate_health_line_chart(selected_countries):
    if not selected_countries:
        selected_countries = ['Finland']
    filtered_df = df[df['Country'].isin(selected_countries)]
    fig = px.line(filtered_df, x='Year', y='Healthy life expectancy', color='Country', markers=True, template='plotly_dark')
    fig.update_layout(title='Healthy Life Expectancy over Years', height=500)
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=filtered_df['Year'].min(), dtick=1))
    return fig

def generate_health_bar(selected_year, top_n):
    filtered_df = df[df['Year'] == selected_year]
    filtered_df = filtered_df.sort_values('Healthy life expectancy', ascending=False).head(top_n)
    fig = px.bar(filtered_df, x='Country', y='Healthy life expectancy', color='Country', template='plotly_dark')
    fig.update_layout(title=f'Top {top_n} Countries by Healthy Life Expectancy in {selected_year}', showlegend=False)
    return fig

def generate_health_violin_plot(selected_year):
    filtered_df = df[df['Year'] == selected_year]
    fig = px.violin(filtered_df, y='Healthy life expectancy', box=True, points='all', template='plotly_dark')
    fig.update_layout(title=f'Healthy Life Expectancy Distribution in {selected_year}')
    return fig

# Trust and Generosity Tab
def generate_corruption_map(selected_year):
    filtered_df = df[df['Year'] == selected_year]
    fig = px.choropleth(filtered_df, locations='Country', locationmode="country names", color='Perceptions of corruption',
                        hover_name='Country', color_continuous_scale=px.colors.sequential.Plasma_r,
                        title=f'Perceptions of Corruption in {selected_year}', template='plotly_dark', height=500)
    return fig

def generate_generosity_bar(selected_year, top_n):
    filtered_df = df[df['Year'] == selected_year]
    filtered_df = filtered_df.nlargest(top_n, 'Generosity')
    fig = px.bar(filtered_df, x='Country', y='Generosity', color='Country', template='plotly_dark')
    fig.update_layout(title=f'Top {top_n} Countries by Generosity in {selected_year}', showlegend=False)
    return fig

def generate_corruption_vs_score(selected_year):
    filtered_df = df[df['Year'] == selected_year]
    fig = px.scatter(filtered_df, x='Perceptions of corruption', y='Score', hover_name='Country', template='plotly_dark')
    fig.update_layout(title=f'Perceptions of Corruption vs Happiness Score in {selected_year}')
    return fig

def generate_generosity_line_chart(selected_countries):
    if not selected_countries:
        selected_countries = ['Finland']
    filtered_df = df[df['Country'].isin(selected_countries)]
    fig = px.line(filtered_df, x='Year', y='Generosity', color='Country', markers=True, template='plotly_dark')
    fig.update_layout(title='Generosity over Years', height=500)
    fig.update_layout(xaxis=dict(tickmode='linear', tick0=filtered_df['Year'].min(), dtick=1))
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=False)
