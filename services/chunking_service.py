from langchain_text_splitters import RecursiveCharacterTextSplitter

splitter = RecursiveCharacterTextSplitter(

    chunk_size=400,

    chunk_overlap=50,

    separators=[
        "\n\n",
        "\n",
        ". ",
        " ",
        ""
    ]

)


def chunk_text(text):
    """
    Split text into smart overlapping chunks.
    """

    return splitter.split_text(text)