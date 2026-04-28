"""
QuantaMatrix Rapid AST Market Dashboard
---------------------------------------

This Streamlit application provides a polished, multi-page dashboard
for the global rapid phenotypic antimicrobial susceptibility testing (AST)
market. It is designed as a strategic market research preview for
QuantaMatrix's executive team and stakeholders, translating the
comprehensive market models contained in the supplied DOCX reports into
interactive visuals and concise insights.

Key features include:

* Executive overview with boardroom-ready KPI cards and high-level narrative.
* Market architecture section showing TAM/SAM/SOM scaling and segment splits
  across infection type, hospital tier and geography.
* Competitive landscape with time‑to‑result benchmarking and a
  device‑level performance table, highlighting QuantaMatrix's position.
* Economics & ROI module featuring an interactive delay‑of‑therapy
  simulator that translates turn‑around time (TAT) into mortality risk
  and cost of delay, plus a revenue component breakdown.
* Strategic playbook outlining where to compete, how to win and
  risk‑mitigation levers, drawn directly from the source reports.

The visual identity carries forward the deep burgundy palette from
Strategic Market Research's prior dashboards, adapted here to
QuantaMatrix's context. All charts are separated cleanly into their
own containers to prevent overlap, and each page is self‑contained
to meet industry‑grade expectations.
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# ---------------------------------------------------------------------------
# Colour palette and basic configuration
# ---------------------------------------------------------------------------

# Deep burgundy palette used throughout the dashboard
BURGUNDY = "#5B0F2E"
BURGUNDY_DARK = "#431022"
BURGUNDY_MID = "#7A1C41"
BURGUNDY_SOFT = "#A45A7B"
GOLD = "#C9A227"
ROSE = "#EEDBE4"
BG = "#F8F5F6"
INK = "#1A1014"
MUTED = "#6B5B63"
BORDER = "rgba(91,15,46,0.1)"

# Set up the Streamlit page configuration
st.set_page_config(
    page_title="QuantaMatrix Rapid AST Market Dashboard",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Custom CSS: fonts, colours, layout polish
# ---------------------------------------------------------------------------

st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');
    html, body, [class*="css"] {{
        font-family: 'Plus Jakarta Sans', sans-serif !important;
        color: {INK};
    }}
    [data-testid="stSidebar"] {{
        background: rgba(255,255,255,0.75) !important;
        backdrop-filter: blur(10px) !important;
        border-right: 1px solid {BORDER};
    }}
    .stApp {{
        background: radial-gradient(circle at 20% 10%, rgba(201,162,39,0.05) 0%, transparent 35%),
                    radial-gradient(circle at 80% 90%, rgba(91,15,46,0.06) 0%, transparent 40%),
                    linear-gradient(180deg, #FCFAFB 0%, #F4ECEF 100%);
        background-attachment: fixed;
    }}
    ::-webkit-scrollbar {{ width: 6px; height:6px; }}
    ::-webkit-scrollbar-thumb {{ background: rgba(91,15,46,0.2); border-radius:10px; }}
    ::-webkit-scrollbar-thumb:hover {{ background: rgba(91,15,46,0.3); }}
    .metric-card {{
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(15px);
        border: 1px solid {BORDER};
        border-radius: 14px;
        padding: 20px;
        box-shadow: 0 6px 20px rgba(91,15,46,0.05);
        min-height: 125px;
    }}
    .metric-label {{
        color: {MUTED};
        font-size: 0.75rem;
        letter-spacing: 0.08em;
        font-weight: 700;
        text-transform: uppercase;
        margin-bottom: 6px;
    }}
    .metric-value {{
        color: {BURGUNDY};
        font-size: 2rem;
        font-weight: 800;
        margin-bottom: 6px;
    }}
    .metric-foot {{
        color: {MUTED};
        font-size: 0.8rem;
    }}
    .section-card {{
        background: rgba(255,255,255,0.85);
        backdrop-filter: blur(15px);
        border: 1px solid {BORDER};
        border-radius: 16px;
        padding: 24px;
        margin-bottom: 24px;
        box-shadow: 0 8px 24px rgba(91,15,46,0.05);
    }}
    .section-title {{
        font-size: 1.25rem;
        font-weight: 800;
        color: {BURGUNDY};
        margin-bottom: 4px;
    }}
    .section-sub {{
        color: {MUTED};
        font-size: 0.9rem;
        margin-bottom: 20px;
    }}
    .insight-box {{
        background: #ffffff;
        border: 1px solid rgba(201,162,39,0.2);
        border-left: 6px solid {GOLD};
        border-radius: 12px;
        padding: 18px;
        color: {INK};
        font-size: 0.95rem;
        line-height: 1.5;
        margin-top: 12px;
        box-shadow: 0 6px 18px rgba(201,162,39,0.05);
    }}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Helper functions for UI components
# ---------------------------------------------------------------------------

def card_metric(label: str, value: str, foot: str) -> None:
    """Render a compact metric card with a label, large value and footnote."""
    st.markdown(
        f'<div class="metric-card"><div class="metric-label">{label}</div>'
        f'<div class="metric-value">{value}</div>'
        f'<div class="metric-foot">{foot}</div></div>',
        unsafe_allow_html=True,
    )

def section_open(title: str, subtitle: str = "") -> None:
    """Open a section card with a title and optional subtitle."""
    st.markdown(
        f'<div class="section-card"><div class="section-title">{title}</div>'
        f'<div class="section-sub">{subtitle}</div>',
        unsafe_allow_html=True,
    )

def section_close() -> None:
    """Close a section card."""
    st.markdown('</div>', unsafe_allow_html=True)

def chart_theme(fig):
    """Apply a consistent theme to Plotly figures."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color=INK, family="'Plus Jakarta Sans', sans-serif"),
        margin=dict(l=10, r=10, t=40, b=10),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
        hoverlabel=dict(
            bgcolor="white",
            font_size=12,
            font_family="'Plus Jakarta Sans', sans-serif",
            bordercolor=BORDER,
        ),
    )
    fig.update_xaxes(showgrid=False, linecolor="rgba(0,0,0,0.05)", tickfont=dict(size=11, color=MUTED))
    fig.update_yaxes(gridcolor="rgba(91,15,46,0.06)", zeroline=False, tickfont=dict(size=11, color=MUTED))
    return fig

