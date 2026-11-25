# Document Update Runbook

**When to run:** A source document has changed and the updated content needs to be reflected in retrieval and answer generation.

## Steps

### 1. Add the updated document

Place the updated PDF inside:

`Week10/data/corpus/`

### 2. Run the document update script

From the Week10 project directory, execute:

```bash
python -m scripts.update_document data/corpus/<filename>.pdf
```

The script performs the following operations:

- Extracts text from the PDF.
- Tombstones the old chunks by setting `deleted_at`.
- Splits the updated document into chunks.
- Applies the Week 8 PII scrubbing and metadata enrichment helpers.
- Generates embeddings for the new chunks.
- Inserts the new chunks into Qdrant.
- Clears the semantic cache.

### 3. Verify the updated content

Choose a question that should be answered using the updated document.

Run:

```bash
python -c "from src.rag.qdrant_rag import ask_rag; print(ask_rag('<relevant question>')['answer'])"
```

Check whether the answer reflects the updated document.

### 4. Optionally bump the knowledge-base version

For a major knowledge-base update:

- Open `src/rag/pipeline.py`.
- Update the `KB_VERSION` value.
- New chunks ingested after the change will carry the new version.

### 5. Log the update

Record the update in:

`docs/kb-changelog.md`

Include:

- Date of update.
- Updated document filename.
- Number of old chunks tombstoned.
- Number of new chunks ingested.
- Number of cache entries cleared.

## Rollback

If an update needs to be rolled back:

1. Un-tombstone the old chunks by removing their `deleted_at` payload field.
2. Delete the newly inserted chunks using their point IDs.
3. Clear the semantic cache again.

**Important:** Record the old and new point IDs before attempting rollback. Do not delete chunks based only on the source filename, because that could also remove the historical chunks you want to restore.