from Bio import SeqIO
import Bio
from collections import defaultdict
from graphviz import Digraph


class Vertex:

    def __init__(self, seq):
        self.seq = seq
        self.coverage = 1
        self.in_edges = {}
        self.out_edges = {}

    def increase_coverage(self):
        self.coverage += 1


class Edge:

    def __init__(self, k1, k2):
        self.seq = k1 + k2[-1]
        self.n = 2
        self.coverage = 0

    def increase_length(self):
        self.length += 1

    def calc_coverage(self, c1, c2):
        self.coverage = (c1 + c2) / 2


class Graph:

    def __init__(self, k):
        self.vertices = {}
        self.k = k

    def add_read(self, read):
        read_lng = len(read)
        if read_lng < self.k:
            return

        # first k-mer
        kmer = read[:k]
        if kmer in self.vertices:
            self.vertices[kmer].increase_coverage()
        else:
            self.vertices[kmer] = Vertex(kmer)

        # next k-mer
        for next_kmer_indx in range(1, read_lng - k + 1, 1):
            next_kmer = read[next_kmer_indx:(next_kmer_indx + k)]
            if next_kmer in self.vertices:
                self.vertices[next_kmer].increase_coverage()
            else:
                self.vertices[next_kmer] = Vertex(next_kmer)

            # new edge
            new_edge = Edge(kmer, next_kmer)

            # vertices
            self.vertices[next_kmer].in_edges[kmer] = [new_edge]
            self.vertices[kmer].out_edges[next_kmer] = [new_edge]

            kmer = next_kmer

    def calc_init_edge_coverage(self):

        for current_vertex in self.vertices.keys():
            for next_vertex in self.vertices[current_vertex].out_edges.keys():
                self.vertices[current_vertex].out_edges[next_vertex][0].calc_coverage(
                    self.vertices[current_vertex].coverage, self.vertices[next_vertex].coverage)



    def graph_vis(self, status):

        graph_deb = Digraph(comment='De_Bruin_graph_viz')

        if status == 'f': #full
            for vert in self.vertices.keys():
                graph_deb.node(self.vertices[vert].seq)
                for edge in self.vertices[vert].out_edges.keys():
                    edge_label = self.vertices[vert].out_edges[edge][0].seq
                    graph_deb.edge(vert, edge, label=edge_label)
        else: #cut
            for vert in self.vertices.keys():
                graph_deb.node(self.vertices[vert].seq, str(self.vertices[vert].coverage))
                for edge in self.vertices[vert].out_edges.keys():
                    edge_label = str(self.vertices[vert].out_edges[edge][0].coverage)
                    graph_deb.edge(vert, edge, label=edge_label)

        print(graph_deb)
        print(graph_deb.source)
        graph_deb.view()
        graph_deb.save()




if __name__ == '__main__':

    dataset = '/Users/mitya/Desktop/Klopa/python/hw_4_5_dataset.fasta'

    k = 3

    my_graph = Graph(k)

    with open(dataset, "r") as handle:
        for record in SeqIO.parse(handle, "fasta"):
            read = str(record.seq)
            my_graph.add_read(read)
    #            my_graph.add_read( str(record.reverse_complement().seq) )

    my_graph.calc_init_edge_coverage()

    for v in my_graph.vertices:
        print('Vertex: {}, coverage: {}'.format(v, my_graph.vertices[v].coverage))
        for e in my_graph.vertices[v].out_edges:
            print('-> Out edge: {}'.format(e))
        for e in my_graph.vertices[v].in_edges:
            print('-> In edge: {}'.format(e))

    my_graph.graph_vis(status='f')

    #default is cut, for full: status='f'