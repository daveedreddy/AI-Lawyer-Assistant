# AI Lawyer Assistant — Task List

## Phase 1: Backend Critical Fixes
- [x] Fix main.py duplicate router + CORS
- [ ] Update core/config.py (add Supabase vars)
- [ ] NEW: core/auth.py (JWT middleware)
- [ ] NEW: app/database/supabase_client.py
- [ ] Update models/response_models.py
- [ ] Update models/history_models.py
- [ ] NEW: prompts/legal_prompt.py (structured legal prompt)
- [ ] Update services/nvidia_service.py (remove hardcoded fallbacks, use new prompt)
- [ ] Update services/history_service.py (Supabase-backed)
- [ ] Update services/document_parser.py (better image handling)
- [ ] NEW: services/storage_service.py
- [ ] Update api/history.py (add missing endpoints)
- [ ] Update api/chat.py (session_id, message persistence)
- [ ] NEW: api/profile.py

## Phase 2: Frontend Integration
- [ ] Install @supabase/supabase-js
- [ ] NEW: src/lib/supabase.ts
- [ ] Update services/auth.service.ts (Supabase)
- [ ] Update services/chat.service.ts (auth + session_id)
- [ ] Update services/history.service.ts (add missing methods)
- [ ] Update services/profile.service.ts (real API)
- [ ] Update services/upload.service.ts (auth header)
- [ ] Update context/AuthContext.tsx (Supabase session)
- [ ] Update pages/ChatScreen.tsx (fix broken syntax + async)
- [ ] Update pages/ChatHistory.tsx (fix async calls)
- [ ] Update pages/Profile.tsx (remove mocks)
- [ ] Update pages/Settings.tsx (persist to DB)
- [ ] Update pages/Login.tsx (remove demo hints, real forgot pw)
- [ ] Update pages/SignUp.tsx (add password field)
- [ ] Update pages/HomeDashboard.tsx (fix async calls)

## Phase 3: Config + Docker
- [ ] Root .env update
- [ ] frontend/.env
- [ ] Dockerfile.backend
- [ ] Dockerfile.frontend
- [ ] docker-compose.yml

## Phase 4: Verification + Supabase Checklist
- [ ] TypeScript compile check
- [ ] Backend startup check
- [ ] Generate Supabase SQL migrations
- [ ] Generate RLS policies
- [ ] Generate final checklist for user