# ---------------------------------------------------------------------------
# Static datasets derived from source DOCX reports
# ---------------------------------------------------------------------------

def load_data():
    """Load pre-defined data frames from embedded structures.

    Data has been manually lifted from the provided Word reports to avoid
    runtime dependencies on python-docx. Should the underlying figures
    change, adjust the values here accordingly.
    """
    # Global market layers: TAM/SAM/SOM
    market_layers = pd.DataFrame({
        'Layer': ['TAM', 'SAM', 'SOM'],
        '2025': [4865.0, 1186.0, 82.7],
        '2030': [6791.6, 1945.0, 169.3],
        '2035': [9481.1, 3189.9, 264.5],
        'CAGR': [6.9, 10.4, 12.3],
    })

    # Segment breakdown by infection type
    segment_data = pd.DataFrame({
        'Segment': [
            'Sepsis / Bacteremia Core',
            'ICU / Severe Infection Extension',
            'Other Bloodstream Infection Workflows',
        ],
        '2025': [56.3, 18.2, 8.3],
        '2030': [111.8, 40.6, 16.9],
        '2035': [169.3, 68.8, 26.5],
        'CAGR': [11.6, 14.2, 12.3],
        'Share2035': [64, 26, 10],
    })

    # Revenue by hospital tier
    tier_data = pd.DataFrame({
        'Tier': [
            'Tier 1 Academic / Tertiary',
            'Tier 2 Regional Hospitals',
            'Tier 3 Selective Sites',
        ],
        '2025': [48.0, 24.8, 9.9],
        '2030': [93.1, 55.9, 20.3],
        '2035': [134.9, 95.2, 34.4],
        'CAGR': [10.9, 14.4, 13.2],
        'Share2035': [51, 36, 13],
    })

    # Revenue by region
    region_data = pd.DataFrame({
        'Region': ['North America', 'Europe', 'Asia Pacific', 'Latin America', 'Middle East & Africa', 'Top 20 Global Total'],
        '2025': [32.8, 17.0, 29.1, 2.2, 1.6, 82.7],
        '2030': [66.8, 34.2, 59.7, 5.1, 3.5, 169.3],
        '2035': [102.5, 55.3, 92.2, 8.9, 5.7, 264.5],
        'CAGR': [12.1, 12.5, 12.2, 15.0, 13.7, 12.3],
    })

    # Top countries by eligible AST volume (2025) and qualitative comments
    country_data = pd.DataFrame({
        'Country': ['China', 'United States', 'India', 'Japan', 'Germany', 'United Kingdom', 'France', 'South Korea'],
        'Region': ['Asia Pacific', 'North America', 'Asia Pacific', 'Asia Pacific', 'Europe', 'Europe', 'Europe', 'Asia Pacific'],
        'Eligible Volume': [309014, 135804, 215075, 34716, 26948, 23499, 18746, 14380],
        'Priority Tier': ['Tier 2', 'Tier 1', 'Tier 3', 'Tier 2', 'Tier 2', 'Tier 2', 'Tier 2', 'Tier 2'],
        'Comment': [
            'Large long-term opportunity; scaling dependent on channel and regulatory pathways',
            'Largest near-term revenue opportunity with premium pricing potential',
            'High burden market; selective early adoption in advanced centers',
            'Strong commercial fit with established clinical workflows',
            'Key EU market; reimbursement-driven',
            'NHS value-based procurement shift',
            'HAS clinical dossier is critical',
            'Home market; reference account hub',
        ],
    })

    # Device-level competitive matrix
    competitor_data = pd.DataFrame({
        'Company': ['QuantaMatrix', 'Gradientech AB', 'Q-linea', 'Accelerate Diagnostics', 'bioMérieux'],
        'Platform': ['dRAST', 'QuickMIC', 'ASTar', 'Pheno / PhenoTest BC', 'VITEK REVEAL'],
        # approximate mid‑point of the reported ranges for plotting
        'Time_to_Result (hrs)': [4.0, 3.0, 6.0, 7.0, 5.5],
        'Direct_from_Positive': ['Yes', 'Yes', 'Yes', 'Yes', 'Yes'],
        'Regulatory Position': [
            'CE‑IVDR; U.S. pathway in progress',
            'CE‑IVDR; U.S. submission disclosed',
            'FDA‑cleared; expanded menu',
            'FDA‑cleared legacy platform',
            'CE‑IVDR; FDA‑cleared',
        ],
        'Commercial Position': [
            'Sepsis‑focused rapid phenotypic specialist',
            'Ultra‑rapid, speed‑led specialist',
            'Automation‑led U.S./EU contender',
            'Installed‑base legacy + integrated ID',
            'Incumbent‑led rapid‑AST expansion',
        ],
    })

    # Sepsis and AMR burden metrics (for executive context)
    sepsis_data = [
        {'Label': 'Global Sepsis Cases', 'Value': '48.9M'},
        {'Label': 'Global Sepsis Deaths', 'Value': '11.0M'},
        {'Label': 'U.S. Sepsis Cases', 'Value': '1.7M'},
        {'Label': 'U.S. Hospital Mortality', 'Value': '≈1 in 3'},
        {'Label': 'AMR Direct Deaths', 'Value': '1.27M'},
        {'Label': 'U.S. Sepsis Cost', 'Value': '$62B'},
    ]

    # Revenue components for installed system economics
    revenue_components = pd.DataFrame({
        'Component': ['Instrument (ASP)', 'Consumable (Per Test)', 'Annual Service', 'Utilization (Tests/Year)'],
        '2025': [150000, 95, 15000, 1530],
        '2035': [165000, 105, 18000, 2306],
        'Strategic Role': [
            'Enables initial system placement',
            'Primary recurring revenue driver',
            'Ensures system uptime and retention',
            'Drives revenue scale per system',
        ],
    })

    # Installed base & utilization metrics (addressable pool etc.)
    adoption_metrics = pd.DataFrame({
        'Metric': ['Addressable Pool (Mn tests/episodes)', 'Installed Base (Systems)', 'Utilization (Tests/System/Year)', 'Implied Annual Test Volume (Mn)', 'Addressable Pool Penetration'],
        '2025': [6.80, 263, 1531, 0.40, 5.9],
        '2030': [7.91, 747, 1879, 1.40, 17.7],
        '2035': [9.20, 1064, 2306, 2.45, 26.7],
        'CAGR': [3.1, 15.0, 4.2, 19.8, None],
    })

    return {
        'market_layers': market_layers,
        'segment_data': segment_data,
        'tier_data': tier_data,
        'region_data': region_data,
        'country_data': country_data,
        'competitor_data': competitor_data,
        'sepsis_data': sepsis_data,
        'revenue_components': revenue_components,
        'adoption_metrics': adoption_metrics,
    }

