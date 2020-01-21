import os
import sys
import time
import warnings
import argparse
import scipy as sp
import numpy as np
from cluster_information import Clustering
from sklearn.preprocessing import MinMaxScaler, MultiLabelBinarizer
from sklearn.metrics import  pairwise_distances, normalized_mutual_info_score, adjusted_rand_score, accuracy_score

def load_labels(filename, pathto="./data/IN/", header=0):
    labels = []
    with open(pathto+filename, 'r', encoding=self.encoding) as fh:
        while header > 0:
            var = fh.readline()
            header = header - 1
        docs = fh.read()
        labels = [n for n in docs.split("\n")]
    return labels

def load_matrix(filename, fformat, pathto="./data/IN/", fsep=" ", header=1):
    data = []
    if fformat == "mat":
        with open(pathto+filename, 'r') as fh:
            while header > 0:
                header = header - 1
            docs = fh.read()
            try:
                data = np.array([[float(l) for l in line.split(fsep)] for line in docs.split("\n") if line != ""])
            except Exception as err:
                print("[Error] Data I/O problems. "+str(err))
        return data
    elif fformat == "mtx":
        with open(pathto+filename, 'r') as fh:
            head = []
            while header > 0:
                head.append(fh.readline())
                header = header - 1
            docid = head[-1]
            docs = fh.read()
            try:
                data = np.zeros((int(docid.split(fsep)[0])+1, int(docid.split(fsep)[1])+1))
                for n in docs.split("\n"):
                    if n != "":
                        id1, id2, n = n.split(fsep)
                        data[int(id1), int(id2)] = float(n)
            except Exception as err:
                print("[Error] Data I/O problems. "+str(err))
        return data
    else: 
        print("Unexpected File Format.")

"""
Analyze cluster labels to parse cluster_id in max vote labels
"""
def cluster_accuracy(true_labels, clusters):
    labels = np.array([uid for uid, ulab in enumerate(np.unique(true_labels)) for l in true_labels if ulab == l])
    cluster_classes = np.zeros(len(labels))
    for c in np.unique(clusters):
        cltr_id = [sid for sid, cid in enumerate(clusters) if cid == c]
        cltr_labels = labels[cltr_id]
        cltr_class = np.bincount(cltr_labels).argmax()
        for sid in cltr_id:
            cluster_classes[sid] = cltr_class
    return accuracy_score(labels, cluster_classes)

"""
GLOBALS
"""
# Clustering
__ALGORITHMS__ = [ "agglomerative"] # "spectral", "dbscan", "kmeans"


# Optimizer
__OPTIMIZERS__ = [ "gprocess", "dummy", "rdn_forest"] # "exhaustive"



# Internal Clustering Validation Measures
__VALIDATION_MEASURES__ = ["size_avg", "silhouette", "mean_pairwise", "ch_score", "db_score"]

# Distance Affinity Metrics
"""
Warnning:
- The following metrics are simetric to other traditional distances : "cityblock", "l1", "l2"
- The following metrics are weighted and not addapted on system recognition format : "yule", "wminkowski".
"""
__METRICS__ = [dist for dist in pairwise_distances.__globals__["_VALID_METRICS"]]
# "davies_bouldin", "calinski_harabaz", "mean_centroid", "max_centroid"

"""
External Clustering Validation Measures
"""
__VALIDATION_MEASURES__ =["ARI", "NMI", "CA"]
#"nmi", "ari", "max_pairwise","min_pairwise"

