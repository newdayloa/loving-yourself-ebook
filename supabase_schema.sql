-- Run this file once in the Supabase SQL Editor.
create extension if not exists pgcrypto;

create table if not exists public.leads (
    id uuid primary key default gen_random_uuid(),
    lead_number text unique not null,
    created_at timestamp with time zone not null default now(),
    name text not null,
    email text not null,
    contact_number text null,
    inspiration text null,
    marketing_consent boolean not null default false,
    source text not null,
    ebook_title text not null,
    download_status text not null default 'Pending'
        check (download_status in ('Pending', 'Downloaded')),
    download_count integer not null default 0 check (download_count >= 0),
    downloaded_at timestamp with time zone null,
    archived boolean not null default false
);

create index if not exists leads_created_at_idx on public.leads (created_at desc);
create index if not exists leads_email_idx on public.leads (lower(email));
create index if not exists leads_archived_idx on public.leads (archived);

-- Only the server-side service-role key used by Streamlit should access this table.
alter table public.leads enable row level security;
revoke all on table public.leads from anon, authenticated;
