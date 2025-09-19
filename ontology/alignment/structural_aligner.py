# ontology/alignment/structural_aligner.py
import torch
import torch.nn as nn
from torch_geometric.nn import GCNConv

class StructuralAligner(nn.Module):
    def __init__(self, in_dim, hidden_dim, out_dim):
        super().__init__()
        self.gcn1 = GCNConv(in_dim, hidden_dim)
        self.gcn2 = GCNConv(hidden_dim, out_dim)

    def forward(self, x, edge_index):
        h = self.gcn1(x, edge_index).relu()
        h = self.gcn2(h, edge_index)
        return h

def compute_similarity(h1, h2):
    h1_norm = h1 / h1.norm(dim=1, keepdim=True)
    h2_norm = h2 / h2.norm(dim=1, keepdim=True)
    return torch.mm(h1_norm, h2_norm.t())