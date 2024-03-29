import argparse
import numpy as np
from sklearn.datasets import make_blobs
import utils
from spectral_clustering import spectral_clustering
from kmeans_pp import k_means_pp
import mykmeanssp as kmns

MAX_CAP_N_3D = 340
MAX_CAP_K_3D = 20
MAX_CAP_N_2D = 350
MAX_CAP_K_2D = 20

'''
Main module of program.
Program computes ond compares Kmeans clustering vs. Spectral clustering for variables given by user.

Max capacity for n and k are the values for which the program does not a accede running time of 5 minutes on nova
    for 2D vectors: n = 350, k = 20
    for 3D vectors: n = 340, k = 20
    
arguments:
n - # of vectors
k - # of clusters
random - inverse flag, if not used program will choose k and n at random from the respective range [max_cap//2: max_cap]

output:
data.txt - contains the data generated randomly
    each line represents a vector of 2 or 3 dim. the last digit represents the cluster it originally belongs to.
clusters.txt - contains the clusters computed by the different algorithms
    first line is the number of clusters (k) calculated by the Spectral clustering algorithm
    next k lines, each represent a cluster calculated by the Spectral clustering algorithm, vectors are mentioned 
        using their index in the data file
    next k lines are the same, but for the K-means algorithm
'''


# argument assertion function
def assert_args(n, k):
    flag = False
    if k >= n:
        print("# of clusters must be smaller than # of points")
        flag = True
    if k <= 0:
        print("# of clusters must be a positive non-zero number")
        flag = True
    if n <= 0:
        print("# of points must be a positive non-zero number")
        flag = True
    return flag


def main(n, k, random):
    d = np.random.choice((2, 3))
    if random:  # values for k & n are chosen at random from range [max_capacity/2, max_capacity]
        max_k = MAX_CAP_K_3D if d == 3 else MAX_CAP_K_2D
        max_n = MAX_CAP_N_3D if d == 3 else MAX_CAP_N_2D
        k = np.random.randint(max_k // 2, max_k + 1)
        n = np.random.randint(max_n // 2, max_n + 1)

    # checking the arguments
    if assert_args(n, k):
        return

    # Print max capacity
    print(f"max capacity of k : 2D {MAX_CAP_K_2D}  3D {MAX_CAP_K_3D}\n"
          f"max capacity of n : 2D {MAX_CAP_N_2D}  3D {MAX_CAP_N_3D}\n")

    # Generate random data with indexed data points
    vectors, clusters = make_blobs(n_samples=n, n_features=d, centers=k)
    vectors, clusters = vectors.astype(np.float32), clusters.astype(np.int32)
    # Create 1st txt file and save randomized data
    utils.save_data(vectors, clusters, d)

    # Run Spectral Clustering
    s_clstr_to_vec, s_vec_to_clstr, obs_k = spectral_clustering(vectors, n, k=-1 if random else k)

    # Run K_means
    k_clstr_to_vec, k_vec_to_clstr = k_means_pp(vectors, obs_k, d, n, 300)

    # Create 2nd txt file with clusters from both algorithms
    utils.write_to_file(s_clstr_to_vec, k_clstr_to_vec, obs_k)

    # Calculate Jaccard measure
    temp = clusters.tolist()
    sjm = kmns.jaccard(temp, s_vec_to_clstr)
    kjm = kmns.jaccard(temp, k_vec_to_clstr)

    # Create pdf file
    utils.save_to_pdf(vectors, s_vec_to_clstr, k_vec_to_clstr, d, k, n, obs_k, sjm, kjm)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('n', type=int, help="# of vectors")
    parser.add_argument('k', type=int, help="# of clusters")
    parser.add_argument('--Random', help="random k and n", default=False, action='store_true')
    args = parser.parse_args()
    main(args.n, args.k, args.Random)