# ---------------------------------------------------------------------------
# Page rendering functions
# ---------------------------------------------------------------------------

def render_overview(data: dict, scale: float) -> None:
    """Render the executive overview page."""
    # Title and introductory narrative
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {BURGUNDY} 0%, {BURGUNDY_MID} 60%, {BURGUNDY_SOFT} 100%); color:white; padding:30px 40px; border-radius:20px; margin-bottom:24px; position: relative;">
            <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; font-weight:800; color:{GOLD}; margin-bottom:6px;">Strategic Market Research</div>
            <h1 style="margin:0; font-size:2.4rem; font-weight:800; letter-spacing:-0.02em;">Executive Overview</h1>
            <p style="font-size:1rem; color:rgba(255,255,255,0.9); max-width:900px; line-height:1.5;">
                A boardroom‑level summary of the global rapid phenotypic AST opportunity.
                The true value driver lies not in broad microbiology automation but in sepsis‑focused adoption
                where speed directly alters therapy and hospital economics.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Pull key metrics
    som_2035 = data['market_layers'].loc[data['market_layers']['Layer'] == 'SOM', '2035'].iloc[0] * scale
    sepsis_cases = data['sepsis_data'][0]['Value']
    tat = '≈4 hrs'
    tier1_share = data['tier_data'].loc[data['tier_data']['Tier'] == 'Tier 1 Academic / Tertiary', 'Share2035'].iloc[0]

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        card_metric("2035 SOM (Rapid AST)", f"${som_2035:,.1f}M", "Serviceable obtainable market under selected scenario")
    with c2:
        card_metric("Global Sepsis Cases", sepsis_cases, "Annual burden driving demand")
    with c3:
        card_metric("dRAST Time‑to‑Result", tat, "Direct from positive blood culture")
    with c4:
        card_metric("Target Hospital Segment", "Tier 1", f"{tier1_share}% of 2035 revenue share")

    # Insight box
    st.markdown(
        '<div class="insight-box"><strong>Core Insight:</strong> Rapid AST adoption hinges on workflow economics, not just clinical curiosity. '
        'Success for QuantaMatrix requires a precise wedge strategy targeting high‑acuity bloodstream infections and ICU environments where speed translates into measurable cost‑of‑delay mitigation.</div>',
        unsafe_allow_html=True,
    )

    # Chart: TAM vs SAM vs SOM trajectory
    section_open("Market trajectory", "Scaling of TAM, SAM and SOM (scaled by scenario logic)")
    layers = data['market_layers'].copy()
    # Apply scaling factor to 2030 and 2035 for scenario analysis
    layers['2030_adj'] = layers.apply(lambda row: row['2030'] * scale if row['Layer'] != 'TAM' else row['2030'], axis=1)
    layers['2035_adj'] = layers.apply(lambda row: row['2035'] * scale if row['Layer'] != 'TAM' else row['2035'], axis=1)

    fig = go.Figure()
    for idx, row in layers.iterrows():
        fig.add_trace(go.Scatter(
            x=[2025, 2030, 2035],
            y=[row['2025'], row['2030_adj'], row['2035_adj']],
            mode="lines+markers",
            name=row['Layer'],
            line=dict(width=3, color=[BURGUNDY, GOLD, BURGUNDY_SOFT][idx]),
            marker=dict(size=8, color=[BURGUNDY, GOLD, BURGUNDY_SOFT][idx]),
        ))
    fig.update_layout(xaxis_title="Year", yaxis_title="Revenue ($Mn)")
    st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
    section_close()

    # Optional: display a table of sepsis burden metrics
    with st.expander("Sepsis & AMR Burden (contextual metrics)"):
        st.table(pd.DataFrame(data['sepsis_data']))

    # Footer
    st.markdown(
        f'<div style="margin-top:30px; text-align:center; padding: 20px; color:{MUTED}; font-size:0.75rem; border-top: 1px solid {BORDER};">'
        f'<strong>Strategic Market Research</strong> © {datetime.now().year} — Preview dashboard for QuantaMatrix.</div>',
        unsafe_allow_html=True,
    )


