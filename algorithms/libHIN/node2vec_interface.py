## this is a simple interface, which runs a node2vec instance in order to obtain an embedding.


def get_n2v_embedding(graph, binary):

    ## construct the embedding and return the binary..
    #./node2vec -i:graph/karate.edgelist -o:emb/karate.emb -l:3 -d:24 -p:0.3 -dr -v

    ## get the graph..
    G = nx.from_scipy_sparse_matrix(graph)
    for e in G.edges():
        if e[0] == e[1]:
            G.remove_edge(e[0],e[0])
    
    if not os.path.exists("tmp"):
        os.makedirs("tmp")

    tmp_graph = "tmp/tmpgraph.edges"
    out_graph = "tmp/tmpgraph.emb"

    number_of_nodes = len(G.nodes())
    number_of_edges = len(G.edges())

    ## n e + for loop..
    f= open(tmp_graph,"w+")
    f.write(str(number_of_nodes)+" "+str(number_of_edges)+"\n")
    for e1,e2 in G.edges(data=True):
        f.write(str(e1)+" "+str(e2)+"\n")
    f.close()

    print("Starting graphlet counts..")
#    call([binary, "5", tmp_graph, out_graph]) to je drugac
    matf = np.loadtxt(out_graph,delimiter=" ")
    call(["rm","-rf","tmp"])
    print("Finished graphlet counting:",matf.shape)
    return matf
