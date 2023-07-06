# About hover labels:
# https://plotly.com/python/hover-text-and-formatting/
# https://plotly.com/python/reference/?_ga=2.135691057.1478852968.1662893046-231659727.1654351901#scatter-hovertemplate
import plotly.graph_objects as go
import numpy as np

color_pattern = {'r': '#ff0000',
                 'g': '#00FF00',
                 'b': '#0000ff',
                 'y': '#ffff00'
                 }

gray_color = '#808080'

import networkx as nx


def draw(G, pos=None, ax=None, title='', **kwds):
    if "with_labels" not in kwds:
        kwds["with_labels"] = "labels" in kwds

    fig = draw_networkx(G, pos=pos, ax=ax, **kwds)
    fig.update_layout(
        title={
                'text': title
        },
        font=dict(
            family="Courier New, monospace",
            size=30
        ),
        xaxis=dict(
            tickfont=dict(size=15)),
        showlegend=False,
        yaxis_visible=False, yaxis_showticklabels=False
        ,
        hoverlabel=dict(
              font=dict(family='Courier New, monospace',
                        size=12)
        )
    )
    return fig


def draw_networkx(G, pos=None, **kwds):
    from inspect import signature

    valid_node_kwds = signature(draw_networkx_nodes).parameters.keys()
    valid_edge_kwds = signature(draw_networkx_edges).parameters.keys()

    node_kwds = {k: v for k, v in kwds.items() if k in valid_node_kwds}
    edge_kwds = {k: v for k, v in kwds.items() if k in valid_edge_kwds}

    if pos is None:
        pos = nx.drawing.spring_layout(G)

    fig = go.Figure()
    fig = draw_networkx_edges(G, pos, fig=fig, **edge_kwds)
    fig = draw_networkx_nodes(G, pos, fig=fig, **node_kwds)
    return fig


def draw_networkx_nodes(
        G,
        pos,
        fig,
        node_size,
        labels,
        nodelist=None,
        node_color="#1f78b4",
):
    if nodelist is None:
        nodelist = list(G)

    xy = np.asarray([pos[v] for v in nodelist])

    customdata = list(labels.values())

    fig.add_scatter(x=xy[:, 0], y=xy[:, 1],
                    mode='markers',
                    customdata=customdata,
                    marker=dict(color=node_color,
                                size=node_size,
                                opacity=1.0),
                    hovertemplate='%{customdata}'
                    )
    return fig


def draw_networkx_edges(
        G,
        pos,
        fig,
        edgelist=None
):
    if edgelist is None:
        edgelist = list(G.edges())

    edge_pos = np.asarray([(pos[e[0]], pos[e[1]]) for e in edgelist])

    line = dict(color=gray_color, width=1)
    for (src, dst) in edge_pos:
        x1, y1 = src
        x2, y2 = dst
        fig.add_scatter(x=[x1, x2], y=[y1, y2],
                        marker=dict(size=0),
                        line=line,
                        hovertext='',
                        hoverinfo='skip',
                        text='xpto')
    return fig