def render_market_architecture(data: dict, scale: float) -> None:
    """Render the market definition and segmentation page."""
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {BURGUNDY} 0%, {BURGUNDY_MID} 60%, {BURGUNDY_SOFT} 100%); color:white; padding:30px 40px; border-radius:20px; margin-bottom:24px; position: relative;">
            <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; font-weight:800; color:{GOLD}; margin-bottom:6px;">Market Architecture</div>
            <h1 style="margin:0; font-size:2.4rem; font-weight:800; letter-spacing:-0.02em;">Definition & Scaling</h1>
            <p style="font-size:1rem; color:rgba(255,255,255,0.9); max-width:900px; line-height:1.5;">
                This section defines the true addressable rapid AST market and demonstrates the projected revenue evolution through 2035.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Global market snapshot table
    ml = data['market_layers'].copy()
    ml_adj = ml[['Layer', '2025', '2030', '2035', 'CAGR']].copy()
    ml_adj.loc[ml_adj['Layer'] != 'TAM', '2030'] = ml_adj.loc[ml_adj['Layer'] != 'TAM', '2030'] * scale
    ml_adj.loc[ml_adj['Layer'] != 'TAM', '2035'] = ml_adj.loc[ml_adj['Layer'] != 'TAM', '2035'] * scale
    ml_adj['2025'] = ml_adj['2025'].map(lambda x: f"{x:,.1f}")
    ml_adj['2030'] = ml_adj['2030'].map(lambda x: f"{x:,.1f}")
    ml_adj['2035'] = ml_adj['2035'].map(lambda x: f"{x:,.1f}")
    ml_adj['CAGR'] = ml_adj['CAGR'].map(lambda x: f"{x:.1f}%")

    col1, col2 = st.columns([1, 1.5])
    with col1:
        section_open("Global Market Snapshot ($Mn)", "Calibrated TAM → SAM → SOM")
        st.dataframe(ml_adj.rename(columns={'Layer': 'Market Layer'}), use_container_width=True, hide_index=True)
        section_close()

        section_open("Installed Base & Utilization", "Selected adoption metrics")
        am = data['adoption_metrics'].copy()
        # scale metrics except TAM; we only scale test‑volume related entries where appropriate (Installed base, Utilization, test volume, penetration)
        for col in ['2030', '2035']:
            # installed base and utilization scale with scenario because higher adoption implies accelerated growth
            am[col] = am[col].apply(lambda x: x * scale if isinstance(x, (int, float)) else x)
        # Format numbers for display
        for col in ['2025', '2030', '2035']:
            am[col] = am[col].apply(lambda v: f"{v:,.1f}" if isinstance(v, (int, float, float)) else v)
        st.dataframe(am, use_container_width=True, hide_index=True)
        section_close()
    with col2:
        # Chart: stacked bar for TAM vs SAM vs SOM across 2025/2030/2035
        section_open("Market Layer Transition", "TAM→SAM→SOM growth trajectory")
        long_df = ml.melt(id_vars='Layer', value_vars=['2025', '2030', '2035'], var_name='Year', value_name='Value')
        long_df['Year'] = long_df['Year'].astype(int)
        # apply scaling to SAM/SOM values for 2030/2035
        long_df['Scaled'] = long_df.apply(
            lambda row: row['Value'] * scale if row['Layer'] != 'TAM' and row['Year'] > 2025 else row['Value'], axis=1
        )
        fig2 = px.bar(
            long_df,
            x='Year',
            y='Scaled',
            color='Layer',
            barmode='group',
            color_discrete_sequence=[BURGUNDY, GOLD, BURGUNDY_SOFT],
        )
        fig2.update_layout(xaxis_title="Year", yaxis_title="Revenue ($Mn)")
        st.plotly_chart(chart_theme(fig2), use_container_width=True, config={"displayModeBar": False})
        section_close()

        # Chart: segmentation by infection type (stacked area)
        section_open("Segment Composition", "By infection type across milestone years")
        seg = data['segment_data'].copy()
        seg_long = seg.melt(id_vars='Segment', value_vars=['2025', '2030', '2035'], var_name='Year', value_name='Revenue')
        seg_long['Year'] = seg_long['Year'].astype(int)
        seg_long['Revenue'] = seg_long.apply(
            lambda row: row['Revenue'] * scale if row['Year'] > 2025 else row['Revenue'], axis=1
        )
        fig3 = px.area(
            seg_long,
            x='Year',
            y='Revenue',
            color='Segment',
            color_discrete_sequence=[BURGUNDY, GOLD, BURGUNDY_SOFT],
        )
        fig3.update_layout(xaxis_title="Year", yaxis_title="Revenue ($Mn)")
        st.plotly_chart(chart_theme(fig3), use_container_width=True, config={"displayModeBar": False})
        section_close()

    # Secondary row: hospital tier and regional analysis
    col3, col4 = st.columns(2)
    with col3:
        section_open("Revenue by Hospital Tier (2035)", "Distribution of SOM across hospital tiers")
        tier = data['tier_data'].copy()
        tier['2035_scaled'] = tier['2035'] * scale
        fig4 = px.pie(
            tier,
            names='Tier',
            values='2035_scaled',
            hole=0.5,
            color_discrete_sequence=[BURGUNDY, GOLD, BURGUNDY_SOFT],
        )
        fig4.update_traces(textinfo='percent+label')
        st.plotly_chart(chart_theme(fig4), use_container_width=True, config={"displayModeBar": False})
        section_close()

    with col4:
        section_open("Revenue by Region (2035)", "Regional opportunity focus")
        reg = data['region_data'].copy()
        reg['2035_scaled'] = reg['2035'] * scale
        fig5 = px.bar(
            reg.sort_values('2035_scaled'),
            x='2035_scaled',
            y='Region',
            orientation='h',
            color='2035_scaled',
            color_continuous_scale=[[0, GOLD], [1, BURGUNDY]],
        )
        fig5.update_layout(coloraxis_showscale=False, xaxis_title="$Mn", yaxis_title="")
        st.plotly_chart(chart_theme(fig5), use_container_width=True, config={"displayModeBar": False})
        section_close()

    # Country bar chart and comments
    section_open("Top Country Opportunity (2025 Eligible Volume)", "Eight leading markets by eligible AST volume")
    cnt = data['country_data'].copy()
    fig6 = px.bar(
        cnt.sort_values('Eligible Volume').tail(8),
        x='Eligible Volume',
        y='Country',
        orientation='h',
        color='Eligible Volume',
        color_continuous_scale=[[0, GOLD], [1, BURGUNDY]],
    )
    fig6.update_layout(coloraxis_showscale=False, xaxis_title="Eligible AST Volume (2025)", yaxis_title="")
    st.plotly_chart(chart_theme(fig6), use_container_width=True, config={"displayModeBar": False})
    section_close()

    st.markdown(
        f'<div style="margin-top:30px; text-align:center; padding: 20px; color:{MUTED}; font-size:0.75rem; border-top: 1px solid {BORDER};">'
        f'<strong>Strategic Market Research</strong> © {datetime.now().year} — Preview dashboard for QuantaMatrix.</div>',
        unsafe_allow_html=True,
    )


