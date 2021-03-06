from itertools import combinations
from StringIO import StringIO

from flask import Blueprint, request, send_file
import networkx as nx
from networkx import degree
from networkx.readwrite import json_graph
from apikit import jsonify, arg_int

from aleph import authz
from aleph.views.cache import etag_cache_keygen
from aleph.search import raw_iter
from aleph.search.queries import document_query

blueprint = Blueprint('graph', __name__)


def multigraph_to_weighted(multigraph):
    graph = nx.Graph()
    for id, data in multigraph.nodes_iter(data=True):
        graph.add_node(id, **data)
    for u, v, data in multigraph.edges_iter(data=True):
        w = data['weight']
        if graph.has_edge(u, v):
            graph[u][v]['weight'] += w
        else:
            graph.add_edge(u, v, weight=w)
    for id in multigraph.nodes_iter():
        deg = degree(graph, id, weight='weight')
        graph.node[id]['degree'] = deg
    return graph


def paginate_graph(graph):
    graph.partial = None
    limit = arg_int('limit')
    if limit is None or graph.number_of_nodes() <= limit:
        return graph

    graph.partial = {
        'total': graph.number_of_nodes(),
        'shown': limit
    }
    nodes = sorted(graph.nodes_iter(data=True),
                   key=lambda (id, d): d['degree'],
                   reverse=True)
    for id, data in nodes[limit:]:
        graph.remove_node(id)
    return graph


def generate_graph(args):
    fields = ['id', 'collection', 'entities.id', 'entities.label',
              'entities.category']
    query = document_query(args, fields=fields,
                           sources=authz.authz_sources('read'),
                           lists=authz.authz_lists('read'),
                           facets=False)
    graph = nx.MultiGraph()
    for doc in raw_iter(query):
        entities = set()
        for entity in doc.get('_source').get('entities', []):
            if not graph.has_node(entity.get('id')):
                graph.add_node(entity.get('id'),
                               label=entity.get('label'),
                               category=entity.get('category'))
            entities.add(entity.get('id'))
        for (src, dst) in combinations(entities, 2):
            graph.add_edge(src, dst, weight=1)
    graph = multigraph_to_weighted(graph)
    return paginate_graph(graph)


@blueprint.route('/api/1/graph')
def query():
    etag_cache_keygen()
    graph = generate_graph(request.args)
    format = request.args.get('format', '').lower().strip()
    if format == 'gexf':
        sio = StringIO()
        nx.write_gexf(graph, sio)
        sio.seek(0)
        return send_file(sio, mimetype='application/xml')
    else:
        data = json_graph.node_link_data(graph)
        data['partial'] = graph.partial
        return jsonify(data)
