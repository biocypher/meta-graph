import random
import requests
import gzip
import json
import string
from enum import Enum, auto
from itertools import chain
from biocypher._logger import logger

logger.debug(f"Loading module {__name__}.")


class BioCypherMetaAdapterNodeType(Enum):
    """
    Define types of nodes the adapter can provide.
    """

    ISSUE = auto()


class BioCypherMetaAdapterIssueField(Enum):
    """
    Define possible fields the adapter can provide for proteins.
    """

    NUMBER = "number"
    TITLE = "title"
    BODY = "body"


class BioCypherMetaAdapterEdgeType(Enum):
    """
    Enum for the types of the protein adapter.
    """

    PART_OF = "part_of"


class BioCypherMetaAdapter:
    """
    Example BioCypher adapter. Generates nodes and edges for creating a
    knowledge graph.

    Args:
        node_types: List of node types to include in the result.
        node_fields: List of node fields to include in the result.
        edge_types: List of edge types to include in the result.
        edge_fields: List of edge fields to include in the result.
    """

    def __init__(
        self,
        node_types: str = None,
        node_fields: str = None,
        edge_types: str = None,
        edge_fields: str = None,
    ):
        self._set_types_and_fields(
            node_types, node_fields, edge_types, edge_fields
        )

        self._download_data()
        self._edges = self._process_edges()
        self._nodes = self._process_nodes()

    def get_nodes(self) -> list:
        """
        Returns a list of node tuples for node types specified in the
        adapter constructor.

        Returns:
            List of nodes.
        """

        return self._nodes

    def get_edges(self):
        """
        Returns a list of edge tuples for edge types specified in the
        adapter constructor.
        """

        return self._edges

    def _download_data(self):
        """
        Download data from the GitHub project page using the API.
        """

        with gzip.open("config/token.txt.gz", "rt") as f:
            token = f.read()

        # Set the API endpoint and headers
        url = "https://api.github.com/graphql"
        headers = {"Authorization": f"Bearer {token}"}

        # Get the project ID
        id_ = self._get_project_id(url, headers)

        # Get the project fields
        self._fields = self._get_project_fields(url, headers, id_)

        # Get the project items
        self._items = self._get_project_items(url, headers, id_)

    def _get_project_id(self, url: str, headers: dict) -> str:
        query = """
                query{
                    organization(login: "biocypher"){
                        projectV2(number: 3) {
                            id
                        }
                    }
                }
                """

        # Set the request data as a dictionary
        data = {"query": query}

        # Send the API request
        response = requests.post(url, headers=headers, json=data)

        # Parse the response JSON
        response_json = json.loads(response.text)

        # Extract the data from the response JSON
        data = response_json.get("data")
        return data.get("organization").get("projectV2").get("id")

    def _get_project_fields(self, url: str, headers: dict, id_: str) -> dict:
        query = (
            """
                query{
                    node(id: "%s") {
                        ... on ProjectV2 {
                            fields(first: 20) {
                                nodes {
                                    ... on ProjectV2Field {
                                        id
                                        name
                                    }
                                    ... on ProjectV2SingleSelectField {
                                        id
                                        name
                                        options {
                                            id
                                            name
                                        }
                                    }
                                }
                            }
                        }
                    }
                }
                """
            % id_
        )

        # Set the request data as a dictionary
        data = {"query": query}

        # Send the API request
        response = requests.post(url, headers=headers, json=data)

        # Parse the response JSON
        response_json = json.loads(response.text)

        # Extract the data from the response JSON
        data = response_json.get("data")
        return data.get("node").get("fields").get("nodes")

    def _get_project_items(self, url: str, headers: dict, id_: str) -> dict:
        nodes = []

        query = (
            """
                query{
                  node(id: "%s") {
                    ... on ProjectV2 {
                      items(first: 20) {
                        nodes {
                          id
                          fieldValues(first: 100) {
                            nodes {
                              ... on ProjectV2ItemFieldTextValue {
                                text
                                field {
                                  ... on ProjectV2FieldCommon {
                                    name
                                  }
                                }
                              }
                              ... on ProjectV2ItemFieldDateValue {
                                date
                                field {
                                  ... on ProjectV2FieldCommon {
                                    name
                                  }
                                }
                              }
                              ... on ProjectV2ItemFieldSingleSelectValue {
                                name
                                field {
                                  ... on ProjectV2FieldCommon {
                                    name
                                  }
                                }
                              }
                            }
                          }
                          content {
                            ... on Issue {
                              title
                              body
                              number
                            }
                          }
                        }
                        pageInfo {
                          endCursor
                          hasNextPage
                        }
                      }
                    }
                  }
                }
                """
            % id_
        )

        # Set the request data as a dictionary
        data = {"query": query}

        # Send the API request
        response = requests.post(url, headers=headers, json=data)

        # Parse the response JSON
        response_json = json.loads(response.text)

        nodes.extend(
            response_json.get("data").get("node").get("items").get("nodes")
        )

        # Extract the data from the response JSON
        pageInfo = (
            response_json.get("data").get("node").get("items").get("pageInfo")
        )

        while pageInfo.get("hasNextPage"):
            next_query = """
                            query{
                              node(id: "%s") {
                                ... on ProjectV2 {
                                  items(first: 20, after: "%s") {
                                    nodes {
                                      id
                                      fieldValues(first: 100) {
                                        nodes {
                                          ... on ProjectV2ItemFieldTextValue {
                                            text
                                            field {
                                              ... on ProjectV2FieldCommon {
                                                name
                                              }
                                            }
                                          }
                                          ... on ProjectV2ItemFieldDateValue {
                                            date
                                            field {
                                              ... on ProjectV2FieldCommon {
                                                name
                                              }
                                            }
                                          }
                                          ... on ProjectV2ItemFieldSingleSelectValue {
                                            name
                                            field {
                                              ... on ProjectV2FieldCommon {
                                                name
                                              }
                                            }
                                          }
                                        }
                                      }
                                      content {
                                        ... on Issue {
                                          title
                                          body
                                          number
                                        }
                                      }
                                    }
                                    pageInfo {
                                      endCursor
                                      hasNextPage
                                    }
                                  }
                                }
                              }
                            }
                            """ % (
                id_,
                pageInfo.get("endCursor"),
            )

            # Set the request data as a dictionary
            data = {"query": next_query}

            # Send the API request
            response = requests.post(url, headers=headers, json=data)

            # Parse the response JSON
            response_json = json.loads(response.text)

            nodes.extend(
                response_json.get("data").get("node").get("items").get("nodes")
            )

            # Extract the data from the response JSON
            pageInfo = (
                response_json.get("data")
                .get("node")
                .get("items")
                .get("pageInfo")
            )

        return nodes

    def _process_nodes(self):
        """
        Returns a list of node tuples for node types specified in the
        adapter constructor.
        """

        logger.info("Generating nodes.")

        nodes = []

        # Fields
        for field in self._fields:
            if field["name"] not in [
                "Adapter Input Format",
                "Resource Type",
                "Data Type",
            ]:
                continue

            for option in field["options"]:
                name = option["name"].lower()
                type = field["name"].lower()

                nodes.append((name, type, {}))

        # Individual cards
        for item in self._items:
            fields = [
                field
                for field in item.get("fieldValues", {}).get("nodes", [])
                if field
            ]

            title = self._get_title(fields)

            if not title:
                logger.warning(f"Item {item['id']} has no title.")
                continue

            label = self._get_label(fields)
            url = self._extract_url(fields)
            number = "i" + str(item["content"]["number"])

            nodes.append((number, label, {"name": title, "url": url}))

        # Edges to fields
        for item in self._items:
            fields = [
                field
                for field in item.get("fieldValues", {}).get("nodes", [])
                if field
            ]

            number = "i" + str(item["content"]["number"])

            for field in fields:
                if field["field"]["name"] not in [
                    "Adapter Input Format",
                    "Resource Type",
                    "Data Type",
                ]:
                    continue

                self._edges.append(
                    (None, number, field["name"].lower(), "uses", {})
                )

        return nodes

    def _get_title(self, fields):
        """
        Get the title for the node.
        """

        for field in fields:
            if field["field"]["name"] == "Title":
                return field["text"]

        return None

    def _get_label(self, labels):
        """
        Get the label for the node.
        """

        g = t = ""

        for label in labels:
            if label["field"]["name"] == "Component Type":
                t = label["name"]

            if t == "Pipeline":
                return "pipeline"

            if label["field"]["name"] == "Adapter Granularity":
                g = label["name"]

        # to list if not empty
        concat = []
        if g:
            concat.append(g.lower())
        if t:
            concat.append(t.lower())

        concat.append("adapter")

        # concatenate
        return " ".join(concat)

    def _extract_url(self, fields) -> str:
        """
        Extract the URL from the body of the item.
        """

        for field in fields:
            if field["field"]["name"] == "Resource URL":
                return field["text"]

        return None

    def _process_edges(self):
        """
        Returns a list of edge tuples for edge types specified in the
        adapter constructor.
        """

        logger.info("Generating edges.")

        edges = []

        for item in self._items:
            uses = self._extract_uses(item["content"]["body"])

            parent = "i" + str(item["content"]["number"])

            for use in uses:
                if not use:
                    continue

                part = use.replace("#", "i")

                edges.append((None, part, parent, "part of", {}))

        return edges

    def _extract_uses(self, body) -> list:
        """
        Extract the uses from the body of the item.
        """

        if not body:
            return []

        lines = body.split("\n")

        for line in lines:
            if line.startswith("Uses:"):
                uses = line.split(": ")[1]

                return uses.split(" ")

        return []

    def get_node_count(self):
        """
        Returns the number of nodes generated by the adapter.
        """
        return len(self.get_nodes())

    def _set_types_and_fields(
        self, node_types, node_fields, edge_types, edge_fields
    ):
        if node_types:
            self.node_types = node_types
        else:
            self.node_types = [type for type in BioCypherMetaAdapterNodeType]

        if node_fields:
            self.node_fields = node_fields
        else:
            self.node_fields = [
                field
                for field in chain(
                    BioCypherMetaAdapterIssueField,
                )
            ]

        if edge_types:
            self.edge_types = edge_types
        else:
            self.edge_types = [type for type in BioCypherMetaAdapterEdgeType]

        if edge_fields:
            self.edge_fields = edge_fields
        else:
            self.edge_fields = [field for field in chain()]
