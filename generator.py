import os
import numpy as np
import json
from gcn_flc.datautils import gurobi_solver, visualize
from gcn_flc.graphutils import graph_generation, vis_graph, save_graph
from matplotlib import pyplot as plt
import argparse
import datetime
import pdb
parser = argparse.ArgumentParser(description='data generator')
parser.add_argument('--config', dest='config', default='config.json',
                    help='hyperparameters')

def load_config(config_path):
    assert(os.path.exists(config_path))
    cfg = json.load(open(config_path, 'r'))
    return cfg
def generate_data(cfg):
    """
    Generate random samples
    Args: 
    cfg: configuration
    cfg.keys():
        total_nodes: total nodes of the graph, must equal GCN input dim
        facility_num: range of facility number
        world_size: Euclidean world grid size
        random_seed: random seed for generating a batch of training data
        sample_num: number of samples to generate
        facility_cost: range of facility opening cost
        travel_cost: the cost per euclidean distance from client to facility
    Return:
    data: list of dictionaries
    data[i].keys():
        clients: [N,2] list
        facilitis: [M,2] list
        charge: [M] list
        alpha: scalar
        x: [M] binary array, 1 if open this facility
        y: [N] scalar array, y[i] is the connected facility index
        d: [N,M] distance array, d[i,j] is the distance from i to j
    """
    np.random.seed(cfg['random_seed'])
    data = []
    for s in range(cfg['sample_num']):
        f_num = np.random.randint(cfg['facility_num'][0],
                                  cfg['facility_num'][1])
        facilities = list(map(list, 
                           list(zip(np.random.rand(f_num)*cfg['world_size'][0],
                                    np.random.rand(f_num)*cfg['world_size'][1]))))   
        charge = np.random.randint(cfg['facility_cost'][0],
                                   cfg['facility_cost'][1], f_num).tolist()
        c_num = cfg['total_nodes'] - f_num
        clients = list(map(list, 
                           list(zip(np.random.rand(c_num)*cfg['world_size'][0],
                                    np.random.rand(c_num)*cfg['world_size'][1]))))
        alpha = cfg['travel_cost']   

        _,_,gen_graph = graph_generation(np.array(facilities),np.array(clients))
        graph_dict = save_graph(gen_graph, f_num, c_num)
        # # visulize the graph
        # nodes = np.concatenate((np.array(facilities),np.array(clients)),axis = 0)
        # vis_graph(nodes,gen_graph,f_num,c_num)
        # plt.show()
        
        data.append({
            'clients': clients,
            'facilities': facilities,
            'charge': charge,
            'alpha': alpha,
            'graph_dict':graph_dict
        })
        x, y, d = gurobi_solver(data[s])
        data[s]['x'] = x
        data[s]['y'] = y
        data[s]['d'] = d.tolist()

    return data

def savedata(data, cfg, name=None,data_dir = 'dataset/synthetic'):
    """
    Data will be saved in json format
    save the configuration and data both
    in the json file.
    """
    s_data = {'cfg':cfg, 'data':{}}
    if not name:
        now = datetime.datetime.now()
        name = 'dataset-%02d-%02d.json' % (now.day, now.month)
    
    for s in range(len(data)):
        with open(os.path.join(data_dir,name), 'w') as fp:
            fp.write(json.dumps(data[s], indent=2))
        # raise NotImplementedError

# def convert_graph(data):
#     """ Convert data to graph structure
#     """
#     raise NotImplementedError


def main():
    global args
    args = parser.parse_args()
    cfg = load_config(args.config)['data']
    data = generate_data(cfg)
    for i in data:
        fig = visualize(i, i['x'], i['y'], False)
        fig.show()
        input('any key to continue')
        fig.clear()
    savedata(data, cfg)



if __name__ == '__main__':
    main()
