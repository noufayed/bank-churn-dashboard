import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px
import pandas as pd

# 1. تحميل البيانات المنظفة
df = pd.read_csv("cleaned_bank_churn.csv")

# 2. إنشاء التطبيق
app = dash.Dash(__name__)
app.title = "Bank Customer Churn Dashboard"

# 3. تصميم الواجهة (Layout)
app.layout = html.Div(style={'backgroundColor': '#f8f9fa', 'padding': '20px', 'fontFamily': 'Arial'}, children=[
    
    # Header / العنوان
    html.H1("Bank Customer Churn & Risk Intelligence", style={'textAlign': 'center', 'color': '#1f2d3d', 'marginBottom': '30px'}),
    
    # Row 1: Key Metrics (KPI Cards)
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between', 'marginBottom': '30px'}, children=[
        html.Div(style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '10px', 'width': '30%', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center'}, children=[
            html.H4("Total Customers", style={'color': '#6c757d', 'margin': '0'}),
            html.H2(f"{len(df):,}", style={'color': '#007bff', 'margin': '10px 0 0 0'})
        ]),
        html.Div(style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '10px', 'width': '30%', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center'}, children=[
            html.H4("Overall Churn Rate", style={'color': '#6c757d', 'margin': '0'}),
            html.H2(f"{(df['Exited'].mean() * 100):.1f}%", style={'color': '#dc3545', 'margin': '10px 0 0 0'})
        ]),
        html.Div(style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '10px', 'width': '30%', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'textAlign': 'center'}, children=[
            html.H4("Total At-Risk Balance", style={'color': '#6c757d', 'margin': '0'}),
            html.H2(f"${df[df['Exited'] == 1]['Balance'].sum():,.0f}", style={'color': '#fd7e14', 'margin': '10px 0 0 0'})
        ]),
    ]),
    
    # Row 2: Filters (القوائم المنسدلة)
    html.Div(style={'backgroundColor': '#ffffff', 'padding': '20px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)', 'marginBottom': '30px'}, children=[
        html.Label("Select Country (Geography):", style={'fontWeight': 'bold', 'color': '#333'}),
        dcc.Dropdown(
            id='country-filter',
            options=[{'label': 'All Countries', 'value': 'All'}] + [{'label': country, 'value': country} for country in df['Geography'].unique()],
            value='All',
            clearable=False,
            style={'marginTop': '10px'}
        )
    ]),
    
    # Row 3: Interactive Graphs (الأشكال البيانية)
    html.Div(style={'display': 'flex', 'justifyContent': 'space-between'}, children=[
        html.Div(style={'width': '49%', 'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
            dcc.Graph(id='churn-by-age-graph')
        ]),
        html.Div(style={'width': '49%', 'backgroundColor': '#ffffff', 'padding': '15px', 'borderRadius': '10px', 'boxShadow': '0 2px 4px rgba(0,0,0,0.1)'}, children=[
            dcc.Graph(id='balance-vs-score-graph')
        ])
    ])
])

# 4. Callbacks (ربط الفلتر بالأشكال البيانية)
@app.callback(
    [Output('churn-by-age-graph', 'figure'),
     Output('balance-vs-score-graph', 'figure')],
    [Input('country-filter', 'value')]
)
def update_graphs(selected_country):
    # تصفية البيانات حسب الدولة المختارة
    if selected_country == 'All':
        filtered_df = df
    else:
        filtered_df = df[df['Geography'] == selected_country]
        
    # الرسم البياني الأول: نسبة المغادرة حسب الفئة العمرية
    age_churn = filtered_df.groupby('AgeGroup', observed=False)['Exited'].mean().reset_index()
    age_churn['ChurnRate'] = age_churn['Exited'] * 100
    
    fig_age = px.bar(
        age_churn, 
        x='AgeGroup', 
        y='ChurnRate', 
        title=f"Churn Rate by Age Group ({selected_country})",
        labels={'ChurnRate': 'Churn Rate (%)', 'AgeGroup': 'Age Group'},
        color_discrete_sequence=['#e63946']
    )
    fig_age.update_layout(template='plotly_white')
    
    # الرسم البياني الثاني: العلاقة بين الدرجة الائتمانية والرصيد
    fig_balance = px.scatter(
        filtered_df, 
        x='CreditScore', 
        y='Balance', 
        color=filtered_df['Exited'].map({0: 'Retained', 1: 'Exited'}),
        title=f"Credit Score vs Balance ({selected_country})",
        labels={'color': 'Customer Status'},
        color_discrete_map={'Retained': '#2a9d8f', 'Exited': '#e63946'},
        opacity=0.6
    )
    fig_balance.update_layout(template='plotly_white')
    
    return fig_age, fig_balance

# 5. تشغيل التطبيق
if __name__ == '__main__':
    app.run(debug=True)