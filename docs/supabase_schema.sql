create extension if not exists "pgcrypto";

create table if not exists public.user_profiles (
  id uuid primary key references auth.users(id) on delete cascade,
  email text,
  full_name text,
  bar_enrollment text,
  practice_areas text[] not null default array[]::text[],
  location text,
  avatar_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.user_settings (
  user_id uuid primary key references auth.users(id) on delete cascade,
  theme text not null default 'dark',
  language text not null default 'en',
  model_preference text not null default 'nvidia',
  notifications_enabled boolean not null default true,
  temperature numeric not null default 0.3,
  api_base_url text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  constraint user_settings_temperature_check check (temperature >= 0 and temperature <= 1)
);

create table if not exists public.chat_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  title text not null default 'New Consultation',
  summary text,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now()
);

create table if not exists public.chat_messages (
  id uuid primary key default gen_random_uuid(),
  session_id uuid not null references public.chat_sessions(id) on delete cascade,
  role text not null check (role in ('user', 'ai')),
  content text not null,
  citations_json jsonb not null default '[]'::jsonb,
  confidence numeric,
  created_at timestamptz not null default now(),
  constraint chat_messages_confidence_check check (confidence is null or (confidence >= 0 and confidence <= 1))
);

create table if not exists public.uploaded_documents (
  id uuid primary key default gen_random_uuid(),
  user_id uuid not null references auth.users(id) on delete cascade,
  session_id uuid references public.chat_sessions(id) on delete set null,
  file_name text not null,
  file_size text not null,
  detected_type text not null,
  summary text not null,
  storage_path text not null,
  uploaded_at timestamptz not null default now()
);

create index if not exists chat_sessions_user_updated_idx
  on public.chat_sessions(user_id, updated_at desc);

create index if not exists chat_messages_session_created_idx
  on public.chat_messages(session_id, created_at);

create index if not exists uploaded_documents_user_uploaded_idx
  on public.uploaded_documents(user_id, uploaded_at desc);

create or replace function public.set_updated_at()
returns trigger
language plpgsql
as $$
begin
  new.updated_at = now();
  return new;
end;
$$;

drop trigger if exists user_profiles_set_updated_at on public.user_profiles;
create trigger user_profiles_set_updated_at
before update on public.user_profiles
for each row execute function public.set_updated_at();

drop trigger if exists user_settings_set_updated_at on public.user_settings;
create trigger user_settings_set_updated_at
before update on public.user_settings
for each row execute function public.set_updated_at();

drop trigger if exists chat_sessions_set_updated_at on public.chat_sessions;
create trigger chat_sessions_set_updated_at
before update on public.chat_sessions
for each row execute function public.set_updated_at();

alter table public.user_profiles enable row level security;
alter table public.user_settings enable row level security;
alter table public.chat_sessions enable row level security;
alter table public.chat_messages enable row level security;
alter table public.uploaded_documents enable row level security;

drop policy if exists "Users can read own profile" on public.user_profiles;
create policy "Users can read own profile"
on public.user_profiles for select
to authenticated
using (auth.uid() = id);

drop policy if exists "Users can create own profile" on public.user_profiles;
create policy "Users can create own profile"
on public.user_profiles for insert
to authenticated
with check (auth.uid() = id);

drop policy if exists "Users can update own profile" on public.user_profiles;
create policy "Users can update own profile"
on public.user_profiles for update
to authenticated
using (auth.uid() = id)
with check (auth.uid() = id);

drop policy if exists "Users can read own settings" on public.user_settings;
create policy "Users can read own settings"
on public.user_settings for select
to authenticated
using (auth.uid() = user_id);

drop policy if exists "Users can create own settings" on public.user_settings;
create policy "Users can create own settings"
on public.user_settings for insert
to authenticated
with check (auth.uid() = user_id);

drop policy if exists "Users can update own settings" on public.user_settings;
create policy "Users can update own settings"
on public.user_settings for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "Users can read own sessions" on public.chat_sessions;
create policy "Users can read own sessions"
on public.chat_sessions for select
to authenticated
using (auth.uid() = user_id);

drop policy if exists "Users can create own sessions" on public.chat_sessions;
create policy "Users can create own sessions"
on public.chat_sessions for insert
to authenticated
with check (auth.uid() = user_id);

drop policy if exists "Users can update own sessions" on public.chat_sessions;
create policy "Users can update own sessions"
on public.chat_sessions for update
to authenticated
using (auth.uid() = user_id)
with check (auth.uid() = user_id);

drop policy if exists "Users can delete own sessions" on public.chat_sessions;
create policy "Users can delete own sessions"
on public.chat_sessions for delete
to authenticated
using (auth.uid() = user_id);

drop policy if exists "Users can read own messages" on public.chat_messages;
create policy "Users can read own messages"
on public.chat_messages for select
to authenticated
using (
  exists (
    select 1 from public.chat_sessions s
    where s.id = chat_messages.session_id and s.user_id = auth.uid()
  )
);

drop policy if exists "Users can create own messages" on public.chat_messages;
create policy "Users can create own messages"
on public.chat_messages for insert
to authenticated
with check (
  exists (
    select 1 from public.chat_sessions s
    where s.id = chat_messages.session_id and s.user_id = auth.uid()
  )
);

drop policy if exists "Users can delete own messages" on public.chat_messages;
create policy "Users can delete own messages"
on public.chat_messages for delete
to authenticated
using (
  exists (
    select 1 from public.chat_sessions s
    where s.id = chat_messages.session_id and s.user_id = auth.uid()
  )
);

drop policy if exists "Users can read own documents" on public.uploaded_documents;
create policy "Users can read own documents"
on public.uploaded_documents for select
to authenticated
using (auth.uid() = user_id);

drop policy if exists "Users can create own documents" on public.uploaded_documents;
create policy "Users can create own documents"
on public.uploaded_documents for insert
to authenticated
with check (auth.uid() = user_id);

insert into storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
values (
  'legal-documents',
  'legal-documents',
  false,
  10485760,
  array[
    'application/pdf',
    'application/msword',
    'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    'text/plain',
    'image/png',
    'image/jpeg'
  ]
)
on conflict (id) do update
set
  public = excluded.public,
  file_size_limit = excluded.file_size_limit,
  allowed_mime_types = excluded.allowed_mime_types;

drop policy if exists "Users can read own stored documents" on storage.objects;
create policy "Users can read own stored documents"
on storage.objects for select
to authenticated
using (
  bucket_id = 'legal-documents'
  and (storage.foldername(name))[1] = auth.uid()::text
);

drop policy if exists "Users can upload own stored documents" on storage.objects;
create policy "Users can upload own stored documents"
on storage.objects for insert
to authenticated
with check (
  bucket_id = 'legal-documents'
  and (storage.foldername(name))[1] = auth.uid()::text
);
