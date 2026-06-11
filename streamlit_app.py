import streamlit as st
import pandas as pd
import math
from pathlib import Path

st.set_page_config(
    page_title='GDP dashboard',
    page_icon=':earth_americas:',
)

# Maps individual country codes to world regions (excludes World Bank aggregate rows)
REGION_MAP = {
    'AFG': 'Asia', 'ARE': 'Asia', 'ARM': 'Asia', 'AZE': 'Asia', 'BGD': 'Asia',
    'BHR': 'Asia', 'BRN': 'Asia', 'BTN': 'Asia', 'CHN': 'Asia', 'GEO': 'Asia',
    'IDN': 'Asia', 'IND': 'Asia', 'IRN': 'Asia', 'IRQ': 'Asia', 'ISR': 'Asia',
    'JOR': 'Asia', 'JPN': 'Asia', 'KAZ': 'Asia', 'KGZ': 'Asia', 'KHM': 'Asia',
    'KOR': 'Asia', 'KWT': 'Asia', 'LAO': 'Asia', 'LBN': 'Asia', 'LKA': 'Asia',
    'MDV': 'Asia', 'MMR': 'Asia', 'MNG': 'Asia', 'MYS': 'Asia', 'NPL': 'Asia',
    'OMN': 'Asia', 'PAK': 'Asia', 'PHL': 'Asia', 'PSE': 'Asia', 'QAT': 'Asia',
    'SAU': 'Asia', 'SGP': 'Asia', 'SYR': 'Asia', 'THA': 'Asia', 'TJK': 'Asia',
    'TKM': 'Asia', 'TLS': 'Asia', 'TUR': 'Asia', 'UZB': 'Asia', 'VNM': 'Asia',
    'YEM': 'Asia',
    'ALB': 'Europe', 'AND': 'Europe', 'AUT': 'Europe', 'BEL': 'Europe', 'BGR': 'Europe',
    'BIH': 'Europe', 'BLR': 'Europe', 'CHE': 'Europe', 'CYP': 'Europe', 'CZE': 'Europe',
    'DEU': 'Europe', 'DNK': 'Europe', 'ESP': 'Europe', 'EST': 'Europe', 'FIN': 'Europe',
    'FRA': 'Europe', 'GBR': 'Europe', 'GRC': 'Europe', 'HRV': 'Europe', 'HUN': 'Europe',
    'IRL': 'Europe', 'ISL': 'Europe', 'ITA': 'Europe', 'LIE': 'Europe', 'LTU': 'Europe',
    'LUX': 'Europe', 'LVA': 'Europe', 'MCO': 'Europe', 'MDA': 'Europe', 'MKD': 'Europe',
    'MLT': 'Europe', 'MNE': 'Europe', 'NLD': 'Europe', 'NOR': 'Europe', 'POL': 'Europe',
    'PRT': 'Europe', 'ROU': 'Europe', 'RUS': 'Europe', 'SMR': 'Europe', 'SRB': 'Europe',
    'SVK': 'Europe', 'SVN': 'Europe', 'SWE': 'Europe', 'UKR': 'Europe', 'XKX': 'Europe',
    'ARG': 'Americas', 'ATG': 'Americas', 'BLZ': 'Americas', 'BOL': 'Americas',
    'BRA': 'Americas', 'BRB': 'Americas', 'CAN': 'Americas', 'CHL': 'Americas',
    'COL': 'Americas', 'CRI': 'Americas', 'CUB': 'Americas', 'DMA': 'Americas',
    'DOM': 'Americas', 'ECU': 'Americas', 'GTM': 'Americas', 'GUY': 'Americas',
    'HND': 'Americas', 'HTI': 'Americas', 'JAM': 'Americas', 'MEX': 'Americas',
    'NIC': 'Americas', 'PAN': 'Americas', 'PER': 'Americas', 'PRY': 'Americas',
    'SLV': 'Americas', 'SUR': 'Americas', 'TTO': 'Americas', 'URY': 'Americas',
    'USA': 'Americas', 'VCT': 'Americas',
    'AGO': 'Africa', 'BDI': 'Africa', 'BEN': 'Africa', 'BFA': 'Africa', 'BWA': 'Africa',
    'CAF': 'Africa', 'CIV': 'Africa', 'CMR': 'Africa', 'COD': 'Africa', 'COG': 'Africa',
    'COM': 'Africa', 'CPV': 'Africa', 'DJI': 'Africa', 'DZA': 'Africa', 'EGY': 'Africa',
    'ERI': 'Africa', 'ETH': 'Africa', 'GAB': 'Africa', 'GHA': 'Africa', 'GIN': 'Africa',
    'GMB': 'Africa', 'GNB': 'Africa', 'GNQ': 'Africa', 'KEN': 'Africa', 'LBR': 'Africa',
    'LBY': 'Africa', 'LSO': 'Africa', 'MAR': 'Africa', 'MDG': 'Africa', 'MLI': 'Africa',
    'MOZ': 'Africa', 'MRT': 'Africa', 'MUS': 'Africa', 'MWI': 'Africa', 'NAM': 'Africa',
    'NER': 'Africa', 'NGA': 'Africa', 'RWA': 'Africa', 'SDN': 'Africa', 'SEN': 'Africa',
    'SLE': 'Africa', 'SOM': 'Africa', 'SSD': 'Africa', 'STP': 'Africa', 'SWZ': 'Africa',
    'SYC': 'Africa', 'TCD': 'Africa', 'TGO': 'Africa', 'TUN': 'Africa', 'TZA': 'Africa',
    'UGA': 'Africa', 'ZAF': 'Africa', 'ZMB': 'Africa', 'ZWE': 'Africa',
    'AUS': 'Oceania', 'FJI': 'Oceania', 'KIR': 'Oceania', 'MHL': 'Oceania',
    'NRU': 'Oceania', 'NZL': 'Oceania', 'PLW': 'Oceania', 'PNG': 'Oceania',
    'SLB': 'Oceania', 'TON': 'Oceania', 'TUV': 'Oceania', 'VUT': 'Oceania',
    'WSM': 'Oceania',
}

