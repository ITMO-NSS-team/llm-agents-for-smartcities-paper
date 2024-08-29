from typing import Any, Iterable
import uuid

import chromadb
from langchain_community.vectorstores.chroma import Chroma
from langchain_core.documents import Document


def merge_collections(
    chroma_client: chromadb.HttpClient,
    collection_name_1: str,
    collection_name_2: str,
    new_collection_name: str | None = None,
):
    """
    Merge 2 collections into the 'collection_name_1' if 'new_collection_name' is None,
    otherwise merge 2 collections into the new one with 'new_collection_name' name.
    If any problems with network or DB accessibility will occur, exception are raised

    Args:
        chroma_client (chromadb.HttpClient): The Chroma DB client instance to interact with the database.
        collection_name_1 (str): The name of the first collection.
        collection_name_2 (str): The name of the second collection.
        new_collection_name (str | None): The name of the new collection to create and merge the data into.
                                          If `None`, the merge is done into `collection_name_1`.

    Raises:
        Exception: If there are issues with network connectivity or database accessibility.
    """

    collection_1 = chroma_client.get_collection(name=collection_name_1)
    collection_2 = chroma_client.get_collection(name=collection_name_2)

    docs_1: dict[str, Any] = collection_1.get(
        include=["documents", "metadatas", "embeddings"]
    )
    docs_2: dict[str, Any] = collection_2.get(
        include=["documents", "metadatas", "embeddings"]
    )

    if new_collection_name is None:
        for i in range(len(docs_2["ids"])):
            if docs_2["documents"][i] not in docs_1["documents"]:
                collection_1.add(
                    ids=[str(uuid.uuid4())],
                    metadatas=[docs_2["metadatas"][i]],
                    documents=[docs_2["documents"][i]],
                    embeddings=[docs_2["embeddings"][i]],
                )
        return

    new_collection = chroma_client.create_collection(name=new_collection_name)

    merged_docs = docs_1
    for i in range(len(docs_2["ids"])):
        if docs_2["documents"][i] not in merged_docs["documents"]:
            merged_docs["ids"].append(str(uuid.uuid4()))
            merged_docs["embeddings"].append(docs_2["embeddings"][i])
            merged_docs["metadatas"].append(docs_2["metadatas"][i])
            merged_docs["documents"].append(docs_2["documents"][i])

    for i in range(len(merged_docs["ids"])):
        new_collection.add(
            ids=[str(uuid.uuid4())],
            metadatas=merged_docs["metadatas"][i],
            documents=merged_docs["documents"][i],
        )


def delete_repeats(collection: Chroma) -> None:
    """Remove duplicate documents from a collection.

    Args:
        collection (Chroma): The collection from which duplicate documents will be removed. The collection
            should include fields: 'documents', 'embeddings', 'metadatas'.

    Raises:
        Exception: If there are issues accessing the database or performing deletion operations.
    """

    docs = collection.get(include=["documents", "metadatas", "embeddings"])
    delete_ids = []

    for i in range(len(docs["ids"])):
        if docs["documents"][i] in docs["documents"][:i]:
            delete_ids.append(docs["ids"][i])

    collection.delete(ids=delete_ids)


def get_all_docs_name(collection: Chroma) -> set[str]:
    """Return list of files' name from collection.

    Args:
        collection (Chroma): The collection from which file names will be extracted. The collection should
            include fields: 'documents', 'embeddings', 'metadatas'.

    Returns:
        set[str]: A set of file names extracted from the collection.

    Raises:
        KeyError: If the key 'source' is not present in the metadata of any document in the collection.
    """

    docs: dict[str, Any] = collection.get()

    if "source" not in docs["metadatas"][0].keys():
        raise KeyError("There is no file name, called <source>, in document metadata")

    return set(str(metadata["source"].split("\\")[-1]) for metadata in docs["metadatas"])


def insert_documents(collection: Chroma, docs: Iterable[Document]):
    """Insert only documents whose names aren't in 'collection'

    Args:
        collection (Chroma): The collection to which documents will be added. The collection should include
            fields: 'documents', 'embeddings', 'metadatas'.
        docs (Iterable[Document]): An iterable of documents to be inserted into the collection.

    Raises:
        KeyError: If the key 'source' is missing in the metadata of any document from the collection or the input documents.
    """

    first_element = next(docs)
    if "source" not in first_element.metadata.keys():
        raise KeyError("There is no file name, called <source>, in document metadata")

    existing_docs_name = set(get_all_docs_name(collection))
    new_docs_name = set(
        [str(doc.metadata["source"].split("\\")[-1]) for doc in docs]
        + [str(first_element.metadata["source"].split("\\")[-1])]
    )
    docs_name_for_insert = new_docs_name.difference(existing_docs_name)
    if first_element.metadata["source"].split("\\")[-1] in docs_name_for_insert:
        docs_for_insert = [first_element]
    else:
        docs_for_insert = []
    docs_for_insert += [
        doc
        for doc in docs
        if doc.metadata["source"].split("\\")[-1] in docs_name_for_insert
    ]
    if docs_for_insert:
        collection.add_documents(docs_for_insert)
