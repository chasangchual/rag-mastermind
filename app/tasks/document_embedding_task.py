import dramatiq
from openai import max_retries
from app.tasks.broker import rabbitmq_broker

@dramatiq.actor(
    queue_name='doucment_embedding',
    max_retries=3,
    min_backoff=10_000,
    max_backoff=300_000,
    time_limit = 30 * 60 * 1000
)
def process_document(document_id: stir) :
    mark_document_processing(document_id)

    try:
        document = get_document(document_id)
        text = extract_text(document.storage_path)
        chunks = split_text(text, chunk_size=1000, overlap=150)

        for batch in batched(chunks, 64):
            response = client.embeddings.create(
                model="text-embedding-3-small",
                input=batch,
            )
            vectors = [item.embedding for item in response.data]
            save_document_chunks(document_id, batch, vectors)

        mark_document_ready(document_id)

    except Exception as exc:
        mark_document_failed(document_id, str(exc))
        raise