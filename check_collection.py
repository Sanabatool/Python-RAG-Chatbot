from services.vector_store import collection


print("\n========== COLLECTION CHECK ==========")

total = collection.count()

print("Total stored chunks:", total)

if total == 0:
    print("❌ ChromaDB collection is empty.")

else:

    results = collection.get(
        include=[
            "documents",
            "metadatas"
        ]
    )

    documents = results.get("documents", [])
    metadatas = results.get("metadatas", [])

    hci_count = 0

    for index, metadata in enumerate(metadatas):

        if metadata.get("source") == "hci_book":

            hci_count += 1

            print("\n========== HCI CHUNK ==========")
            print("Metadata:", metadata)
            print("Text:")
            print(documents[index][:1000])

    print("\nTotal HCI chunks:", hci_count)