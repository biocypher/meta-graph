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
docker compose up -d
```

After the graph has been built, you can access it in the Neo4j Browser at
http://localhost:7474. This version of the meta-graph is a read-only instance,
so you will not be able to make changes to the graph. Authentication is not
required. To see the entire graph, you can run the following Cypher query:

```
MATCH (n) RETURN n
```

## Docker Compose

The docker-compose.yml file is used to build the graph. It uses the three stages
`build`, `import`, and `deploy` to serve the graph from Neo4j. The deploy stage
is necessary because a read-only graph cannot be served from the import stage
container. If you want to locally create a read-write instance, you can simply
change the `docker-compose.yml` file to enable writing by setting
`NEO4J_dbms_databases_default__to__read__only` in the deploy stage to `false`.

There is a simpler, one-stage setup that allows read-write in the 
`simple-docker` branch of this repository.

### Stages

- `build`: Builds the graph from the GitHub API. This stage runs BioCypher and
creates the knowledge graph in the configured build directory (mounted as a
volume to the docker compose).
- `import`: Imports the graph from the build directory into Neo4j. This stage
runs the Neo4j docker container and imports the graph from the build directory
into the Neo4j database. The database is started once and stopped again to
perform first-time setup of Neo4j.
- `deploy`: Serves the graph from Neo4j. This stage runs the Neo4j docker
container (again) and serves the graph from the Neo4j database. The database is
started in read-only mode.
