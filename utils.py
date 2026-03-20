import autograd.numpy as np
import os

try:
    from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score
    from sklearn.metrics import confusion_matrix
except ImportError:
    roc_auc_score = None
    precision_score = None
    recall_score = None
    f1_score = None
    confusion_matrix = None

from rdkit import Chem
from rdkit.Chem import Draw
import matplotlib.pyplot as plt

try:
    from rdkit.Chem.Draw import DrawingOptions
except ImportError:
    DrawingOptions = None

degrees = [1, 2, 3, 4, 5,6]

def sigmoid(x):
    return 0.5*(np.tanh(x) + 1)

def accuracy(X, Y):
    """
    X: predictions
    Y: targets
    """
    probs = sigmoid(X)
    label_pred = np.where(probs>=0.5, 1, 0)
    
    return sum(label_pred == Y) / len(Y)    
def auc(X, Y):
    if roc_auc_score is None:
        raise ImportError("scikit-learn is required for auc().")
    prob = sigmoid(X)
    Y = np.concatenate(Y.astype(np.int32))
    X = np.concatenate(X)
    auc = roc_auc_score(Y, X)
    return auc

def precision(X, Y):
    if precision_score is None:
        raise ImportError("scikit-learn is required for precision().")
    probs = sigmoid(X)
    label_pred = np.where(probs>=0.5, 1, 0)
    precision = precision_score(Y, label_pred)
    return precision
    
def recall(X, Y):
    if recall_score is None:
        raise ImportError("scikit-learn is required for recall().")
    probs = sigmoid(X)
    label_pred = np.where(probs>=0.5, 1, 0)
    recall = recall_score(Y, label_pred)
    return recall
    
def f1score(X, Y):
    if f1_score is None:
        raise ImportError("scikit-learn is required for f1score().")
    probs = sigmoid(X)
    label_pred = np.where(probs>=0.5, 1, 0)
    f1score = f1_score(Y, label_pred)
    return f1score

def FNR(X, Y):
    if confusion_matrix is None:
        raise ImportError("scikit-learn is required for FNR().")
    probs = sigmoid(X)
    label_pred = np.where(probs>=0.5, 1, 0)
    
    confusion_matrix_all  = confusion_matrix(Y, label_pred)
    fnr = confusion_matrix_all[1][0] / (confusion_matrix_all[1][0] + confusion_matrix_all[1][1])
    return fnr
    
def visualization(substances, pred, inputs, targets, atom_activations_vis, att_prob_vis, model_params):
    os.makedirs("figures", exist_ok=True)
    
    unstable_prob = sigmoid(pred)
    
    def construct_atom_neighbor_list(array_rep):
        atom_neighbour_list = []
        for degree in degrees:
            atom_neighbour_list += [list(neighbours) for neighbours in array_rep['atom_neighbors_'+str(degree)]]
        return atom_neighbour_list
    
    atom_neighbour_list = construct_atom_neighbor_list(substances)
    
    def get_neighborhood_ixs(array_rep, cur_atom_ix, radius):
        # Recursive function to get indices of all atoms in a certain radius.
        if radius == 0:
            return set([cur_atom_ix])
        else:
            cur_set = set([cur_atom_ix])
            for n_ix in atom_neighbour_list[cur_atom_ix]:
                cur_set.update(get_neighborhood_ixs(array_rep, n_ix, radius-1))
            return cur_set
        
    def draw_molecule_with_highlights(filename, smiles, highlight_atoms):
        mol = Chem.MolFromSmiles(smiles)
        if DrawingOptions is not None:
            drawoptions = DrawingOptions()
            drawoptions.selectColor = (255.0/255.0, 0.0/255.0, 0.0/255.0)
            drawoptions.elemDict = {}
            drawoptions.bgColor = None
            fig = Draw.MolToImage(
                mol, highlightAtoms=highlight_atoms, size=(500, 500), options=drawoptions)
        else:
            fig = Draw.MolToImage(mol, highlightAtoms=highlight_atoms, size=(500, 500))
        fig.save(filename, bbox_inches='tight')
        
    for mol_idx in range(att_prob_vis.shape[0]):
        
        # only output those unstable compounds
        if int(targets[mol_idx]) == 0:
            continue
            
        # try, output the high probability compounds
        prob = round(float(unstable_prob[mol_idx]), 3)
        #if prob < 0.95: 
        #    continue
        
        most_act = np.max(att_prob_vis[mol_idx, :, :])
        most_act_atom_fp = np.where(att_prob_vis[mol_idx, :, :] == most_act)
        if len(most_act_atom_fp[0]) <= 1: most_act_atom = np.int(most_act_atom_fp[0])
        else: most_act_atom = np.int(most_act_atom_fp[0][0])
        if len(most_act_atom_fp[1]) <= 1: most_act_fp = np.int(most_act_atom_fp[1])
        else: most_act_fp = np.int(most_act_atom_fp[1][0])

        most_act_atom_idx = substances["rnn_raw_input"][mol_idx, most_act_atom]

        most_act_radii = []
        for radius in range(model_params['fp_depth']):
            most_act_radii.append(atom_activations_vis[radius][most_act_atom_idx, most_act_fp])
        most_act_radii = np.array(most_act_radii)
        #print(most_act_radii)
        most_act_radius = np.int(np.where(most_act_radii == np.max(most_act_radii))[0])
        most_act_radius = np.int(np.where(most_act_radii == np.max(most_act_radii))[0][-1])
        #print(most_act_radius)

        highlight_list_our_ixs = get_neighborhood_ixs(substances, most_act_atom_idx, most_act_radius)
        highlight_list_rdkit = [substances['rdkit_ix'][our_ix] for our_ix in highlight_list_our_ixs]
        draw_molecule_with_highlights(
                    "figures/{0}_{1}.jpg".format(mol_idx, prob),
                    inputs[mol_idx],
                    highlight_atoms=highlight_list_rdkit)
        
        
