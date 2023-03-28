from biocypher import BioCypher
from meta_graph.adapters.adapter import (
    BioCypherMetaAdapter,
    BioCypherMetaAdapterNodeType,
    BioCypherMetaAdapterEdgeType,
    BioCypherMetaAdapterIssueField,
)

# Instantiate the BioCypher interface
# You can use `config/biocypher_config.yaml` to configure the framework or
# supply settings via parameters below
bc = BioCypher()

# Take a look at the ontology structure of the KG according to the schema
bc._get_ontology()
bc.show_ontology_structure()

# Choose node types to include in the knowledge graph.
# These are defined in the adapter (`adapter.py`).
node_types = [
    BioCypherMetaAdapterNodeType.ISSUE,
]

# Choose protein adapter fields to include in the knowledge graph.
# These are defined in the adapter (`adapter.py`).
node_fields = [
    # Issues
    BioCypherMetaAdapterIssueField.NUMBER,
    BioCypherMetaAdapterIssueField.TITLE,
    BioCypherMetaAdapterIssueField.BODY,
]

edge_types = [
    BioCypherMetaAdapterEdgeType.PART_OF,
]

# Create a protein adapter instance
adapter = BioCypherMetaAdapter(
    node_types=node_types,
    node_fields=node_fields,
    edge_types=edge_types,
    # we can leave edge fields empty, defaulting to all fields in the adapter
)


# Create a knowledge graph from the adapter
bc.write_nodes(adapter.get_nodes())
bc.write_edges(adapter.get_edges())

# Write admin import statement
bc.write_import_call()

# Check output
bc.log_duplicates()
bc.log_missing_bl_types()
