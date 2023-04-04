# BioCypher meta-graph
Information about pipelines and adapters available in BioCypher, as described on
the GitHub Projects board for 
[Components](https://github.com/orgs/biocypher/projects/3). Uses the GitHub API
adapter to populate the graph and mount it on localhost:7474 using the Neo4j
docker container. To run locally, you will need to have Docker installed and
running. Then, you can run it using:

```
git clone https://github.com/biocypher/meta-graph.git
cd meta-graph
docker compose up
```

After the graph has been built, you can access it in the Neo4j Browser at
http://localhost:7474. This version of the meta-graph is a read-only instance,
so you will not be able to make changes to the graph. Authentication is not
required. To see the entire graph, you can run the following Cypher query:

```
MATCH (n) RETURN n
```