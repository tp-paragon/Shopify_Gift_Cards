from gql import gql
from graphql.language.ast import DocumentNode

def get_gql_op(file_name: str) -> DocumentNode:
    with open(f"./GraphQL_Operations/{file_name}.gql") as file:
        return gql(file.read())