UNIT_OPTIONS = ['Trillion ($T)', 'Billion ($B)', 'Million ($M)']
UNIT_DIVISOR = {'Trillion ($T)': 1e12, 'Billion ($B)': 1e9, 'Million ($M)': 1e6}
UNIT_SUFFIX  = {'Trillion ($T)': 'T',  'Billion ($B)': 'B',  'Million ($M)': 'M'}


@st.cache_data
def get_gdp_data():
    DATA_FILENAME = Path(__file__).parent / 'data/gdp_data.csv'
    raw_gdp_df = pd.read_csv(DATA_FILENAME)

    MIN_YEAR = 1960
    MAX_YEAR = 2022

    gdp_df = raw_gdp_df.melt(
        ['Country Name', 'Country Code'],
        [str(x) for x in range(MIN_YEAR, MAX_YEAR + 1)],
        'Year',
        'GDP',
    )

    gdp_df['Year'] = pd.to_numeric(gdp_df['Year'])
    gdp_df['GDP'] = pd.to_numeric(gdp_df['GDP'], errors='coerce')

    return gdp_df


gdp_df = get_gdp_data()

# Build country lookup tables (individual countries only, no World Bank aggregates)
country_meta = (
    gdp_df[['Country Name', 'Country Code']]
    .drop_duplicates()
    .pipe(lambda df: df[df['Country Code'].isin(REGION_MAP)])
    .assign(Region=lambda df: df['Country Code'].map(REGION_MAP))
    .sort_values('Country Name')
)
code_to_name = dict(zip(country_meta['Country Code'], country_meta['Country Name']))
name_to_code = dict(zip(country_meta['Country Name'], country_meta['Country Code']))

# -----------------------------------------------------------------------------
# Page

'''
# :earth_americas: GDP dashboard

Browse GDP data from the [World Bank Open Data](https://data.worldbank.org/) website. As you'll
notice, the data only goes to 2022 right now, and datapoints for certain years are often missing.
But it's otherwise a great (and did I mention _free_?) source of data.
'''

''
''

min_value = int(gdp_df['Year'].min())
max_value = int(gdp_df['Year'].max())

from_year, to_year = st.slider(
    'Which years are you interested in?',
    min_value=min_value,
    max_value=max_value,
    value=[min_value, max_value],
)

unit = st.radio('GDP unit', UNIT_OPTIONS, index=1, horizontal=True)
divisor = UNIT_DIVISOR[unit]
suffix  = UNIT_SUFFIX[unit]

# Region filter → narrows the country list
all_regions = sorted(country_meta['Region'].unique())
selected_regions = st.multiselect('Filter by region', all_regions, all_regions)

available_names = (
    country_meta[country_meta['Region'].isin(selected_regions)]['Country Name']
    .sort_values()
    .tolist()
)

default_names = [n for n in ['Germany', 'France', 'United Kingdom', 'Brazil', 'Mexico', 'Japan']
                 if n in available_names]

selected_names = st.multiselect(
    'Which countries would you like to view?',
    available_names,
    default_names,
)

if not selected_names:
    st.warning('Select at least one country')
    st.stop()

selected_codes = [name_to_code[n] for n in selected_names]

''
''
''

# Filter data
filtered_gdp_df = gdp_df[
    gdp_df['Country Code'].isin(selected_codes)
    & gdp_df['Year'].between(from_year, to_year)
].copy()
filtered_gdp_df['Country Name'] = filtered_gdp_df['Country Code'].map(code_to_name)
filtered_gdp_df[f'GDP ({suffix})'] = filtered_gdp_df['GDP'] / divisor

st.header('GDP over time', divider='gray')

''

st.line_chart(
    filtered_gdp_df,
    x='Year',
    y=f'GDP ({suffix})',
    color='Country Name',
)

''
''

first_year_df = gdp_df[gdp_df['Year'] == from_year]
last_year_df  = gdp_df[gdp_df['Year'] == to_year]

st.header(f'GDP in {to_year}', divider='gray')

''

cols = st.columns(4)

for i, (code, name) in enumerate(zip(selected_codes, selected_names)):
    col = cols[i % len(cols)]

    with col:
        first_rows = first_year_df.loc[first_year_df['Country Code'] == code, 'GDP']
        last_rows  = last_year_df.loc[last_year_df['Country Code']  == code, 'GDP']

        first_gdp = first_rows.iloc[0] / divisor if not first_rows.empty else float('nan')
        last_gdp  = last_rows.iloc[0]  / divisor if not last_rows.empty  else float('nan')

        if pd.isna(first_gdp) or pd.isna(last_gdp):
            growth = 'n/a'
            delta_color = 'off'
        else:
            growth = f'{last_gdp / first_gdp:,.2f}x'
            delta_color = 'normal'

        st.metric(
            label=f'{name} GDP',
            value=f'{last_gdp:,.2f}{suffix}' if not pd.isna(last_gdp) else 'n/a',
            delta=growth,
            delta_color=delta_color,
        )