def render_competitive_landscape(data: dict) -> None:
    """Render the competitive landscape page."""
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {BURGUNDY} 0%, {BURGUNDY_MID} 60%, {BURGUNDY_SOFT} 100%); color:white; padding:30px 40px; border-radius:20px; margin-bottom:24px; position: relative;">
            <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; font-weight:800; color:{GOLD}; margin-bottom:6px;">Competitive Landscape</div>
            <h1 style="margin:0; font-size:2.4rem; font-weight:800; letter-spacing:-0.02em;">Benchmarking & Positioning</h1>
            <p style="font-size:1rem; color:rgba(255,255,255,0.9); max-width:900px; line-height:1.5;">
                Mapping win/loss zones against direct rapid AST peers and incumbents. Understanding differentiation
                across speed, workflow integration and pricing is critical for positioning QuantaMatrix.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    col1, col2 = st.columns([1, 1])
    with col1:
        section_open("Time‑to‑Result Benchmark", "Average hours from positive blood culture")
        cd = data['competitor_data'].copy()
        fig = px.bar(
            cd.sort_values('Time_to_Result (hrs)'),
            x='Time_to_Result (hrs)',
            y='Company',
            orientation='h',
            color='Time_to_Result (hrs)',
            color_continuous_scale=[[0, GOLD], [1, BURGUNDY]],
        )
        fig.update_layout(coloraxis_showscale=False, xaxis_title="Hours", yaxis_title="")
        st.plotly_chart(chart_theme(fig), use_container_width=True, config={"displayModeBar": False})
        section_close()
    with col2:
        section_open("Interpretation", "Strategic narrative")
        st.markdown(
            """
            **Strategic Interpretation**

            Competitive intensity is high and rising. Incumbents possess deep lock‑in via legacy automated systems (e.g. VITEK 2, MicroScan). Direct peers such as Gradientech and Q‑linea already have European clearance. QuantaMatrix's primary differentiation lies in the ~4 hour MIC‑based phenotypic result directly from positive blood culture.

            To win, QuantaMatrix must emphasize random‑access throughput, workflow integration and definitive speed‑to‑therapy. Incumbent entrants like bioMérieux will bundle rapid AST with existing ecosystems; therefore the commercial story should highlight measurable cost‑of‑delay mitigation and clinical outcome benefits.
            """,
            unsafe_allow_html=True,
        )
        section_close()

    section_open("Device‑Level Performance & Pricing Matrix", "Competitive comparison across platforms")
    cd_table = data['competitor_data'].copy()
    # Highlight QuantaMatrix row by adding a column for styling (Streamlit cannot directly style rows, so we annotate the company name)
    st.dataframe(cd_table, use_container_width=True, hide_index=True)
    section_close()

    st.markdown(
        f'<div style="margin-top:30px; text-align:center; padding: 20px; color:{MUTED}; font-size:0.75rem; border-top: 1px solid {BORDER};">'
        f'<strong>Strategic Market Research</strong> © {datetime.now().year} — Preview dashboard for QuantaMatrix.</div>',
        unsafe_allow_html=True,
    )