def main()
    parser = argparse.ArgumentParser(usage="%(prog)s [options] <dataset>", description="Clustering optimization by distance metrics and internal validity indexes.")
    parser.add_argument("dataset", help="Dataset folder.")
    parser.add_argument("-i", "--pathin", type=str, dest=dbinput, default="./data/input/", help="Dataset path location.")
    parser.add_argument("-o", "--pathout", type=str, dest=dboutput, default="./data/output/", help="Dataset results output.")
    parser.add_argument("-l", "--labels", type=str, dest=dblabels, default="", help="Dataset single column labels. Default : None")
    parser.add_argument("-h", "--header", type=int, dest=header_size, default=0, help="Dataset files header size. Default : 0.")
    parser.add_argument("-f", "--format", type=str, dest=dbformat, default="mtx", help="Dataset input format. [Matrix Market (mtx), Dense Matrix (mat)]. Default : 'mtx'.")
    parser.add_argument("-d", "--distance", type=str, dest=distance_metric, default="euclidean", help="Distance metric for samples' affinity evaluation \n"+"\t-".join(__METRICS__))
    # Distance matrix not supported in this version
    parser.add_argument("-a", "--algorithm", type=str, dest=algorithm, default="agglomerative", help="Clustering algorithm. Default ': agglomerative. '. \n"+"-".join(__ALGORITHMS__))
    # Algorithms' choice not supported in this version
    parser.add_argument("-t", "--optimizer", type=str, dest=optimizer, default="gprocess", help="Optimizer algorithm. Default : 'gprocess'. \n"+"-".join(__OPTIMIZERS__))
    parser.add_argument("-e", "--evaluation", type=str, dest=evaluation, default="silhouette", help="Optimization measure using Clustering Internal Validity Indexes. Default : 'silhouette'. \n"+"-".join(__VALIDATION_MEASURES__))
    args = parser.parse_args()
    
    assert args.dbformat == "mtx" or args.dbformat == "mat", "Invalid matrix format"
    assert args.distance_metric in __METRICS__, "A invalid distance metric was selected"
    assert args.algorithm in __ALGORITHMS__, "This clustering algorithm currently not supported"
    assert args.optimizer in __OPTIMIZERS__, "This optimizer currently not avaliable"
    assert args.evaluation in __VALIDATION_MEASURES__, "Internal Validity Index not found."
    assert args.dbinput != "" and args.dboutput != "", "Insert a valid input and output folder."

    if args.distance_metric in ["yule", "wminkowski"]:
        print("[Warning] This metric was not suited for the modelling process and may not work.")
    if args.distance_metric in ["cityblock", "l1", "l2"]:
        print("[Warning] This metric is symmetric to other avaliable distance, ensure the test consistency.")

    data = []
    if os.stat(args.dbinput+args.dataset):
        print("[Process] Loading dataset.")
        data = load_matrix(args.dataset, args.dbformat, pathto=args.dbinput, header=args.header_size)

    labels = []
    if args.dblabels != "":
        if os.stat(args.dbinput+args.dblabels):
            print("[Process] Loading data labels.")
            labels = load_labels(args.dblabels, pathto=args.dbinput, header=args.header_size)

    # Check libraries' warnings
    # with warnings.catch_warnings():
    #     warnings.simplefilter("ignore")

    if data == []:
        print("[Error] Load data fails.")
    else:
        print("[Process] Generating distance matrix")
        distance_mtx = pairwise_distances(data_, metric=metric_, n_jobs=None)

        
        print("[Process] Generating Clustering module.")
        start_time = time.time()

        timer = 0.
        clabels = []
        clstr = None

        evi_nmi = -1.0
        evi_ari = -1.0
        evi_ca = -1.0
        ivi_ss = -1.0
        ivi_db = -1.0
        ivi_ch = -1.0
        ivi_pm = -1.0

        try:
            clstr = Clustering(
                args.dataset, args.dbinput, args.dboutput, metric_ = metric,
                algorithm_ = args.algorithm, distance_=distance_mtx, optimization_ = args.evaluation,
                method_ = args.optimizer, labels_=labels
            )
            print("[Process] Starting Clustering.")
            clabels, k_tests = clstr.cluster_analysis()
            print("[Process] Evaluating Clusters.")
            timer = (time.time() - start_time) / 60

            ivi_ss = clstr.__silhouette__(np.array(clabels))
            ivi_ch = clstr.__davies_bouldin__(np.array(clabels))
            ivi_db = clstr.__calinski_harabaz__(np.array(clabels))
            ivi_pm = clstr.__pairwise_distance_mean__(np.array(clabels))
            if len(labels) > 0 and len(labels) == len(clabels):
                evi_ari = adjusted_rand_score(labels, clabels)
                evi_nmi = normalized_mutual_info_score(labels, clabels)
                evi_ca = cluster_accuracy(labels, clabels)
            print("[Process] Writing results.")
        metrics = [evi_nmi, evi_ari, evi_ca, ivi_ss, ivi_db, ivi_ch, ivi_pm]
        with open(args.dboutput+"clusters.csv", "a") as out:
            out.write(" ".join([str(c) for c in clabels]))
    except Exception as err:
        print("[Error] "+str(err))
        with open(args.dboutput+"exceptions.csv", "a") as out:
            out.write(args.dataset+"\t"+str(timer)+"\t"+"\t".join([args.metric, args.algorithm, args.evaluation, args.optimizer])
                +"\t"+str(err).replace("\n","\t")
                +"\n")

    else:
        with open(args.dboutput+"exec.csv", "a") as run:
            run.write(args.dataset+"\t"+str(timer)+"\t"+"\t".join([args.metric, args.algorithm, args.evaluation, args.optimizer])
                +"\t"+str(k_tests)
                +"\t"+":".join([str(len(np.where(clabels == l)[0])) for l in np.unique(clabels)])
                +"\n")

    print("[Process] Done!")

if __name__=="__main__":
    main()