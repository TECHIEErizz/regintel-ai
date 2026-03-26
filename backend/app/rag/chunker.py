from langchain_text_splitters import RecursiveCharacterTextSplitter


def chunk_document(text: str):
    """
    Improved semantic chunking for regulatory documents
    """

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,     # bigger chunks = better context
        chunk_overlap=200,
        separators=[
            "\n\n\n",   # section breaks
            "\n\n",     # paragraphs
            "\n",       # lines
            ".",        # sentences
        ]
    )

    return splitter.split_text(text)