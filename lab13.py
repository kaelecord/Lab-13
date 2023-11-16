# -*- coding: utf-8 -*-
"""
Created on Thu Nov 16 14:25:26 2023

@author: kaele
"""

import pandas as pd
import plotly.graph_objects as go
import networkx as nx
from ast import literal_eval
import streamlit as st

full_data = pd.read_csv('data/friends_transcript_data.csv')
speaker = pd.read_csv('data/speaker_cleaned_data.csv')
char_net = pd.read_csv('data/character_network_cleaned_data.csv')

def create_network_dict(df):
    speakers = set(df['speaker'])
    outer_dict = {key: {} for key in speakers}
    for i in range(len(df['speaker'])):
        for key in set(literal_eval(df['character_entities'][i])):
            if key not in outer_dict[df['speaker'][i]]:
                outer_dict[df['speaker'][i]][key] = list(literal_eval(df['character_entities'][i])).count(key)
            else:
                outer_dict[df['speaker'][i]][key] += list(literal_eval(df['character_entities'][i])).count(key)
    return outer_dict

def create_network_df(network_dict):
    restructured_data = [(outer_key, inner_key, value)
                     for outer_key, inner_dict in network_dict.items()
                     for inner_key, value in inner_dict.items()]
    df = pd.DataFrame(restructured_data, columns=['Source', 'Target', 'Value'])
    return df

def create_network(df, highlight_chars):
    G = nx.from_pandas_edgelist(df, 'Source', 'Target', 'Value')
    pos = nx.spring_layout(G, k= 0.5, iterations = 25)
    degree_centrality = nx.degree_centrality(G)
    
    # Extract node and edge positions
    node_x = [pos[node][0] for node in G.nodes()]
    node_y = [pos[node][1] for node in G.nodes()]
    edge_x = []
    edge_y = []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    node_text = [f"{node, round(degree_centrality[node],3)}" for node in G.nodes()]

    # Create nodes trace
    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode='markers',
        hoverinfo='text',
        hovertext = node_text,
        marker=dict(
            showscale=False,
            colorscale='YlGnBu',
            color = ['red' if node in highlight_chars else 'black' for node in G.nodes()],
            size=[15 if node in highlight_chars else 10 for node in G.nodes()],
            colorbar=dict(
                thickness=15,
                title='Node Connections',
                xanchor='left',
                titleside='right'
            )
        )
    )

    # Create edges trace
    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        mode='lines',
        line=dict(width=1, color='gray'),
        hoverinfo='text'
    )
    # Create figure
    fig = go.Figure(data=[edge_trace, node_trace],
                 layout=go.Layout(
                    showlegend=False,
                    hovermode='closest',
                    margin=dict(b=0, l=0, r=0, t=0),
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)))

    # Show figure
    return fig

def generate_network(season, episode, characters):
    if season == "ALL" and episode == "ALL":
        df = char_net
    elif season != "ALL" and episode == "ALL":
        df = char_net[char_net['season_id'] == season]
    elif season == "ALL" and episode != "ALL":
        df = char_net[char_net['episode_id'] == episode]
    else:
        df = char_net[(char_net['season_id'] == season) & (char_net['episode_id'] == episode)]
    network_dict = create_network_dict(df)
    network_df = create_network_df(network_dict)
    fig = create_network(network_df, characters)
    return fig

def generate_network_df(season, episode, characters):
    if season == "ALL" and episode == "ALL":
        df = char_net
    elif season != "ALL" and episode == "ALL":
        df = char_net[char_net['season_id'] == season]
    elif season == "ALL" and episode != "ALL":
        df = char_net[char_net['episode_id'] == episode]
    else:
        df = char_net[(char_net['season_id'] == season) & (char_net['episode_id'] == episode)]
    network_dict = create_network_dict(df)
    network_df = create_network_df(network_dict)
    return network_df

def get_seasons():
    season_ = list(full_data['season_id'].unique())
    season_.insert(0,"ALL")
    return season_

def get_episodes(season = 'ALL'):
    if season == "ALL":
        episode_ = list(full_data['episode_id'].unique())
    else:
        episode_ = list(full_data['episode_id'][full_data['season_id'] == season].unique())
    episode_.insert(0,"ALL")
    return episode_

def get_speakers(season, episode):
    if season == "ALL" and episode == "ALL":
        temp = speaker.groupby(['speaker']).agg({'speaker': ['count']}).reset_index()
        temp.columns = ["".join(col).strip() for col in temp.columns.values]
        temp = temp[temp['speakercount']>10]
        temp = temp.sort_values(['speakercount', 'speaker'], ascending = False).reset_index()
        return list(temp['speaker'])
    elif season != "ALL" and episode == "ALL":
        temp = speaker.groupby(['season_id', 'speaker']).agg({'speaker': ['count']}).reset_index()
        temp.columns = ["".join(col).strip() for col in temp.columns.values]
        temp = temp[(temp['speakercount']>5) & (temp['season_id'] == season)]
        temp = temp.sort_values(['speakercount', 'speaker'], ascending = False).reset_index()
    else:
        temp = speaker.groupby(['season_id','episode_id', 'speaker']).agg({'speaker': ['count']}).reset_index()
        temp.columns = ["".join(col).strip() for col in temp.columns.values]
        temp = temp[(temp['speakercount']>1) & (temp['season_id'] == season) & (temp['episode_id'] == episode)]
        temp = temp.sort_values(['speakercount', 'speaker'], ascending = False).reset_index()
    return list(temp['speaker'])

header = st.container()
exercise1 = st.container()
exercise2 = st.container()

with header:
    st.title("Lab 13 - Kael Ecord 11/16/2023")
    
with exercise1:
    st.header("Exercise 1")
    st.subheader("How are the characters in Friends related?")
    st.write("Let's look at a character network to find out.")
    
    
with exercise2:
    st.header("Exercise 2")
    
    st.subheader("Select an episode or scene to see the character network!")
    col_1, col_2 = st.columns(2)
    season_choice = col_1.selectbox('Season:', options = get_seasons(), index = 1)
    episode_choice = col_2.selectbox('Episode:', options = get_episodes(season=season_choice), index = 0)
    st.write("Select Characters you want to know more about (this will highlight them in the below network)")
    character_choice = st.multiselect('Character:', options= get_speakers(season_choice, episode_choice))
    st.write(generate_network(season_choice, episode_choice, character_choice))
    
    st.write("Network built on the following data")
    st.dataframe(generate_network_df(season_choice, episode_choice, character_choice), use_container_width= True)
    
