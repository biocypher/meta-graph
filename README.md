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

After the graph has been built, you can access it at http://localhost:7474. The
default username and password are `neo4j` and `neo4jpassword`; they can be 
changed in the `docker-variables.env` file.  Please note that the graph is
created in the `docker` database, not the default `neo4j` database, so you need
to switch to the `docker` database the first time you log in.

We will make an online version of the graph available soon.