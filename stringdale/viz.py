# AUTOGENERATED! DO NOT EDIT! File to edit: ../nbs/001_visualization.ipynb.

# %% auto 0
__all__ = ['logger', 'is_ipython', 'display_in_ipython', 'wrap_text', 'node_description', 'edge_description',
           'graph_to_graphviz_spec', 'check_graphviz_installed', 'draw_graphviz', 'draw_nx']

# %% ../nbs/001_visualization.ipynb 4
from IPython.display import Image, display, HTML,SVG
import networkx as nx
from .core import jinja_render
import os
import shutil
import graphviz
import logging
from textwrap import wrap
logger = logging.getLogger(__name__)


# %% ../nbs/001_visualization.ipynb 6
from IPython.display import Markdown, display


# %% ../nbs/001_visualization.ipynb 7
def is_ipython():
    try:
        from IPython import get_ipython
        return get_ipython() is not None
    except ImportError:
        return False

def display_in_ipython(obj):
    if obj is None:
        return
    if is_ipython():
        display(obj)


# %% ../nbs/001_visualization.ipynb 9
def _attrs_to_str(attrs,drop_keys=None  ):
    if drop_keys is None:
        drop_keys = []
    return '\n'.join([f'{k}={v}' for k,v in attrs.items() if k not in drop_keys])


def wrap_text(text,width=None,**kwargs):
    if width is None or text is None:
        return text
    return '\n'.join(wrap(text,width=width,**kwargs))


def node_description(g,node,label_key=None,drop_keys=None,**kwargs):
    if drop_keys is None:
        drop_keys = []
    if label_key is not None:
        drop_keys.append(label_key)
    
    node_id = node
    node_data = g.nodes[node_id]
    
    node_data_str = _attrs_to_str(node_data,drop_keys=drop_keys)

    if label_key is None:
        node_str = f'{node_id}\n{node_data_str}'
    else:
        node_label = node_data[label_key]
        node_str = f'{node_id}({node_label})\n{node_data_str}'
    return wrap_text(node_str,**kwargs)

def edge_description(g,edge,drop_keys=None,**kwargs):
    edge_id = edge
    edge_data = g.edges[edge_id]
    edge_data_str = _attrs_to_str(edge_data,drop_keys=drop_keys)
    return wrap_text(edge_data_str,**kwargs)


def graph_to_graphviz_spec(g,label_key=None,drop_keys=None,**kwargs):
    node_kwargs = [{
        'name':node, 'label':node_description(g,node,label_key=label_key,drop_keys=drop_keys,**kwargs)
    } for node in g.nodes]
    edge_kwargs = [{
        'tail_name':edge[0], 'head_name':edge[1], 'label':edge_description(g,edge,drop_keys=drop_keys,**kwargs)
    } for edge in g.edges]

    return node_kwargs, edge_kwargs

# %% ../nbs/001_visualization.ipynb 11
def check_graphviz_installed():
    if not shutil.which('dot'):
        logger.warning('graphviz is not installed, cannot draw diagrams')
        return False
    return True

def draw_graphviz(node_data,edge_data,name=None,direction='TB',format='svg',node_attrs=None,edge_attrs=None,graph_attrs=None,**kwargs):

    if not check_graphviz_installed():
        return None
    
    dot = graphviz.Digraph(name, format=format)
    if direction not in ['TB','LR']:
        raise ValueError('directions can only be TB or LR')
    dot.attr(rankdir=direction,label=name,labelloc='t',**graph_attrs)
    for node in node_data:
        merged = node_attrs | node
        merged['label'] = wrap_text(merged['label'],**kwargs)
        dot.node(**merged)
    for edge in edge_data:
        merged = edge_attrs | edge
        merged['label'] = wrap_text(merged['label'],**kwargs)
        dot.edge(**merged)
    return dot


# %% ../nbs/001_visualization.ipynb 12
def draw_nx(g:nx.DiGraph,direction='TB',
    name=None,
    format='svg',
    label_key=None,
    drop_keys=None,
    node_attrs=None,
    edge_attrs=None,
    graph_attrs=None,
    ret_dot=False,
    **kwargs):
    
    node_kwargs, edge_kwargs = graph_to_graphviz_spec(g,label_key=label_key,drop_keys=drop_keys)
    if graph_attrs is None:
        graph_attrs = {}
    if node_attrs is None:
        node_attrs = {}
    if edge_attrs is None:
        edge_attrs = {}

    graph_attrs = {} | graph_attrs
    node_attrs = {'shape':'box','color':'#9370DB','fillcolor':'#ECECFF','style':'filled'} | node_attrs
    edge_attrs = {'color':'black'} | edge_attrs

    dot = draw_graphviz(node_kwargs,
        edge_kwargs,
        name=name,
        direction=direction,
        format=format,
        node_attrs=node_attrs,
        edge_attrs=edge_attrs,
        graph_attrs=graph_attrs,
        **kwargs
        )
    if ret_dot:
        return dot
    else:
        display_in_ipython(dot)
    
    
