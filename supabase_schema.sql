-- Run this in the Supabase SQL editor for your project.
-- Safe to re-run; everything is idempotent.

create extension if not exists vector;

create table if not exists documents (
  id bigserial primary key,
  source text not null,
  chunk_index int not null,
  content text not null,
  embedding vector(1024) not null,
  metadata jsonb default '{}'::jsonb not null,
  created_at timestamptz default now() not null
);

-- Drop the old ivfflat index. ivfflat clusters rows into `lists` cells and
-- queries only search `probes` cells (default 1). With small datasets most
-- cells are empty, so the search returns zero matches. Sequential scan is
-- correct and fast until the table grows large.
drop index if exists documents_embedding_idx;

-- When you have >10k rows, add an HNSW index (no cell-miss failure mode):
--   create index documents_embedding_idx
--     on documents using hnsw (embedding vector_cosine_ops);

create or replace function match_documents(
  query_embedding vector(1024),
  match_count int default 5
) returns table (
  id bigint,
  source text,
  chunk_index int,
  content text,
  similarity float
) language sql stable as $$
  select
    documents.id,
    documents.source,
    documents.chunk_index,
    documents.content,
    1 - (documents.embedding <=> query_embedding) as similarity
  from documents
  order by documents.embedding <=> query_embedding
  limit match_count;
$$;