def render_economics_roi(data: dict, tat_hours: int) -> None:
    """Render the economic justification & ROI page.

    Args:
        tat_hours: Targeted therapy delivery hours selected via slider.
    """
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {BURGUNDY} 0%, {BURGUNDY_MID} 60%, {BURGUNDY_SOFT} 100%); color:white; padding:30px 40px; border-radius:20px; margin-bottom:24px; position: relative;">
            <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; font-weight:800; color:{GOLD}; margin-bottom:6px;">Economics & ROI</div>
            <h1 style="margin:0; font-size:2.4rem; font-weight:800; letter-spacing:-0.02em;">Economic Value & Justification</h1>
            <p style="font-size:1rem; color:rgba(255,255,255,0.9); max-width:900px; line-height:1.5;">
                Quantifying the cost of delayed therapy. Translating clinical speed into a hard economic return‑on‑investment framework
                is critical for hospital procurement committees.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Simulator calculations: baseline is 4 hours (dRAST). Mortality risk increases by ~7.6% per hour of delay.
    baseline = 4
    hours_delay = max(tat_hours - baseline, 0)
    mortality_risk_increase = hours_delay * 7.6  # percent increase
    # Each 24h delay costs $3,531 and adds 1.4 days LOS; cost scales linearly with hours.
    cost_per_day = 3531
    cost_delay = (hours_delay / 24.0) * cost_per_day

    # Layout: left side interactive slider and metrics; right side narrative
    col1, col2 = st.columns([1, 1])
    with col1:
        section_open("Value of Speed Simulator", "Adjust time to targeted therapy (hrs)")
        st.write("Select hours from positive blood culture to targeted therapy:")
        st.slider(
            label="Targeted therapy delivery (hrs)",
            min_value=3,
            max_value=48,
            value=tat_hours,
            key="tat_slider",
            on_change=lambda: None,
        )
        # Display calculated metrics
        st.markdown(
            f"""
            <div class="metric-card" style="background:#fff5f7;">
                <div class="metric-label">Estimated Mortality Risk Increase</div>
                <div class="metric-value" style="color:#c0392b;">{mortality_risk_increase:.0f}%</div>
                <div class="metric-foot">vs. immediate therapy at 4 hrs</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown(
            f"""
            <div class="metric-card" style="background:#f0fbf9;">
                <div class="metric-label">Cost of Delay (per patient)</div>
                <div class="metric-value" style="color:{BURGUNDY};">${cost_delay:,.0f}</div>
                <div class="metric-foot">Excess treatment & LOS costs</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        section_close()

    with col2:
        section_open("Procurement Decision Drivers", "Why hospitals invest in rapid AST")
        st.markdown(
            """
            A $95 rapid test may appear expensive relative to a $35 conventional panel, but reducing the time‑to‑result from 24 hours to 4 hours yields significant economic and clinical value:

            • **ICU de‑escalation:** Shaving 20 hours off broad‑spectrum empiric therapy reduces toxicities and allows earlier patient discharge.
            
            • **Stewardship alignment:** Rapid phenotypic MICs drive high‑confidence therapy step‑downs, aligning with hospital quality metrics.

            • **Cost of delay:** Each day of inappropriate therapy adds over $3,500 in costs and 1.4 days of length of stay.

            Hospitals will accept premium test pricing when capital expenditure barriers are removed via reagent rental or risk‑sharing models tied to verifiable outcome improvements.
            """,
            unsafe_allow_html=True,
        )
        section_close()

    # Revenue components table
    section_open("Revenue Structure per Installed System", "Base case versus maturity")
    rc = data['revenue_components'].copy()
    # Format numbers into friendly strings
    rc_display = rc.copy()
    rc_display['2025'] = rc_display['2025'].apply(lambda v: f"${v:,.0f}" if isinstance(v, (int, float)) else v)
    rc_display['2035'] = rc_display['2035'].apply(lambda v: f"${v:,.0f}" if isinstance(v, (int, float)) else v)
    st.dataframe(rc_display.rename(columns={'Component': 'Revenue Component', '2035': '2035 (Maturity)'}), use_container_width=True, hide_index=True)
    section_close()

    st.markdown(
        f'<div style="margin-top:30px; text-align:center; padding: 20px; color:{MUTED}; font-size:0.75rem; border-top: 1px solid {BORDER};">'
        f'<strong>Strategic Market Research</strong> © {datetime.now().year} — Preview dashboard for QuantaMatrix.</div>',
        unsafe_allow_html=True,
    )


def render_playbook(data: dict) -> None:
    """Render the strategic playbook page."""
    st.markdown(
        f"""
        <div style="background: linear-gradient(135deg, {BURGUNDY} 0%, {BURGUNDY_MID} 60%, {BURGUNDY_SOFT} 100%); color:white; padding:30px 40px; border-radius:20px; margin-bottom:24px; position: relative;">
            <div style="font-size:0.75rem; text-transform:uppercase; letter-spacing:0.1em; font-weight:800; color:{GOLD}; margin-bottom:6px;">Strategic Playbook</div>
            <h1 style="margin:0; font-size:2.4rem; font-weight:800; letter-spacing:-0.02em;">Execution Strategy & Playbook</h1>
            <p style="font-size:1rem; color:rgba(255,255,255,0.9); max-width:900px; line-height:1.5;">
                Transitioning from technology advantage to commercial precision. This section defines where to compete,
                how to win and how to mitigate adoption risk across geographies and customer segments.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )

    # Playbook content structured in three cards
    col1, col2 = st.columns(2)
    with col1:
        section_open("Where to Compete", "Geographies & customer focus")
        st.markdown(
            """
            **Geography prioritization**

            * **Europe & Middle East (near‑term):** High readiness driven by CE‑IVDR status and established distributor networks. AMR burden in southern and eastern Europe creates urgency; local reimbursement pathways (e.g. NUB in Germany, LPPR in France) must be leveraged.
            
            * **United States (strategic pipeline):** Massive acute‑care market (1.7 M sepsis hospitalizations) but gated by pending 510(k) clearance and entrenched incumbents. NTAP designation is critical for early reimbursement.
            
            * **Asia Pacific (growth engine):** Led by South Korea and China. Home market provides reference accounts; long‑term expansion dependent on pricing strategy and infrastructure maturity.

            **Customer segmentation**

            Focus exclusively on **Tier 1 / academic / tertiary hospitals**. These environments possess the ICU complexity, stewardship sophistication and blood‑culture volume to justify premium rapid AST economics. Tier 2 hospitals may be addressed via reagent rental once the installed base scales.
            """,
            unsafe_allow_html=True,
        )
        section_close()

    with col2:
        section_open("How to Compete", "Differentiation & pricing")
        st.markdown(
            """
            **Workflow integration narrative**

            Position dRAST not as a lab replacement but as an **ICU optimization layer**. Bundle the platform with upstream rapid identification (e.g. MALDI‑TOF) to create a same‑shift targeted therapy workflow.

            **Pricing structure**

            Transition from pure capital sales (~$150 k ASP) to **reagent rental models**. Hospitals will accept ~$95/test operating costs if capital barriers are removed. Consider risk‑sharing arrangements tied to outcome improvements to accelerate adoption in Tier 2 settings.
            """,
            unsafe_allow_html=True,
        )
        section_close()

    # Risk mitigation card (full width)
    section_open("Risk & Frictional Barriers", "Key adoption constraints and mitigation levers")
    st.markdown(
        """
        * **Incumbent bundling:** bioMérieux and BD will discount routine AST panels to block rapid AST adoption. **Mitigation:** Quantify ICU length‑of‑stay savings that dwarf lab budget variations and position rapid AST as a hospital‑wide value driver.

        * **Behavioural resistance:** Clinicians may wait for 24h conventional confirmation. **Mitigation:** Integrate rapid AST into antimicrobial stewardship protocols and publish local validation studies highlighting improved outcomes.

        * **Ultra‑rapid threat:** Gradientech QuickMIC claims 2–4 hour turnaround. **Mitigation:** Emphasize dRAST's random‑access throughput (up to 12 samples) and broader validated menu stability. Throughput and menu breadth are critical differentiators beyond speed alone.
        """,
        unsafe_allow_html=True,
    )
    section_close()

    st.markdown(
        f'<div style="margin-top:30px; text-align:center; padding: 20px; color:{MUTED}; font-size:0.75rem; border-top: 1px solid {BORDER};">'
        f'<strong>Strategic Market Research</strong> © {datetime.now().year} — Preview dashboard for QuantaMatrix.</div>',
        unsafe_allow_html=True,
    )


# ---------------------------------------------------------------------------
# Main application logic: sidebar navigation and page dispatch
# ---------------------------------------------------------------------------

def main():
    data = load_data()
    # Sidebar branding
    st.sidebar.markdown(
        f'<div style="background:rgba(255,255,255,0.8); padding:20px; border-radius:12px; margin-bottom:24px;">'
        f'<h2 style="color:{BURGUNDY}; margin:0; font-size:1rem; font-weight:800; letter-spacing:-0.02em;">QuantaMatrix Dashboard</h2>'
        f'<p style="color:{MUTED}; margin:4px 0 0 0; font-size:0.75rem; font-weight:500;">Rapid Phenotypic AST Market</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    # Scenario scaling slider
    scale = st.sidebar.slider(
        label="Scenario scaling multiplier",
        min_value=0.8,
        max_value=1.2,
        value=1.0,
        step=0.05,
        help="Adjusts the 2030/2035 values to simulate downside (0.8x) or upside (1.2x) scenarios."
    )
    page = st.sidebar.radio(
        "Navigate", ["Executive Overview", "Market Architecture", "Competitive Landscape", "Economics & ROI", "Strategic Playbook"],
        index=0
    )
    if page == "Executive Overview":
        render_overview(data, scale)
    elif page == "Market Architecture":
        render_market_architecture(data, scale)
    elif page == "Competitive Landscape":
        render_competitive_landscape(data)
    elif page == "Economics & ROI":
        # Use a separate slider within the ROI page for TAT selection
        tat_hours = st.sidebar.slider(
            label="Targeted therapy hours", min_value=3, max_value=48, value=24,
            help="Adjusts the hours from positive blood culture to targeted therapy for ROI simulation"
        )
        render_economics_roi(data, tat_hours)
    elif page == "Strategic Playbook":
        render_playbook(data)


if __name__ == "__main__":
    main()
